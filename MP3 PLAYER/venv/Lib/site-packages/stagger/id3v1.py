#
# id3v1.py
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

import string

from stagger.errors import *
import stagger.fileutil as fileutil

from stagger.id3 import genres

class Tag1():
    @property
    def genre(self):
        if self._genre < len(genres):
            return "{0} ({1})".format(self._genre, genres[self._genre])
        else:
            return "{0} (unknown)".format(self._genre)

    @genre.setter
    def genre(self, value):
        if value is None:
            self._genre = 0
            return
        if type(value) == int:
            if value in range(256):
                self._genre = value
            else:
                raise ValueError("Genre must be between 0 and 255")
            return
        if type(value) == str:
            if value.lower() == "unknown":
                self._genre = 255
                return
            try:
                self._genre = genres.index(value)
                return
            except ValueError:
                raise ValueError("Unknown genre")
        raise TypeError("Invalid genre")

    def __str__(self):
        return "\n".join(["title={0}".format(repr(self.title)),
                          "artist={0}".format(repr(self.artist)),
                          "album={0}".format(repr(self.album)),
                          "year={0}".format(repr(self.year)),
                          "comment={0}".format(repr(self.comment)),
                          "genre={0}".format(self.genre)])

    def __repr__(self):
        return "Tag1({0})".format(", ".join(["title={0}".format(repr(self.title)),
                                             "artist={0}".format(repr(self.artist)),
                                             "album={0}".format(repr(self.album)),
                                             "year={0}".format(repr(self.year)),
                                             "comment={0}".format(repr(self.comment)),
                                             "genre={0}".format(self._genre)]))

    def __eq__(self, other):
        return (isinstance(other, Tag1)
                and self.title == other.title
                and self.artist == other.artist
                and self.album == other.album
                and self.year == other.year
                and self.comment == other.comment
                and self._genre == other._genre)
    
    @classmethod
    def decode(cls, data, encoding="iso-8859-1"):
        def decode_field(data):
            try:
                data = data[:data.index(b"\x00")]
            except ValueError:
                pass
            return data.decode(encoding).strip(string.whitespace)
        if data[:3] != b"TAG" or len(data) < 128:
            raise NoTagError("ID3v1 tag not found")
        tag = Tag1()
        tag.title = decode_field(data[3:33])
        tag.artist = decode_field(data[33:63])
        tag.album = decode_field(data[63:93])
        tag.year = decode_field(data[93:97])
        if data[125] == 0:
            tag.comment = decode_field(data[97:125])
            tag.track = data[126]
        else:
            tag.comment = decode_field(data[97:127])
            tag.track = 0
        tag._genre = data[127]
        return tag

    @classmethod
    def read(cls, filename, offset=None, encoding="iso-8859-1"):
        """Read an ID3v1 tag from a file."""
        with fileutil.opened(filename, "rb") as file:
            if offset is None:
                file.seek(-128, 2)
            else:
                file.seek(offset)
            data = file.read(128)
            return cls.decode(data, encoding=encoding)

    @classmethod
    def delete(cls, filename, offset=None):
        """Delete ID3v1 tag from a file (if present)."""
        with fileutil.opened(filename, "rb+") as file:
            if offset is None:
                file.seek(-128, 2)
            else:
                file.seek(offset)
            offset = file.tell()
            data = file.read(128)
            if data[:3] == b"TAG":
                fileutil.replace_chunk(file, offset, 128, b"", in_place=True)

    def encode(self, encoding="iso-8859-1", errors="strict"):
        def encode_field(field, width):
            data = field.encode(encoding, errors)
            if len(data) < width:
                data = data + b"\x00" * (width - len(data))
            return data[:width]
        data = bytearray(b"TAG")
        data.extend(encode_field(self.title, 30))
        data.extend(encode_field(self.artist, 30))
        data.extend(encode_field(self.album, 30))
        data.extend(encode_field(self.year, 4))
        if self.track:
            data.extend(encode_field(self.comment, 28))
            data.append(0)
            data.append(self.track)
        else:
            data.extend(encode_field(self.comment, 30))
        data.append(self._genre)
        assert len(data) == 128
        return data

    def write(self, filename, encoding="iso-8859-1", errors="strict"):
        with fileutil.opened(filename, "rb+") as file:
            file.seek(-128, 2)
            data = file.read(128)
            if data[:3] == b"TAG":
                file.seek(-128, 2)
            else:
                file.seek(0, 2)
            file.write(self.encode(encoding, errors))

