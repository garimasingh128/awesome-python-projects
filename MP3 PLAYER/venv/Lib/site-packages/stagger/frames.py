#
# frames.py
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

"""Class definitions for ID3v2 frames."""

import abc
import collections
import imghdr
from abc import abstractmethod
from warnings import warn

from stagger.errors import *
from stagger.specs import *

class Frame(metaclass=abc.ABCMeta):
    _framespec = tuple()
    _version = tuple()
    _allow_duplicates = False
    
    def __init__(self, frameid=None, flags=None, frameno=None, **kwargs):
        self.frameid = frameid if frameid else type(self).__name__
        self.flags = flags if flags else set()
        self.frameno = frameno
        assert len(self._framespec) > 0
        for spec in self._framespec:
            val = kwargs.get(spec.name, None)
            setattr(self, spec.name, val)

    def __setattr__(self, name, value):
        # Automatic validation on assignment
        for spec in self._framespec:
            if name == spec.name:
                value = spec.validate(self, value)
                break
        super().__setattr__(name, value)

    def __eq__(self, other):
        return (isinstance(other, type(self))
                and self.frameid == other.frameid
                and self.flags == other.flags
                and self._framespec == other._framespec
                and all(getattr(self, spec.name, None) == 
                        getattr(other, spec.name, None)
                        for spec in self._framespec))

    @classmethod
    def _decode(cls, frameid, data, flags=None, frameno=None):
        frame = cls(frameid=frameid, flags=flags, frameno=frameno)
        if getattr(frame, "_untested", False):
            warn("{0}: Untested frame; please verify results".format(frameid),
                 UntestedFrameWarning)
        for spec in frame._framespec:
            try:
                val, data = spec.read(frame, data)
                setattr(frame, spec.name, val)
            except EOFError:
                if not spec._optional:
                    raise
        return frame

    @classmethod
    def _from_frame(cls, frame):
        "Copy constructor"
        assert frame._framespec == cls._framespec
        new = cls(flags=frame.flags, frameno=frame.frameno)
        for spec in cls._framespec:
            setattr(new, spec.name, getattr(frame, spec.name, None))
        return new

    @classmethod
    def _merge(cls, frames):
        if cls._allow_duplicates:
            return frames
        else:
            if len(frames) > 1:
                # TODO: Research what iTunes does in this case
                # Mutagen displays the first frame only.
                warn("{0}: Duplicate frame; only the first instance is kept"
                     .format(frames[0].frameid),
                     DuplicateFrameWarning)
            return frames[0]

    @classmethod
    def _in_version(self, *versions):
        "Returns true if this frame is in any of the specified versions of ID3."
        for version in versions:
            if (self._version == version
                or (isinstance(self._version, collections.Container) 
                    and version in self._version)):
                return True
        return False

    def _to_version(self, version):
        if self._in_version(version):
            return self
        if version == 2 and hasattr(self, "_v2_frame"):
            return self._v2_frame._from_frame(self)
        if self._in_version(2):
            base = type(self).__bases__[0]
            if issubclass(base, Frame) and base._in_version(version): 
                return base._from_frame(self)
        raise IncompatibleFrameError("Frame {0} cannot be converted "
                                     "to ID3v2.{1} format".format(self.frameid, version))

    def _encode(self, encodings=("latin-1", "utf-16")):
        # if getattr(self, "_bozo", False):
        #     warn("{0}: Frame type is not widely implemented, "
        #          "its use is discouraged".format(self.frameid), 
        #          BozoFrameWarning)
        
        def encode_fields():
            data = bytearray()
            for spec in self._framespec:
                if spec._optional and getattr(self, spec.name) is None:
                    break
                data.extend(spec.write(self, getattr(self, spec.name)))
            return data

        def try_preferred_encodings():
            orig_encoding = self.encoding
            try:
                for encoding in encodings:
                    try:
                        self.encoding = encoding
                        return encode_fields()
                    except UnicodeEncodeError:
                        pass
            finally:
                self.encoding = orig_encoding
            raise ValueError("Could not encode strings")

        if not isinstance(self._framespec[0], EncodingSpec):
            return encode_fields()
        elif self.encoding is None:
            return try_preferred_encodings()
        else:
            try:
                # Try specified encoding before others
               return encode_fields()
            except UnicodeEncodeError:
                return try_preferred_encodings()

    def __repr__(self):
        stype = type(self).__name__
        args = []
        if stype != self.frameid:
            args.append("frameid={0!r}".format(self.frameid))
        if self.flags:
            args.append("flags={0!r}".format(self.flags))
        for spec in self._framespec:
            if isinstance(spec, BinaryDataSpec):
                data = getattr(self, spec.name)
                if isinstance(data, (bytes, bytearray)):
                    args.append("{0}=<{1} bytes of binary data {2!r}{3}>".format(
                            spec.name, len(data), 
                            data[:20], "..." if len(data) > 20 else ""))
                else:
                    args.append(repr(data))
            else:
                args.append("{0}={1!r}".format(spec.name, getattr(self, spec.name)))
        return "{0}({1})".format(stype, ", ".join(args))

    def _spec(self, name):
        "Return the named spec."
        for s in self._framespec:
            if s.name == name:
                return s
        raise ValueError("Unknown spec: " + name)

    def _str_fields(self):
        fields = []
        # Determine how many fields to show
        cutoff = max(i for i in range(len(self._framespec)) 
                     if i == 0 # don't call max with an the empty sequence
                     or not self._framespec[i]._optional 
                     or getattr(self, self._framespec[i].name, None) is not None)
        for spec in self._framespec[:cutoff + 1]:
            fields.append("{0}={1}"
                          .format(spec.name, 
                                  repr(spec.to_str(getattr(self, spec.name, None)))))
        return ", ".join(fields)
        
    def __str__(self):
        flag = " "
        if "unknown" in self.flags: flag = "?"
        if isinstance(self, ErrorFrame): flag = "!"
        return "{0}{1}({2})".format(flag, self.frameid, self._str_fields())

class UnknownFrame(Frame):
    _framespec = (BinaryDataSpec("data"),)

class ErrorFrame(Frame):
    _framespec = (BinaryDataSpec("data"),)

    def __init__(self, frameid, data, exception, frameno=None, **kwargs):
        super().__init__(frameid=frameid, flags={}, frameno=frameno, **kwargs)
        self.data = data
        self.exception = exception

    def _str_fields(self):
        strs = ["ERROR"]
        if self.exception:
            strs.append(str(self.exception))
        strs.append(repr(self.data))
        return ", ".join(strs)
    
    
class TextFrame(Frame):
    _framespec = (EncodingSpec("encoding"),
                  SequenceSpec("text", EncodedStringSpec("text")))

    def __init__(self, *values, frameid=None, flags=None, frameno=None, **kwargs):
        def extract_strs(values):
            if values is None:
                return
            if isinstance(values, str):
                yield values
            elif isinstance(values, collections.Iterable):
                for val in values:
                    for v in extract_strs(val):
                        yield v
            else:
                raise ValueError("Invalid text frame value")
        super().__init__(frameid=frameid, flags=flags, frameno=frameno, **kwargs)
        self.text.extend(list(extract_strs(values)))

    @classmethod
    def _decode(cls, frameid, data, flags=None, frameno=None):
        frame = super()._decode(frameid, data, flags=flags, frameno=frameno)
        count = 0
        while len(frame.text) > 0 and frame.text[-1] == "":
            frame.text = frame.text[0:-1]
            count += 1
        if count > 0:
            warn("{0}: Stripped {1} empty strings from end of frame"
                 .format(frameid, count), FrameWarning)
        if len(frame.text) == 0 or sum(len(t) for t in frame.text) == 0:
            warn("{0}: Ignoring empty text frame".format(frameid), 
                 EmptyFrameWarning)
            return None
        return frame

    def _str_fields(self):
        return ", ".join(repr(t) for t in self.text)
#        return "{0} {1}".format((EncodedStringSpec._encodings[self.encoding][0] 
#                                if self.encoding is not None else "<undef>"),
#                                ", ".join(repr(t) for t in self.text))

    @classmethod
    def _merge(cls, frames):
        if len(frames) == 1:
            return frames
        res = cls(text=[])
        enc = None
        for f in frames:
            if enc is None:
                enc = f.encoding
            elif enc != f.encoding:
                enc = False
            try:
                res.text.extend(f.text)
            except KeyError:  # f may be an ErrorFrame here.
                pass
        if enc is not False:
            res.encoding = enc
        return [res]

class URLFrame(Frame):
    _framespec = (URLStringSpec("url"), )
    def _str_fields(self):
        return repr(self.url)

class CreditsFrame(Frame):
    _framespec = (EncodingSpec("encoding"),
                  MultiSpec("people",
                            EncodedStringSpec("involvement"),
                            EncodedStringSpec("person")))

class PictureFrame(Frame):
    def __init__(self, value=None, frameid=None, flags=None, frameno=None, **kwargs):
        super().__init__(frameid=frameid, flags=flags, frameno=frameno, **kwargs)
        if value is not None:
            with open(value, "rb") as file:
                self.data = file.read()
                self.type = 0
                self.desc = ""
                format = imghdr.what(None, self.data[:32])
                if not format:
                    format = value.rpartition(".")[2]
                self._set_format(format)
    
    @abstractmethod
    def _set_format(self, format):
        pass

def is_frame_class(cls):
    return (isinstance(cls, type)
            and issubclass(cls, Frame)
            and 3 <= len(cls.__name__) <= 4
            and cls.__name__ == cls.__name__.upper())
