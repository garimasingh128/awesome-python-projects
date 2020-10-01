#
# tags.py
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
import struct
import re
import collections
import io
import imghdr
import zlib

from abc import abstractmethod, abstractproperty
from warnings import warn
from contextlib import contextmanager

from stagger.errors import *
from stagger.conversion import *

import stagger.frames as Frames
import stagger.fileutil as fileutil

_FRAME23_FORMAT_COMPRESSED = 0x0080
_FRAME23_FORMAT_ENCRYPTED = 0x0040
_FRAME23_FORMAT_GROUP = 0x0020
_FRAME23_FORMAT_UNKNOWN_MASK = 0x001F

_FRAME23_STATUS_DISCARD_ON_TAG_ALTER = 0x8000
_FRAME23_STATUS_DISCARD_ON_FILE_ALTER = 0x4000
_FRAME23_STATUS_READ_ONLY = 0x2000
_FRAME23_STATUS_UNKNOWN_MASK = 0x1F00

_TAG24_UNSYNCHRONISED = 0x80
_TAG24_EXTENDED_HEADER = 0x40
_TAG24_EXPERIMENTAL = 0x20
_TAG24_FOOTER = 0x10
_TAG24_UNKNOWN_MASK = 0x0F

_FRAME24_FORMAT_GROUP = 0x0040
_FRAME24_FORMAT_COMPRESSED = 0x0008
_FRAME24_FORMAT_ENCRYPTED = 0x0004
_FRAME24_FORMAT_UNSYNCHRONISED = 0x0002
_FRAME24_FORMAT_DATA_LENGTH_INDICATOR = 0x0001
_FRAME24_FORMAT_UNKNOWN_MASK = 0x00B0

_FRAME24_STATUS_DISCARD_ON_TAG_ALTER = 0x4000
_FRAME24_STATUS_DISCARD_ON_FILE_ALTER = 0x2000
_FRAME24_STATUS_READ_ONLY = 0x1000
_FRAME24_STATUS_UNKNOWN_MASK = 0x8F00

def read_tag(filename):
    with fileutil.opened(filename, "rb") as file:
        (cls, offset, length) = detect_tag(file)
        return cls.read(file, offset)

def decode_tag(data):
    return read_tag(io.BytesIO(data))

def delete_tag(filename):
    with fileutil.opened(filename, "rb+") as file:
        try:
            (cls, offset, length) = detect_tag(file)
            fileutil.replace_chunk(file, offset, length, bytes())
        except NoTagError:
            pass

def detect_tag(filename):
    """Return type and position of ID3v2 tag in filename.
    Returns (tag_class, offset, length), where tag_class
    is either Tag22, Tag23, or Tag24, and (offset, length)
    is the position of the tag in the file.
    """
    with fileutil.opened(filename, "rb") as file:
        file.seek(0)
        header = file.read(10)
        file.seek(0)
        if len(header) < 10:
            raise NoTagError("File too short")
        if header[0:3] != b"ID3":
            raise NoTagError("ID3v2 tag not found")
        if header[3] not in _tag_versions or header[4] != 0:
            raise TagError("Unknown ID3 version: 2.{0}.{1}"
                           .format(*header[3:5]))
        cls = _tag_versions[header[3]]
        offset = 0
        length = Syncsafe.decode(header[6:10]) + 10
        if header[3] == 4 and header[5] & _TAG24_FOOTER:
            length += 10
        return (cls, offset, length)

def frameclass(cls):
    """Register cls as a class representing an ID3 frame.

    Sets cls.frameid and cls._version if not present, and registers the
    new frame in Tag's known_frames dictionary.

    To be used as a decorator on the class definition:

    @frameclass
    class UFID(Frame):
        _framespec = (NullTerminatedStringSpec("owner"), BinaryDataSpec("data"))
    """
    assert issubclass(cls, Frames.Frame)

    # Register v2.2 versions of v2.3/v2.4 frames if encoded by inheritance.
    if len(cls.__name__) == 3:
        base = cls.__bases__[0]
        if issubclass(base, Frames.Frame) and base._in_version(3, 4):
            assert not hasattr(base, "_v2_frame")
            base._v2_frame = cls
            # Override frameid from base with v2.2 name
            if base.frameid == cls.frameid:
                cls.frameid = cls.__name__

    # Add frameid.
    if not hasattr(cls, "frameid"):
        cls.frameid = cls.__name__
    assert Tag._is_frame_id(cls.frameid)

    # Supply _version attribute if missing.
    if len(cls.frameid) == 3:
        cls._version = 2
    if len(cls.frameid) == 4 and not cls._version:
        cls._version = (3, 4)

    # Register cls as a known frame.
    assert cls.frameid not in Tag.known_frames
    Tag.known_frames[cls.frameid] = cls
    
    return cls

class FrameOrder:
    """Order frames based on their position in a predefined list of patterns, 
    and their original position in the source tag.

    A pattern may be a frame class, or a regular expression that is to be
    matched against the frame id.

    >>> order = FrameOrder(TIT1, "T.*", TXXX)
    >>> order.key(TIT1())
    (0, 1)
    >>> order.key(TPE1())
    (1, 1)
    >>> order.key(TXXX())
    (2, 1)
    >>> order.key(APIC())
    (3, 1)
    >>> order.key(APIC(frameno=3))
    (3, 0, 3)
    """
    def __init__(self, *patterns):
        self.re_keys = []
        self.frame_keys = dict()
        i = -1
        for (i, pattern) in zip(range(len(patterns)), patterns):
            if isinstance(pattern, str):
                self.re_keys.append((pattern, i))
            else:
                assert issubclass(pattern, Frames.Frame)
                self.frame_keys[pattern] = i
        self.unknown_key = i + 1

    def key(self, frame):
        "Return the sort key for the given frame."
        def keytuple(primary):
            if frame.frameno is None:
                return (primary, 1)
            return (primary, 0, frame.frameno)

        # Look up frame by exact match
        if type(frame) in self.frame_keys:
            return keytuple(self.frame_keys[type(frame)])

        # Look up parent frame for v2.2 frames
        if frame._in_version(2) and type(frame).__bases__[0] in self.frame_keys:
            return keytuple(self.frame_keys[type(frame).__bases__[0]])

        # Try each pattern
        for (pattern, key) in self.re_keys:
            if re.match(pattern, frame.frameid):
                return keytuple(key)

        return keytuple(self.unknown_key)

    def __repr__(self):
        order = []
        order.extend((repr(pair[0]), pair[1]) for pair in self.re_keys)
        order.extend((cls.__name__, self.frame_keys[cls]) 
                     for cls in self.frame_keys)
        order.sort(key=lambda pair: pair[1])
        return "<FrameOrder: {0}>".format(", ".join(pair[0] for pair in order))
        

class Tag(collections.MutableMapping, metaclass=abc.ABCMeta):
    known_frames = { }        # Maps known frameids to Frame class objects

    frame_order = None        # Initialized by stagger.id3

    def __init__(self):
        self.flags = set()
        self._frames = dict()
        self._filename = None

    # Primary accessor (no magic)
    def frames(self, key=None, orig_order=False):
        """Returns a list of frames in this tag.
        If KEY is None, returns all frames in the tag; otherwise returns all frames
        whose frameid matches KEY.
        
        If ORIG_ORDER is True, then the frames are returned in their original order.
        Otherwise the frames are sorted in canonical order according to the frame_order
        field of this tag.
        """
        if key is not None:
            # If there are multiple frames, then they are already in original order.
            key = self._normalize_key(key)
            if len(self._frames[key]) == 0:
                raise KeyError("Key not found: " + repr(key))
            return self._frames[key]
        
        frames = []
        for frameid in self._frames.keys():
            for frame in self._frames[frameid]:
                frames.append(frame)
        if orig_order:
            key = (lambda frame: 
                   (0, frame.frameno) 
                   if frame.frameno is not None 
                   else (1,))
        else:
            key = self.frame_order.key
        frames.sort(key=key)
        return frames

    # MutableMapping API
    def __iter__(self):
        for frameid in self._frames:
            yield frameid

    def __len__(self):
        return sum(len(self._frames[l]) for l in self._frames)

    def __eq__(self, other):
        return (self.version == other.version
                and self.flags == other.flags 
                and self._frames == other._frames)

    def _normalize_key(self, key, unknown_ok=True):
        """Return the normalized version of KEY.
        KEY may be a frameid (a string), or a Frame class object.
        If KEY corresponds to a registered frameid, then that frameid is returned.
        Otherwise, either KeyError is raised, or KEY is returned verbatim, 
        depending on the value of UNKNOWN_OK.
        """
        if Frames.is_frame_class(key):
            key = key.frameid
        if isinstance(key, str):
            if not self._is_frame_id(key):
                raise KeyError("{0}: Invalid frame id".format(key))
            if key not in self.known_frames:
                if unknown_ok:
                    warn("{0}: Unknown frame id".format(key), UnknownFrameWarning)
                else:
                    raise KeyError("{0}: Unknown frame id".format(key))
        return key

    # Mapping accessor (with extra magic, for convenience)
    def __getitem__(self, key):
        key = self._normalize_key(key)
        fs = self.frames(key)
        allow_duplicates = (key not in self.known_frames 
                            or self.known_frames[key]._allow_duplicates)
        if allow_duplicates:
            return fs
        if len(fs) > 1:
            # Merge duplicates into one ephemeral frame, and return that.
            # This may break users' expectations when they try to make changes
            # to the attributes of the returned frame; however, I think 
            # sometimes returning a list, sometimes a single frame for the same
            # frame id would be even worse.
            fs = fs[0]._merge(fs)
        assert len(fs) == 1
        return fs[0]

    def __setitem__(self, key, value):
        key = self._normalize_key(key, unknown_ok=False)
        if isinstance(value, self.known_frames[key]):
            self._frames[key] = [value]
            return
        if self.known_frames[key]._allow_duplicates:
            if not isinstance(value, collections.Iterable) or isinstance(value, str):
                raise ValueError("{0} requires a list of frame values".format(key))
            self._frames[key] = [val if isinstance(val, self.known_frames[key])
                                 else self.known_frames[key](val) 
                                 for val in value]
        else: # not _allow_duplicates
            self._frames[key] = [self.known_frames[key](value)]

    def __delitem__(self, key):
        del self._frames[self._normalize_key(key)]
    
    def values(self):
        for frameid in self._frames.keys():
            for frame in self._frames[frameid]:
                yield frame

    # Friendly names API
    _friendly_names = [ "title", "artist", 
                        "date", 
                        "album-artist", "album", 
                        "track", "track-total",
                        "disc", "disc-total",
                        "grouping", "composer", 
                        "genre", 
                        "comment", 
                        #"compilation",
                        "picture",
                        "sort-title", "sort-artist",
                        "sort-album-artist", "sort-album",
                        "sort-composer",
                        ]

    title = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    artist = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    date = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    album_artist = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    album = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    track = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    track_total = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    disc = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    disc_total = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    composer = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    genre = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    comment = abstractproperty(fget=lambda self: Non, fset=lambda self, value: None)
    grouping = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    picture = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    sort_title = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    sort_artist = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    sort_album_artist = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    sort_album = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)
    sort_composer = abstractproperty(fget=lambda self: None, fset=lambda self, value: None)

    def __friendly_text_collect(self, frameid):
        """Collect text values from all instances of FRAMEID into a single list.
        Returns an empty list if there are no instances of FRAMEID with a text attribute.
        """
        try:
            return self[frameid].text
        except (KeyError, AttributeError):
            return []
        
    @classmethod
    def _friendly_text_frame(cls, frameid):
        def getter(self):
            return " / ".join(self.__friendly_text_collect(frameid))
        def setter(self, value):
            if isinstance(value, str):
                if len(value): 
                    # For non-empty strings, split value
                    self[frameid] = value.split(" / ")
                elif frameid in self:
                    # For empty strings, delete frame
                    del self[frameid]
            else:
                self[frameid] = value
        return (getter, setter)

    @classmethod
    def _friendly_track(cls, frameid, totalattr):
        def getter(self):
            ts = self.__friendly_text_collect(frameid)
            try:
                return int(ts[0].partition("/")[0])
            except (ValueError, IndexError):
                return 0
        def setter(self, value):
            value = int(value)
            total = getattr(self, totalattr)
            if total > 0:
                self[frameid] = "{0}/{1}".format(value, total)
            elif value:
                self[frameid] = str(value)
            elif frameid in self:
                del self[frameid]
        return (getter, setter)

    @classmethod
    def _friendly_track_total(cls, frameid, trackattr):
        def getter(self):
            ts = self.__friendly_text_collect(frameid)
            try:
                return int(ts[0].partition("/")[2])
            except (ValueError, IndexError):
                return 0
        def setter(self, value):
            value = int(value)
            track = getattr(self, trackattr)
            if value:
                self[frameid] = "{0}/{1}".format(track, value)
            elif track:
                self[frameid] = str(track)
            elif frameid in self:
                del self[frameid]
        return (getter, setter)

    __date_pattern = re.compile(r"""(?x)\s*
                  ((?P<year>[0-9]{4})       # YYYY
                  (-(?P<month>[01][0-9])    # -MM
                  (-(?P<day>[0-3][0-9])     # -DD
                  )?)?)?
                  [ T]?
                  ((?P<hour>[0-2][0-9])     #  HH
                  (:(?P<min>[0-6][0-9])     # :MM
                  (:(?P<sec>[0-6][0-9])     # :SS
                  )?)?)?\s*
                  """)

    @classmethod
    def _validate_friendly_date(cls, string):
        m = cls.__date_pattern.match(string)
        if m is None or m.end() != len(string):
            raise ValueError("date must be in 'YYYY-MM-DD HH:MM:SS' format")

    @classmethod
    def _get_friendly_date(cls, string):
        m = cls.__date_pattern.match(string)
        if m is None:
            return (None, None, None, None, None, None)
        res = []
        for field in ("year", "month", "day", "hour", "min", "sec"):
            v = m.group(field)
            res.append(int(v) if v is not None else None)
        return res

    def _get_date(self, yearframe, dateframe, timeframe):
        year = month = day = hour = minute = second = None
        
        # Parse year.
        try:
            year = int(self.__friendly_text_collect(yearframe)[0])
        except (IndexError, ValueError):
            pass
        
        # Parse month and date.
        try:
            date = self.__friendly_text_collect(dateframe)[0]
            m = re.match(r"\s*(?P<month>[01][0-9])\s*-?\s*(?P<day>[0-3][0-9])?\s*$", 
                         date)
            if m is not None:
                month = int(m.group("month"))
                day = int(m.group("day"))
        except IndexError:
            pass

        # Parse time.
        try:
            time = self.__friendly_text_collect(timeframe)[0]
            m = re.match(r"\s*(?P<hour>[0-2][0-9])\s*:?\s*"
                         "(?P<minute>[0-5][0-9])\s*:?\s*"
                         "(?P<second>[0-5][0-9])?\s*$", time)
            if m is not None:
                hour = int(m.group("hour"))
                minute = int(m.group("minute"))
                s = m.group("second")
                second = int(s) if s is not None else None
        except IndexError: 
            pass
        return (year, month, day, hour, minute, second)

    def _friendly_date_string(self, *fields):
        seps = ("", "-", "-", " ", ":", ":")
        formats = ("04", "02", "02", "02", "02", "02")
        res = []
        for i in range(len(fields)):
            if fields[i] is None:
                break
            res.append(seps[i])
            res.append("{0:{1}}".format(fields[i], formats[i]))
        return "".join(res)

    @classmethod
    def _friendly_picture(cls, frameid):
        def getter(self):
            if frameid not in self:
                return ""
            else:
                return ", ".join("{0}:{1}:<{2} bytes of {3} data>"
                                 .format(f._spec("type").to_str(f.type),
                                         f.desc,
                                         len(f.data),
                                         imghdr.what(None, f.data[:32]))
                                 for f in self[frameid])
        def setter(self, value):
            if len(value) > 0:
                self[frameid] = [self.known_frames[frameid](value=value)]
            elif frameid in self:
                del self[frameid]
        return (getter, setter)

    @classmethod
    def _friendly_comment(cls, frameid):
        def comment_frame_index(self):
            if frameid not in self:
                return None
            # Return comment with lang="eng", desc="", if present.
            # Otherwise return the first comment with no description,
            # regardless of language.
            icmt = None
            for i in range(len(self[frameid])):
                f = self[frameid][i]
                if f.desc == "":
                    if f.lang == "eng":
                        return i
                    if icmt is None:
                        icmt = i
            return icmt
        def getter(self):
            i = comment_frame_index(self)
            if i is None:
                return ""
            else:
                return self[frameid][i].text
        def setter(self, value):
            assert isinstance(value, str)
            i = comment_frame_index(self)
            if i is not None:
                del self._frames[frameid][i]
            if len(value) > 0:
                frame = self.known_frames[frameid](lang="eng", desc="", text=value)
                if frameid not in self._frames:
                    self._frames[frameid] = []
                self._frames[frameid].append(frame)
        return (getter, setter)

    # Misc
    def __repr__(self):
        return "<{0}: ID3v2.{1} tag{2} with {3} frames>".format(
            type(self).__name__,
            self.version,
            ("({0})".format(", ".join(self.flags)) 
             if len(self.flags) > 0 else ""),
            len(self._frames))


    # Reading tags
    @classmethod
    def read(cls, filename, offset=0):
        """Read an ID3v2 tag from a file."""
        i = 0
        with fileutil.opened(filename, "rb") as file:
            file.seek(offset)
            tag = cls()
            tag._read_header(file)
            for (frameid, bflags, data) in tag._read_frames(file):
                if len(data) == 0:
                    warn("{0}: Ignoring empty frame".format(frameid), 
                         EmptyFrameWarning)
                else:
                    frame = tag._decode_frame(frameid, bflags, data, i)
                    if frame is not None:
                        l = tag._frames.setdefault(frame.frameid, [])
                        l.append(frame)
                        if file.tell() > tag.offset + tag.size:
                            break
                        i += 1
            try:
                tag._filename = file.name
            except AttributeError:
                pass
            return tag

    @classmethod
    def decode(cls, data):
        return cls.read(io.BytesIO(data))

    def _decode_frame(self, frameid, bflags, data, frameno=None):
        try:
            (flags, data) = self._interpret_frame_flags(frameid, bflags, data)
            if flags is None: 
                flags = set()
            if frameid in self.known_frames:
                return self.known_frames[frameid]._decode(frameid, data, 
                                                          flags, 
                                                          frameno=frameno)
            else:
                # Unknown frame
                flags.add("unknown")
                warn("{0}: Unknown frame".format(frameid), UnknownFrameWarning)
                if frameid.startswith('T'): # Unknown text frame
                    return Frames.TextFrame._decode(frameid, data, flags, 
                                                    frameno=frameno)
                elif frameid.startswith('W'): # Unknown URL frame
                    return Frames.URLFrame._decode(frameid, data, flags, 
                                                   frameno=frameno)
                else:
                    return Frames.UnknownFrame._decode(frameid, data, flags, 
                                                       frameno=frameno)
        except (FrameError, ValueError, EOFError) as e:
            warn("{0}: Invalid frame".format(frameid), ErrorFrameWarning)
            return Frames.ErrorFrame(frameid, data, exception=e, frameno=frameno)

    @abstractmethod
    def _read_header(self, file): pass

    @abstractmethod
    def _read_frames(self, file): pass

    @abstractmethod
    def _interpret_frame_flags(self, frameid, bflags, data): pass


    # Writing tags

    def write(self, filename=None):
        if not filename:
            filename = self._filename
        if not filename:
            raise TypeError("invalid file: {0}".format(filename))
        with fileutil.opened(filename, "rb+") as file:
            try:
                (offset, length) = detect_tag(file)[1:3]
            except NoTagError:
                (offset, length) = (0, 0)
            if offset > 0:
                delete_tag(file)
                (offset, length) = (0, 0)
            tag_data = self.encode(size_hint=length)
            fileutil.replace_chunk(file, offset, length, tag_data)

    @abstractmethod
    def encode(self, size_hint=None):
        pass

    padding_default = 128
    padding_max = 1024

    def _get_size_with_padding(self, size_desired, size_actual):
        size = size_actual 
        if (size_desired is not None and size < size_desired
            and (self.padding_max is None or 
                 size_desired - size_actual <= self.padding_max)):
            size = size_desired
        elif self.padding_default:
            size += min(self.padding_default, self.padding_max)
        return size

    @staticmethod
    def _is_frame_id(data):
        if isinstance(data, str):
            try:
                data = data.encode("ASCII")
            except UnicodeEncodeError:
                return false
        # Allow a single space at end of four-character ids
        # Some programs (e.g. iTunes 8.2) generate such frames when converting
        # from 2.2 to 2.3/2.4 tags.
        pattern = re.compile(b"^[A-Z][A-Z0-9]{2}[A-Z0-9 ]?$")
        return pattern.match(data)

    def _prepare_frames_hook(self):
        pass

    def _prepare_frames(self):
        # Generate dictionary of frames
        d = self._frames

        # Merge duplicate frames
        for frameid in self._frames.keys():
            fs = self._frames[frameid]
            if len(fs) > 1:
                d[frameid] = fs[0]._merge(fs)

        self._prepare_frames_hook()

        # Convert frames
        newframes = []
        for frameid in self._frames.keys():
            for frame in self._frames[frameid]:
                try:
                    newframes.append(frame._to_version(self.version))
                except IncompatibleFrameError:
                    warn("{0}: Ignoring incompatible frame".format(frameid), 
                         FrameWarning)
                except ValueError as e:
                    warn("{0}: Ignoring invalid frame ({1})".format(frameid, e), 
                         FrameWarning)

        # Sort frames
        newframes.sort(key=self.frame_order.key)
        return newframes


        
class Tag22(Tag):
    version = 2
    encodings = ("latin-1", "utf-16")

    def __init__(self):
        super().__init__()

    title = property(*Tag._friendly_text_frame("TT2"))
    artist = property(*Tag._friendly_text_frame("TP1"))

    @property
    def date(self):
        fields = self._get_date("TYE", "TDA", "TIM")
        return self._friendly_date_string(*fields)

    @date.setter
    def date(self, value):
        self._validate_friendly_date(value)
        (year, month, day, hour, minute, second) = self._get_friendly_date(value)
        for f in "TYE", "TDA", "TIM":
            if f in self:
                del self[f]
        if year is not None:
            self["TYE"] = "{0:04}".format(year)
        if month is not None and day is not None:
            self["TDA"] = "{0:02}{1:02}".format(month, day)
        if hour is not None and minute is not None:
            self["TIM"] = "{0:02}{1:02}".format(hour, minute)

    album_artist = property(*Tag._friendly_text_frame("TP2"))
    album = property(*Tag._friendly_text_frame("TAL"))
    track = property(*Tag._friendly_track("TRK", "track_total"))
    track_total = property(*Tag._friendly_track_total("TRK", "track"))
    disc = property(*Tag._friendly_track("TPA", "disc_total"))
    disc_total = property(*Tag._friendly_track_total("TPA", "disc"))
    composer = property(*Tag._friendly_text_frame("TCM"))
    genre = property(*Tag._friendly_text_frame("TCO"))
    comment = property(*Tag._friendly_comment("COM"))
    grouping = property(*Tag._friendly_text_frame("TT1"))
    # TODO: compilation
    picture = property(*Tag._friendly_picture("PIC"))
    sort_title = property(*Tag._friendly_text_frame("TST"))
    sort_artist = property(*Tag._friendly_text_frame("TSP"))
    sort_album_artist = property(*Tag._friendly_text_frame("TS2"))
    sort_album = property(*Tag._friendly_text_frame("TSA"))
    sort_composer = property(*Tag._friendly_text_frame("TSC"))

    def _read_header(self, file):
        self.offset = file.tell()
        header = fileutil.xread(file, 10)
        if header[0:5] != b"ID3\x02\00":
            raise NoTagError("ID3v2.2 header not found")
        if header[5] & 0x80:
            self.flags.add("unsynchronised")
        if header[5] & 0x40: # Compression bit is ill-defined in standard
            raise TagError("ID3v2.2 tag compression is not supported")
        if header[5] & 0x3F:
            warn("Unknown ID3v2.2 flags", TagWarning)
        self.size = Syncsafe.decode(header[6:10]) + 10

    def _read_frames(self, file):
        if "unsynchronised" in self.flags:
            ufile = UnsyncReader(file)
        else:
            ufile = file
        while file.tell() < self.offset + self.size:
            header = fileutil.xread(ufile, 6)
            if not self._is_frame_id(header[0:3]):
                break
            frameid = header[0:3].decode("ASCII")
            size = Int8.decode(header[3:6])
            data = fileutil.xread(ufile, size)
            yield (frameid, None, data)

    def _interpret_frame_flags(self, frameid, bflags, data):
        # No frame flags in v2.2
        return (None, data)

    def __encode_one_frame(self, frame):
        framedata = frame._encode(encodings=self.encodings)

        data = bytearray()
        # Frame id
        if len(frame.frameid) != 3 or not self._is_frame_id(frame.frameid):
            raise "Invalid ID3v2.2 frame id {0}".format(repr(frame.frameid))
        data.extend(frame.frameid.encode("ASCII"))
        # Size
        data.extend(Int8.encode(len(framedata), width=3))
        assert(len(data) == 6)
        data.extend(framedata)
        return data

    def _prepare_frames_hook(self):
        for frameid in self._frames.keys():
            for frame in self._frames[frameid]:
                if isinstance(frame, Frames.TextFrame):
                    # ID3v2.2 doesn't support multiple text values
                    if len(frame.text) > 1:
                        warn("{0}: merged multiple text strings into one value"
                             .format(frame.frameid), FrameWarning)
                        frame.text = [" / ".join(frame.text)]

    def encode(self, size_hint=None):
        if len(self) == 0:  # No frames -> no tag
            return b""
        frames = self._prepare_frames()
        framedata = bytearray().join(self.__encode_one_frame(frame)
                                     for frame in frames)
        if "unsynchronised" in self.flags:
            framedata = Unsync.encode(framedata)

        size = self._get_size_with_padding(size_hint, len(framedata) + 10)

        data = bytearray()
        data.extend(b"ID3\x02\x00")
        data.append(0x80 if "unsynchronised" in self.flags else 0x00)
        data.extend(Syncsafe.encode(size - 10, width=4))
        assert len(data) == 10
        data.extend(framedata)
        if size > len(data):
            data.extend(b"\x00" * (size - len(data)))
        assert len(data) == size
        return data

class Tag23(Tag):
    version = 3
    encodings = ("latin-1", "utf-16")

    def __init__(self):
        super().__init__()

    title = property(*Tag._friendly_text_frame("TIT2"))
    artist = property(*Tag._friendly_text_frame("TPE1"))

    @property
    def date(self):
        fields = self._get_date("TYER", "TDAT", "TIME")
        return self._friendly_date_string(*fields)

    @date.setter
    def date(self, value):
        self._validate_friendly_date(value)
        (year, month, day, hour, minute, second) = self._get_friendly_date(value)
        for f in "TYER", "TDAT", "TIME":
            if f in self:
                del self[f]
        if year is not None:
            self["TYER"] = "{0:04}".format(year)
        if month is not None and day is not None:
            self["TDAT"] = "{0:02}{1:02}".format(month, day)
        if hour is not None and minute is not None:
            self["TIME"] = "{0:02}{1:02}".format(hour, minute)

    album_artist = property(*Tag._friendly_text_frame("TPE2"))
    album = property(*Tag._friendly_text_frame("TALB"))
    track = property(*Tag._friendly_track("TRCK", "track_total"))
    track_total = property(*Tag._friendly_track_total("TRCK", "track"))
    disc = property(*Tag._friendly_track("TPOS", "disc_total"))
    disc_total = property(*Tag._friendly_track_total("TPOS", "disc"))
    composer = property(*Tag._friendly_text_frame("TCOM"))
    genre = property(*Tag._friendly_text_frame("TCON"))
    comment = property(*Tag._friendly_comment("COMM"))
    grouping = property(*Tag._friendly_text_frame("TIT1"))
    # TODO: compilation
    picture = property(*Tag._friendly_picture("APIC"))
    sort_title = property(*Tag._friendly_text_frame("TSOT"))
    sort_artist = property(*Tag._friendly_text_frame("TSOP"))
    sort_album_artist = property(*Tag._friendly_text_frame("TSO2"))
    sort_album = property(*Tag._friendly_text_frame("TSOA"))
    sort_composer = property(*Tag._friendly_text_frame("TSOC"))

    def _read_header(self, file):
        self.offset = file.tell()
        header = fileutil.xread(file, 10)
        if header[0:5] != b"ID3\x03\x00":
            raise NoTagError("ID3v2.3 header not found")
        if header[5] & 0x80:
            self.flags.add("unsynchronised")
        if header[5] & 0x40:
            self.flags.add("extended_header")
        if header[5] & 0x20:
            self.flags.add("experimental")
        if header[5] & 0x1F:
            warn("Unknown ID3v2.3 flags", TagWarning)
        self.size = Syncsafe.decode(header[6:10]) + 10
        if "extended_header" in self.flags:
            self.__read_extended_header(file)

    def __read_extended_header(self, file):
        (size, ext_flags, self.padding_size) = \
            struct.unpack("!IHI", fileutil.xread(file, 10))
        if size != 6 and size != 10:
            warn("Unexpected size of ID3v2.3 extended header: {0}".format(size), 
                 TagWarning)
        if ext_flags & 32768:
            if size < 10:
                warn("Extended header is too short for a CRC field: {0} bytes instead of 10".format(size),
                     TagWarning)
            else:
                self.flags.add("ext:crc_present")
                (self.crc32,) = struct.unpack("!I", fileutil.xread(file, 4))
                size -= 6
        if size > 6:
            fileutil.xread(file, size - 6)

    def _read_frames(self, file):
        if "unsynchronised" in self.flags:
            ufile = UnsyncReader(file)
        else:
            ufile = file
        while file.tell() < self.offset + self.size:
            header = fileutil.xread(ufile, 10)
            if not self._is_frame_id(header[0:4]):
                break
            frameid = header[0:4].decode("ASCII")
            size = Int8.decode(header[4:8])
            bflags = Int8.decode(header[8:10])
            data = fileutil.xread(ufile, size)
            yield (frameid, bflags, data)

    def _interpret_frame_flags(self, frameid, bflags, data):
        flags = set()
        # Frame encoding flags
        if bflags & _FRAME23_FORMAT_UNKNOWN_MASK:
            raise FrameError("{0}: Invalid ID3v2.3 frame encoding flags: 0x{0:X}".format(frameid, bflags))
        if bflags & _FRAME23_FORMAT_COMPRESSED:
            flags.add("compressed")
            expanded_size = Int8.decode(data[0:4])
            data = zlib.decompress(data[4:])
        if bflags & _FRAME23_FORMAT_ENCRYPTED:
            raise FrameError("{0}: Can't read ID3v2.3 encrypted frames".format(frameid))
        if bflags & _FRAME23_FORMAT_GROUP:
            flags.add("group")
            flags.add("group={0}".format(data[0])) # Hack
            data = data[1:]
        # Frame status messages
        if bflags & _FRAME23_STATUS_DISCARD_ON_TAG_ALTER:
            flags.add("discard_on_tag_alter")
        if bflags & _FRAME23_STATUS_DISCARD_ON_FILE_ALTER:
            flags.add("discard_on_file_alter")
        if bflags & _FRAME23_STATUS_READ_ONLY:
            flags.add("read_only")
        if bflags & _FRAME23_STATUS_UNKNOWN_MASK:
            warn("{0}: Unexpected ID3v2.3 frame status flags: 0x{1:X}".format(frameid, bflags), 
                 TagWarning)
        return flags, data

    def __encode_one_frame(self, frame):
        framedata = frame._encode(encodings=self.encodings)
        origlen = len(framedata)

        flagval = 0
        frameinfo = bytearray()
        if "compressed" in frame.flags:
            framedata = zlib.compress(framedata)
            flagval |= _FRAME23_FORMAT_COMPRESSED
            frameinfo.extend(Int8.encode(origlen, width=4))
        if "group" in frame.flags:
            grp = 0
            for flag in frame.flags:
                if flag.startswith("group="):
                    grp = int(flag[6:])
            frameinfo.append(grp)
            flagval |= _FRAME23_FORMAT_GROUP
        if "discard_on_tag_alter" in frame.flags:
            flagval |= _FRAME23_STATUS_DISCARD_ON_TAG_ALTER
        if "discard_on_file_alter" in frame.flags:
            flagval |= _FRAME23_STATUS_DISCARD_ON_FILE_ALTER
        if "read_only" in frame.flags:
            flagval |= _FRAME23_STATUS_READ_ONLY

        data = bytearray()
        # Frame id
        if len(frame.frameid) != 4 or not self._is_frame_id(frame.frameid.encode("ASCII")):
            raise ValueError("Invalid ID3v2.3 frame id {0}".format(repr(frame.frameid)))
        data.extend(frame.frameid.encode("ASCII"))
        # Size
        data.extend(Int8.encode(len(frameinfo) + len(framedata), width=4))
        # Flags
        data.extend(Int8.encode(flagval, width=2))
        assert len(data) == 10
        # Format info
        data.extend(frameinfo)
        # Frame data
        data.extend(framedata)
        return data

    def encode(self, size_hint=None):
        if len(self) == 0:  # No frames -> no tag
            return b""
        frames = self._prepare_frames()
        framedata = bytearray().join(self.__encode_one_frame(frame)
                                     for frame in frames)
        if "unsynchronised" in self.flags:
            framedata = Unsync.encode(framedata)

        size = self._get_size_with_padding(size_hint, len(framedata) + 10)

        data = bytearray()
        data.extend(b"ID3\x03\x00")
        flagval = 0x00
        if "unsynchronised" in self.flags:
            flagval |= 0x80
        data.append(flagval)
        data.extend(Syncsafe.encode(size - 10, width=4))
        assert len(data) == 10
        data.extend(framedata)
        if size > len(data):
            data.extend(b"\x00" * (size - len(data)))
        assert len(data) == size
        return data

class Tag24(Tag):
    ITUNES_WORKAROUND = False

    version = 4
    encodings = ("latin-1", "utf-8")

    def __init__(self):
        super().__init__()

    title = property(*Tag._friendly_text_frame("TIT2"))
    artist = property(*Tag._friendly_text_frame("TPE1"))
    
    @property
    def date(self):
        try:
            frame = self["TDRC"]
        except KeyError:
            return ""
        else:
            return frame.text[0]

    @date.setter
    def date(self, value):
        self._validate_friendly_date(value)
        fields = self._get_friendly_date(value)
        val = self._friendly_date_string(*fields)
        if val:
            self["TDRC"] = val
        elif "TDRC" in self:
            del self["TDRC"]

    album = property(*Tag._friendly_text_frame("TALB"))
    album_artist = property(*Tag._friendly_text_frame("TPE2"))
    track = property(*Tag._friendly_track("TRCK", "track_total"))
    track_total = property(*Tag._friendly_track_total("TRCK", "track"))
    disc = property(*Tag._friendly_track("TPOS", "disc_total"))
    disc_total = property(*Tag._friendly_track_total("TPOS", "disc"))
    composer = property(*Tag._friendly_text_frame("TCOM"))
    genre = property(*Tag._friendly_text_frame("TCON"))
    comment = property(*Tag._friendly_comment("COMM"))
    grouping = property(*Tag._friendly_text_frame("TIT1"))
    # TODO: compilation
    picture = property(*Tag._friendly_picture("APIC"))
    sort_title = property(*Tag._friendly_text_frame("TSOT"))
    sort_artist = property(*Tag._friendly_text_frame("TSOP"))
    sort_album_artist = property(*Tag._friendly_text_frame("TSO2"))
    sort_album = property(*Tag._friendly_text_frame("TSOA"))
    sort_composer = property(*Tag._friendly_text_frame("TSOC"))

    def _read_header(self, file):
        self.offset = file.tell()
        header = fileutil.xread(file, 10)
        if header[0:5] != b"ID3\x04\x00":
            raise NoTagError("ID3v2 header not found")
        if header[5] & _TAG24_UNSYNCHRONISED:
            self.flags.add("unsynchronised")
        if header[5] & _TAG24_EXTENDED_HEADER:
            self.flags.add("extended_header")
        if header[5] & _TAG24_EXPERIMENTAL:
            self.flags.add("experimental")
        if header[5] & _TAG24_FOOTER:
            self.flags.add("footer")
        if header[5] & _TAG24_UNKNOWN_MASK:
            warn("Unknown ID3v2.4 flags", TagWarning)
        self.size = (Syncsafe.decode(header[6:10]) + 10 
                     + (10 if "footer" in self.flags else 0))
        if "extended_header" in self.flags:
            self.__read_extended_header(file)

    def __read_extended_header_flag_data(self, data):
        # 1-byte length + data
        length = data[0]
        if length & 128:
            raise TagError("Invalid size of extended header field")
        return (data[1:1+length], data[1+length:])

    def __read_extended_header(self, file):
        size = Syncsafe.decode(fileutil.xread(file, 4))
        if size < 6:
            warn("Unexpected size of ID3v2.4 extended header: {0}".format(size), 
                 TagWarning)
        data = fileutil.xread(file, size - 4)

        numflags = data[0]
        if numflags != 1:
            warn("Unexpected number of ID3v2.4 extended flag bytes: {0}"
                 .format(numflags), 
                 TagWarning)
        flags = data[1]
        data = data[1+numflags:]
        if flags & 0x40:
            self.flags.add("ext:update")
            (dummy, data) = self.__read_extended_header_flag_data(data)
        if flags & 0x20:
            self.flags.add("ext:crc_present")
            (self.crc32, data) = self.__read_extended_header_flag_data(data)
            self.crc32 = Syncsafe.decode(self.crc32)
        if flags & 0x10:
            self.flags.add("ext:restrictions")
            (self.restrictions, data) = self.__read_extended_header_flag_data(data)

    def _read_frames(self, file, syncsafe_workaround = None):
        # Older versions of iTunes stored frame sizes as straight 8bit integers,
        # not syncsafe values as the spec requires.
        # (The bug is known to be fixed in iTunes 8.2.)
        #
        # To work around such an erroneous encoding, we re-read the entire tag 
        # in non-syncsafe mode when we detect a frame with a bad size.
        # This heuristic does not detect all badly encoded tags; 
        # it fails when the 8-bit frame size happens to be in syncsafe format.
        #
        # We could improve detection by parsing the tag both ways and see which 
        # interpretation produces more frames. However, the extra effort doesn't
        # seem worthwhile to do by default.
        #
        # If you have many files with iTunes-encoded tags, you can force stagger
        # to read them in non-syncsafe mode setting the ITUNES_WORKAROUND
        # class attribute to True and let stagger reencode your tags. (Stagger
        # will never produce a 2.4 tag with non-syncsafe frame lengths.)        
        if syncsafe_workaround is None:
            syncsafe_workaround = self.ITUNES_WORKAROUND
        origfpos = file.tell()
        frames = []
        while file.tell() < self.offset + self.size:
            header = fileutil.xread(file, 10)
            if not self._is_frame_id(header[0:4]):
                break
            frameid = header[0:4].decode("ASCII")
            if syncsafe_workaround:
                size = Int8.decode(header[4:8])
            else:
                try:
                    size = Syncsafe.decode(header[4:8])
                except ValueError:
                    if syncsafe_workaround:
                        raise
                    warn("Invalid syncsafe frame size; switching to 8-bit mode")
                    file.seek(origfpos)
                    return self._read_frames(file, True)
            bflags = Int8.decode(header[8:10])
            data = fileutil.xread(file, size)
            frames.append((frameid, bflags, data))
        return frames

    def _interpret_frame_flags(self, frameid, bflags, data):
        flags = set()
        # Frame format flags
        if bflags & _FRAME24_FORMAT_UNKNOWN_MASK:
            raise FrameError("{0}: Unknown frame encoding flags: 0x{1:X}".format(frameid, bflags))
        if bflags & _FRAME24_FORMAT_GROUP:
            flags.add("group")
            flags.add("group={0}".format(data[0])) # hack
            data = data[1:]
        if bflags & _FRAME24_FORMAT_COMPRESSED:
            flags.add("compressed")
        if bflags & _FRAME24_FORMAT_ENCRYPTED:
            raise FrameError("{0}: Can't read encrypted frames".format(frameid))
        if bflags & _FRAME24_FORMAT_UNSYNCHRONISED:
            flags.add("unsynchronised")
        expanded_size = len(data)
        if bflags & _FRAME24_FORMAT_DATA_LENGTH_INDICATOR:
            flags.add("data_length_indicator")
            expanded_size = Syncsafe.decode(data[0:4])
            data = data[4:]
        if "unsynchronised" in self.flags:
            data = Unsync.decode(data)
        if "compressed" in self.flags:
            data = zlib.decompress(data)
        # Frame status flags
        if bflags & _FRAME24_STATUS_DISCARD_ON_TAG_ALTER:
            flags.add("discard_on_tag_alter")
        if bflags & _FRAME24_STATUS_DISCARD_ON_FILE_ALTER:
            flags.add("discard_on_file_alter")
        if bflags & _FRAME24_STATUS_READ_ONLY:
            flags.add("read_only")
        if bflags & _FRAME24_STATUS_UNKNOWN_MASK:
            warn("{0}: Unexpected status flags: 0x{1:X}"
                 .format(frameid, bflags), FrameWarning)
        return flags, data

    def __encode_one_frame(self, frame):
        framedata = frame._encode(encodings=self.encodings)
        origlen = len(framedata)

        flagval = 0
        frameinfo = bytearray()
        if "group" in frame.flags:
            grp = 0
            for flag in frame.flags:
                if flag.startswith("group="):
                    grp = int(flag[6:])
            frameinfo.append(grp)
            flagval |= _FRAME24_FORMAT_GROUP
        if "compressed" in frame.flags:
            frame.flags.add("data_length_indicator")
            framedata = zlib.compress(framedata)
            flagval |= _FRAME24_FORMAT_COMPRESSED
        if "unsynchronised" in frame.flags:
            frame.flags.add("data_length_indicator")
            framedata = Unsync.encode(framedata)
            flagval |= _FRAME24_FORMAT_UNSYNCHRONISED
        if "data_length_indicator" in frame.flags:
            frameinfo.extend(Syncsafe.encode(origlen, width=4))
            flagval |= _FRAME24_FORMAT_DATA_LENGTH_INDICATOR

        if "discard_on_tag_alter" in frame.flags:
            flagval |= _FRAME24_STATUS_DISCARD_ON_TAG_ALTER
        if "discard_on_file_alter" in frame.flags:
            flagval |= _FRAME24_STATUS_DISCARD_ON_FILE_ALTER
        if "read_only" in frame.flags:
            flagval |= _FRAME24_STATUS_READ_ONLY

        data = bytearray()
        # Frame id
        if len(frame.frameid) != 4 or not self._is_frame_id(frame.frameid):
            raise "{0}: Invalid frame id".format(repr(frame.frameid))
        data.extend(frame.frameid.encode("ASCII"))
        # Size
        data.extend(Syncsafe.encode(len(frameinfo) + len(framedata), width=4))
        # Flags
        data.extend(Int8.encode(flagval, width=2))
        assert len(data) == 10
        # Format info
        data.extend(frameinfo)
        # Frame data
        data.extend(framedata)
        return data

    def encode(self, size_hint=None):
        if len(self) == 0:  # No frames -> no tag
            return b""
        frames = self._prepare_frames()
        if "unsynchronised" in self.flags:
            for frame in frames: 
                frame.flags.add("unsynchronised")
        framedata = bytearray().join(self.__encode_one_frame(frame)
                                     for frame in frames)

        size = self._get_size_with_padding(size_hint, len(framedata) + 10)

        data = bytearray()
        data.extend(b"ID3\x04\x00")
        flagval = 0x00
        if "unsynchronised" in self.flags:
            flagval |= 0x80
        data.append(flagval)
        data.extend(Syncsafe.encode(size - 10, width=4))
        assert len(data) == 10
        data.extend(framedata)
        if size > len(data):
            data.extend(b"\x00" * (size - len(data)))
        assert len(data) == size
        return data


_tag_versions = {
    2: Tag22,
    3: Tag23,
    4: Tag24,
    }
