#
# specs.py
# From the stagger project: http://code.google.com/p/stagger/
#
# Copyright (c) 2009-2011 Karoly Lorentey  <karoly@lorentey.hu>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import abc
import collections

from abc import abstractmethod
from warnings import warn

from stagger.conversion import *
from stagger.errors import *

# The idea for the Spec system comes from Mutagen.

def optionalspec(spec):
    spec._optional = True
    return spec

class Spec(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.name = name

    _optional = False
        
    @abstractmethod
    def read(self, frame, data): pass

    @abstractmethod
    def write(self, frame, value): pass

    def validate(self, frame, value):
        self.write(frame, value)
        return value

    def to_str(self, value):
        return str(value)

class ByteSpec(Spec):
    def read(self, frame, data):
        if len(data) < 1:
            raise EOFError()
        return data[0], data[1:]
    def write(self, frame, value):
        return bytes([value])
    def validate(self, frame, value):
        if value is None:
            return value
        if not isinstance(value, int):
            raise TypeError("Not a byte")
        if  value not in range(256):
            raise ValueError("Invalid byte value")
        return value

class IntegerSpec(Spec):
    """An 8-bit, big-endian unsigned integer of specified width.
    Width is the number of bits in the representation.  
    If width is a sting, it must name a frame attribute to get the
    width from.
    The width is automatically rounded up to the nearest multiple of 8.
    """
    def __init__(self, name, width):
        super().__init__(name)
        self.width = width

    def _width(self, frame):
        if isinstance(self.width, str):
            return (getattr(frame, self.width) + 7) // 8
        else:
            return (self.width + 7) // 8

    def read(self, frame, data):
        w = self._width(frame)
        if len(data) < w:
            raise EOFError()
        return Int8.decode(data[:w]), data[w:]

    def write(self, frame, value):
        return Int8.encode(value, width=self._width(frame))

    def validate(self, frame, value):
        if value is None:
            return value
        if type(value) is not int: 
            raise TypeError("Not an integer: {0}".format(repr(value)))
        w = self._width(frame)
        if value < 0:
            raise ValueError("Value is negative")
        if value >= 1 << (w << 3):
            raise ValueError("Value is too large")
        return value

class SignedIntegerSpec(IntegerSpec):
    """An 8-bit, big-endian two's-complement signed integer of specified width.
    Width is the number of bits in the representation.
    If width is a sting, it must name a frame attribute to get the
    width from.
    The width is automatically rounded up to the nearest multiple of 8.
    """
    def __init__(self, name, width):
        super().__init__(name, width=width)

    def read(self, frame, data):
        w = self._width(frame)
        (value, data) = super().read(frame, data)
        if value & (1 << ((w << 3) - 1)): # Negative value
            value -= (1 << (w << 3))
        return value, data

    def write(self, frame, value):
        w = self._width(frame)
        if value < 0:
            value += (1 << (w << 3))
        return super().write(frame, value)

    def validate(self, frame, value):
        if value is None:
            return value
        if type(value) is not int: 
            raise TypeError("Not an integer")
        w = self._width(frame)
        if value >= (1 << ((w << 3) - 1)):
            raise ValueError("Value is too large")
        if value < -(1 << ((w << 3) - 1)):
            raise ValueError("Value is too small")
        return value

class RVADIntegerSpec(IntegerSpec):
    """An 8-bit, big-endian signed integer in RVAD format.
    The value is stored in sign + magnitude format,
    with the sign bit encoded in bit <signbit> of the 
    frame's <signs> attribute.  A zero sign bit indicates
    the value is negative.
    """
    def __init__(self, name, width, signbit, signs="signs"):
        super().__init__(name, width)
        self.signbit = signbit
        self.signs = signs

    def read(self, frame, data):
        (value, data) = super().read(frame, data)
        if not (getattr(frame, self.signs) & (1 << self.signbit)):
            value *= -1
        return (value, data)

    def write(self, frame, value):
        return super().write(frame, abs(value))

    def validate(self, frame, value):
        if value is None:
            return value
        if type(value) is not int: 
            raise TypeError("Not an integer: {0}".format(repr(value)))

        # Update sign bit in frame.signs.
        signs = getattr(frame, self.signs)
        if value < 0:
            signs &= ~(1 << self.signbit)
        else:
            signs |= 1 << self.signbit
        setattr(frame, self.signs, signs)

        w = self._width(frame)
        if abs(value) >= 1 << (w << 3):
            raise ValueError("Value is too large")
        return value
        

class VarIntSpec(Spec):
    def read(self, frame, data):
        if len(data) == 0:
            raise EOFError()
        bits = data[0]
        data = data[1:]
        bytes = (bits + 7) >> 3
        if len(data) < bytes:
            raise EOFError()
        return Int8.decode(data[:bytes]), data[bytes:]
    def write(self, frame, value):
        bytes = 4
        t = value >> 32
        while t > 0:
            t >>= 32
            bytes += 4
        return Int8.encode(bytes * 8, width=1) + Int8.encode(value, width=bytes)
    def validate(self, frame, value):
        if value is None:
            return value
        if type(value) is not int:
            raise TypeError("Not an integer")
        if value < 0:
            raise ValueError("Value is negative")
        return value

class BinaryDataSpec(Spec):
    def read(self, frame, data):
        return data, bytes()
    def write(self, frame, value):
        return bytes(value)
    def validate(self, frame, value):
        if value is None:
            return bytes()
        if not isinstance(value, collections.ByteString):
            raise TypeError("Not a byte sequence")
        return value
    def to_str(self, value):
        return '{0}{1}'.format(value[0:16], "..." if len(value) > 16 else "")

class SimpleStringSpec(Spec):
    def __init__(self, name, length):
        super().__init__(name)
        self.length = length
    def read(self, frame, data):
        return data[:self.length].decode('latin-1'), data[self.length:]
    def write(self, frame, value):
        if value is None:
            return b" " * self.length
        data = value.encode('latin-1')
        if len(data) != self.length:
            raise ValueError("String length mismatch")
        return data
    def validate(self, frame, value):
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("Not a string")
        if len(value) != self.length: 
            raise ValueError("String length mismatch")
        value.encode('latin-1')
        return value

class LanguageSpec(SimpleStringSpec):
    def __init__(self, name):
        super().__init__(name, 3)
    
class NullTerminatedStringSpec(Spec):
    def read(self, frame, data):
        rawstr, sep, data = data.partition(b"\x00")
        return rawstr.decode('latin-1'), data
    def write(self, frame, value):
        return value.encode('latin-1') + b"\x00"
    def validate(self, frame, value):
        if value is None:
            return ""
        if not isinstance(value, str):
            raise TypeError("Not a string")
        value.encode('latin-1')
        return value

class URLStringSpec(NullTerminatedStringSpec):
    def read(self, frame, data):
        rawstr, sep, data = data.partition(b"\x00")
        if len(rawstr) == 0 and len(data) > 0:
            # iTunes prepends an extra null byte to WFED frames (encoding spec?)
            #warn("Frame {0} includes a text encoding byte".format(frame.frameid), Warning)
            rawstr, sep, data = data.partition(b"\x00")
        return rawstr.decode('latin-1'), data

class EncodingSpec(ByteSpec):
    "EncodingSpec must be the first spec."
    def read(self, frame, data):
        enc, data = super().read(frame, data)
        if enc & 0xFC:
            raise FrameError("Invalid encoding")
        return enc, data
    def write(self, frame, value):
        return super().write(frame, value)
    def validate(self, frame, value):
        if value is None:
            return value
        def norm(s):
            return s.lower().replace("-", "")
        if isinstance(value, str):
            for i in range(len(EncodedStringSpec._encodings)):
                if norm(EncodedStringSpec._encodings[i][0]) == norm(value):
                    value = i
                    break
            else:
                raise ValueError("Unknown encoding: " + repr(value))
        if not isinstance(value, int):
            raise TypeError("Not an encoding")
        if 0 <= value <= 3:
            return value
        raise ValueError("Invalid encoding 0x{0:X}".format(value))

    def to_str(self, value):
        if value is None:
            return ""
        else:
            return EncodedStringSpec._encodings[value][0]

class EncodedStringSpec(Spec):
    _encodings = (('latin-1', b"\x00"),
                  ('utf-16', b"\x00\x00"),
                  ('utf-16-be', b"\x00\x00"),
                  ('utf-8', b"\x00"))

    def read(self, frame, data):
        enc, term = self._encodings[frame.encoding]
        if len(term) == 1:
            rawstr, sep, data = data.partition(term)
        else:
            index = len(data)
            for i in range(0, len(data), 2):
                if data[i:i+2] == term:
                    index = i
                    break
            #if index == len(data):
            #    warn("Unterminated string in frame '{0}'".format(frame.frameid), Warning)
            if index & 1:
                raise EOFError()
            rawstr = data[:index]
            data = data[index+2:]
        return rawstr.decode(enc), data

    def write(self, frame, value):
        assert frame.encoding is not None
        enc, term = self._encodings[frame.encoding]
        return value.encode(enc) + term

    def validate(self, frame, value):
        if value is None:
            return ""
        if not isinstance(value, str):
            raise TypeError("Not a string")
        if frame.encoding is not None:
            self.write(frame, value)
        return value

class EncodedFullTextSpec(EncodedStringSpec):
    pass # TODO

class SequenceSpec(Spec):
    """Recognizes a sequence of values, all of the same spec."""
    def __init__(self, name, spec):
        super().__init__(name)
        self.spec = spec

    def read(self, frame, data):
        "Returns a list of values, eats all of data."
        seq = []
        while data:
            elem, data = self.spec.read(frame, data)
            seq.append(elem)
        return seq, data

    def write(self, frame, values):
        if isinstance(values, str):
            return self.spec.write(frame, values)
        data = bytearray()
        for v in values:
            data.extend(self.spec.write(frame, v))
        return data

    def validate(self, frame, values):
        if values is None:
            return []
        if isinstance(values, str):
            values = [values]
        return [self.spec.validate(frame, v) for v in values]

class MultiSpec(Spec):
    def __init__(self, name, *specs):
        super().__init__(name)
        self.specs = specs

    def read(self, frame, data):
        seq = []
        while data:
            record = []
            origdata = data
            try:
                for s in self.specs:
                    elem, data = s.read(frame, data)
                    record.append(elem)
                seq.append(tuple(record))
            except (EOFError, ValueError):
                if len(seq) == 0:
                    raise
                warn("Frame {0} has {1} bytes of junk at end".format(frame.frameid, len(origdata)), 
                     FrameWarning)
                frame.junkdata = origdata
                data = b''
        return seq, data

    def write(self, frame, values):
        data = bytearray()
        for v in values:
            for i in range(len(self.specs)):
                data.extend(self.specs[i].write(frame, v[i]))
        return bytes(data)

    def validate(self, frame, values):
        if values is None:
            return []
        res = []
        for v in values:
            if not isinstance(v, collections.Sequence) or isinstance(v, str):
                raise TypeError("Records must be sequences")
            if len(v) != len(self.specs):
                raise ValueError("Invalid record length")
            res.append(tuple(self.specs[i].validate(frame, v[i])
                             for i in range(len(self.specs))))
        return res

class ASPISpec(Spec):
    "A list of frame.N integers whose width depends on frame.b."
    def read(self, frame, data):
        width = 1 if frame.b == 1 else 2
        value = []
        if len(data) < width * frame.N:
            raise EOFError
        for i in range(frame.N):
            value.append(Int8.decode(data[:width]))
            data = data[width:]
        return value, data

    def write(self, frame, values):
        width = 1 if frame.b == 1 else 2
        data = bytearray()
        for v in values:
            data.extend(Int8.encode(v, width=width))
        return data
    
    def validate(self, frame, values):
        if values is None:
            return []
        if not isinstance(values, collections.Sequence) or isinstance(values, str):
            raise TypeError("ASPISpec needs a sequence of integers")
        if len(values) != frame.N:
            raise ValueError("ASPISpec needs {0} integers".format(frame.N))
        self.write(frame, values)
        res = []
        for v in values:
            res.append(v)
        return res

class PictureTypeSpec(ByteSpec):
    picture_types = (
        "Other", "32x32 icon", "Other icon", "Front Cover", "Back Cover",
        "Leaflet", "Media", "Lead artist", "Artist", "Conductor",
        "Band/Orchestra", "Composer", "Lyricist/text writer",
        "Recording Location", "Recording", "Performance", "Screen capture",
        "A bright coloured fish", "Illustration", "Band/artist",
        "Publisher/Studio")

    def validate(self, frame, value):
        if value is None:
            return value
        if isinstance(value, str):
            def matches(value, name):
                return value.lower() == name.lower()
            for i in range(len(self.picture_types)):
                if matches(value, self.picture_types[i]):
                    value = i
                    break
            else:
                raise ValueError("Unknown picture type: " + repr(value))
        if not isinstance(value, int):
            raise TypeError("Not a picture type")
        if 0 <= value < len(self.picture_types):
            return value
        raise ValueError("Unknown picture type 0x{0:X}".format(value))

    def to_str(self, value):
        return "{1}({0})".format(value, self.picture_types[value])

