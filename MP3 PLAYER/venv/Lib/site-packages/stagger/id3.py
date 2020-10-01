#
# id3.py
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

"""List of frames defined in the various ID3 versions.
"""

import imghdr

import stagger.tags as tags
from stagger.frames import *
from stagger.specs import *
from stagger.tags import frameclass


# ID3v2.4

# 4.2.1. Identification frames
@frameclass
class UFID(Frame):
    "Unique file identifier"
    _framespec = (NullTerminatedStringSpec("owner"), BinaryDataSpec("data"))
    _allow_duplicates = True

@frameclass
class TIT1(TextFrame): 
    "Content group description"

@frameclass
class TIT2(TextFrame): 
    "Title/songname/content description"

@frameclass
class TIT3(TextFrame): 
    "Subtitle/Description refinement"

@frameclass
class TALB(TextFrame): 
    "Album/Movie/Show title"

@frameclass
class TOAL(TextFrame): 
    "Original album/movie/show title"

@frameclass
class TRCK(TextFrame): 
    "Track number/Position in set"
# #/#

@frameclass
class TPOS(TextFrame): 
    "Part of a set"
# #/#

@frameclass
class TSST(TextFrame):
    "Set subtitle"
    _version = 4

@frameclass
class TSRC(TextFrame): 
    "ISRC (international standard recording code)"


# 4.2.2. Involved persons frames
@frameclass
class TPE1(TextFrame): 
    "Lead performer(s)/Soloist(s)"

@frameclass
class TPE2(TextFrame): 
    "Band/orchestra/accompaniment"

@frameclass
class TPE3(TextFrame): 
    "Conductor/performer refinement"

@frameclass
class TPE4(TextFrame): 
    "Interpreted, remixed, or otherwise modified by"

@frameclass
class TOPE(TextFrame): 
    "Original artist(s)/performer(s)"

@frameclass
class TEXT(TextFrame): "Lyricist/Text writer"
@frameclass
class TOLY(TextFrame): "Original lyricist(s)/text writer(s)"
@frameclass
class TCOM(TextFrame): "Composer"

@frameclass
class TMCL(CreditsFrame):
    "Musician credits list"
    _version = 4

@frameclass
class TIPL(CreditsFrame):
    "Involved people list"
    _version = 4

@frameclass
class TENC(TextFrame): "Encoded by"



# 4.2.3. Derived and subjective properties frames

@frameclass
class TBPM(TextFrame): "BPM (beats per minute)"
# integer in string format

@frameclass
class TLEN(TextFrame): "Length"
# milliseconds in string format

@frameclass
class TKEY(TextFrame): "Initial key"
# /^([CDEFGAB][b#]?[m]?|o)$/

@frameclass
class TLAN(TextFrame): "Language(s)"
# /^...$/  ISO 639-2

@frameclass
class TCON(TextFrame): "Content type"
# integer  - ID3v1
# RX - Remix
# CR - Cover
# Freeform text
# id3v2.3: (number), 

@frameclass
class TFLT(TextFrame): "File type"
@frameclass
class TMED(TextFrame): "Media type"
@frameclass
class TMOO(TextFrame):
    "Mood"
    _version = 4


# 4.2.4. Rights and license frames

@frameclass
class TCOP(TextFrame): "Copyright message"
@frameclass
class TPRO(TextFrame):
    "Produced notice"
    _version = 4
    
@frameclass
class TPUB(TextFrame): "Publisher"
@frameclass
class TOWN(TextFrame): "File owner/licensee"
@frameclass
class TRSN(TextFrame): "Internet radio station name"
@frameclass
class TRSO(TextFrame): "Internet radio station owner"



# 4.2.5. Other text frames

@frameclass
class TOFN(TextFrame): "Original filename"
@frameclass
class TDLY(TextFrame): "Playlist delay"
# milliseconds

@frameclass
class TDEN(TextFrame):
    # timestamp
    "Encoding time"
    _version = 4

@frameclass
class TDOR(TextFrame):
    "Original release time"
    # timestamp
    _version = 4

@frameclass
class TDRC(TextFrame):
    "Recording time"
    # timestamp
    _version = 4

@frameclass
class TDRL(TextFrame):
    "Release time"
    # timestamp
    _version = 4

@frameclass
class TDTG(TextFrame):
    "Tagging time"
    # timestamp
    _version = 4

@frameclass
class TSSE(TextFrame): 
    "Software/Hardware and settings used for encoding"

@frameclass
class TSOA(TextFrame):
    "Album sort order"
    _version = 4

@frameclass
class TSOP(TextFrame):
    "Performer sort order"
    _version = 4

@frameclass
class TSOT(TextFrame):
    "Title sort order"
    _version = 4


# 4.2.6. User defined information frame

@frameclass
class TXXX(Frame):
    "User defined text information frame"
    _framespec = (EncodingSpec("encoding"),
                  EncodedStringSpec("description"),
                  EncodedStringSpec("value"))
    _allow_duplicates = True


# 4.3. URL link frames

@frameclass
class WCOM(URLFrame): 
    "Commercial information"
    _allow_duplicates = True

@frameclass
class WCOP(URLFrame): 
    "Copyright/Legal information"

@frameclass
class WOAF(URLFrame): 
    "Official audio file webpage"

@frameclass
class WOAR(URLFrame): 
    "Official artist/performer webpage"
    _allow_duplicates = True

@frameclass
class WOAS(URLFrame): 
    "Official audio source webpage"

@frameclass
class WORS(URLFrame): 
    "Official Internet radio station homepage"

@frameclass
class WPAY(URLFrame): 
    "Payment"

@frameclass
class WPUB(URLFrame): 
    "Publishers official webpage"

@frameclass
class WXXX(Frame):
    "User defined URL link frame"
    _framespec = (EncodingSpec("encoding"),
                  EncodedStringSpec("description"),
                  URLStringSpec("url"))
    _allow_duplicates = True


# 4.4.-4.13  Junk frames
@frameclass
class MCDI(Frame):
    "Music CD identifier"
    _framespec = (BinaryDataSpec("cd_toc"),)

@frameclass
class ETCO(Frame):
    "Event timing codes"
    _framespec = (ByteSpec("format"),
                  MultiSpec("events", ByteSpec("type"), IntegerSpec("timestamp", 32)))
    _untested = True
    _bozo = True

@frameclass
class MLLT(Frame):
    "MPEG location lookup table"
    _framespec = (IntegerSpec("frames", 16), IntegerSpec("bytes", 24),
                  IntegerSpec("milliseconds", 24),
                  ByteSpec("bits_for_bytes"), ByteSpec("bits_for_milliseconds"),
                  BinaryDataSpec("data"))
    _untested = True
    _bozo = True

@frameclass
class SYTC(Frame):
    "Synchronised tempo codes"
    _framespec = (ByteSpec("format"), BinaryDataSpec("data"))
    _untested = True
    _bozo = True

@frameclass
class USLT(Frame):
    "Unsynchronised lyric/text transcription"
    _framespec = (EncodingSpec("encoding"), LanguageSpec("lang"),
                  EncodedStringSpec("desc"), EncodedFullTextSpec("text"))
    _allow_duplicates = True
    
@frameclass
class SYLT(Frame):
    "Synchronised lyric/text"
    _framespec = (EncodingSpec("encoding"), LanguageSpec("lang"),
                  ByteSpec("format"), ByteSpec("type"),
                  EncodedStringSpec("desc"),
                  MultiSpec("data", EncodedFullTextSpec("text"), 
                            IntegerSpec("timestamp", 32)))
    _allow_duplicates = True
    _bozo = True

@frameclass
class COMM(Frame):
    "Comments"
    _framespec = (EncodingSpec("encoding"), LanguageSpec("lang"),
                  EncodedStringSpec("desc"), EncodedFullTextSpec("text"))
    _allow_duplicates = True

@frameclass
class RVA2(Frame):
    "Relative volume adjustment (2)"
    _framespec = (NullTerminatedStringSpec("desc"),
                  MultiSpec("adjustment",
                            ByteSpec("channel"),
                            IntegerSpec("gain", 16),  # * 512
                            VarIntSpec("peak")))
    _allow_duplicates = True

@frameclass
class EQU2(Frame):
    "Equalisation (2)"
    _framespec = (ByteSpec("method"), NullTerminatedStringSpec("desc"),
                  MultiSpec("adjustments",
                            IntegerSpec("frequency", 16), # in 0.5Hz
                            SignedIntegerSpec("adjustment", 16))) # * 512x
    _allow_duplicates = True
    _untested = True
    _bozo = True

@frameclass
class RVRB(Frame):
    "Reverb"
    _framespec = (IntegerSpec("left", 16),
                  IntegerSpec("right", 16),
                  ByteSpec("bounce_left"), ByteSpec("bounce_right"),
                  ByteSpec("feedback_ltl"), ByteSpec("feedback_ltr"),
                  ByteSpec("feedback_rtr"), ByteSpec("feedback_rtl"),
                  ByteSpec("premix_ltr"), ByteSpec("premix_rtl"))
    _untested = True
    _bozo = True

@frameclass
class APIC(PictureFrame):
    "Attached picture"
    _framespec = (EncodingSpec("encoding"),
                  NullTerminatedStringSpec("mime"),
                  PictureTypeSpec("type"),
                  EncodedStringSpec("desc"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True

    def _set_format(self, format):
        if format.lower() in ("jpeg", "jpg", "image/jpeg", "image/jpg"):
            self.mime = "image/jpeg"
        elif format.lower() in ("png", "image/png"):
            self.mime = "image/png"
        else:
            raise ValueError("invalid image format")

    def _to_version(self, version):
        if version in (3, 4):
            return self
        if self.mime.lower() not in ("image/jpeg", "image/jpg", "image/png"):
            raise ValueError("Unsupported image format")
        return PIC(format="PNG" if self.mime.lower() == "image/png" else "JPG",
                   type=self.type,
                   desc=self.desc,
                   data=self.data)
            
    def _str_fields(self):
        img = "{0} bytes of {1} data".format(len(self.data), 
                                             imghdr.what(None, self.data[:32]))
        return ("type={0}, desc={1}, mime={2}: {3}"
                .format(repr(self._spec("type").to_str(self.type)),
                        repr(self.desc),
                        repr(self.mime),
                        img))

@frameclass
class GEOB(Frame):
    "General encapsulated object"
    _framespec = (EncodingSpec("encoding"),
                  NullTerminatedStringSpec("mime"),
                  EncodedStringSpec("filename"),
                  EncodedStringSpec("desc"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True

@frameclass
class PCNT(Frame):
    "Play counter"
    _framespec = (IntegerSpec("count", 32),)

@frameclass
class POPM(Frame):
    "Popularimeter"
    _framespec = (NullTerminatedStringSpec("email"),
                  ByteSpec("rating"),
                  # Windows Vista's explorer does not generate a count
                  optionalspec(IntegerSpec("count", 32)))
    _allow_duplicates = True

@frameclass
class RBUF(Frame):
    "Recommended buffer size"
    _framespec = (IntegerSpec("size", 32),
                  optionalspec(ByteSpec("info")),
                  optionalspec(IntegerSpec("offset", 32)))
    _untested = True
    _bozo = True

@frameclass
class AENC(Frame):
    "Audio encryption"
    _framespec = (NullTerminatedStringSpec("owner"),
                  IntegerSpec("preview_start", 16),
                  IntegerSpec("preview_length", 16),
                  BinaryDataSpec("data"))
    _allow_duplicates = True
    _untested = True
    _bozo = True

@frameclass
class LINK(Frame):
    "Linked information"
    _framespec = (SimpleStringSpec("linked_frameid", 4),
                  NullTerminatedStringSpec("url"),
                  optionalspec(BinaryDataSpec("data")))
    _allow_duplicates = True
    _untested = True
    _bozo = True

@frameclass
class POSS(Frame):
    "Position synchronisation frame"
    _framespec = (ByteSpec("format"),
                  IntegerSpec("position", 32))
    _untested = True
    _bozo = True

@frameclass
class USER(Frame):
    "Terms of use"
    # TODO: emusic.com forgets the language field
    _framespec = (EncodingSpec("encoding"),
                  LanguageSpec("lang"),
                  EncodedStringSpec("text"))
    _allow_duplicates = True

@frameclass
class OWNE(Frame):
    "Ownership frame"
    _framespec = (EncodingSpec("encoding"),
                  NullTerminatedStringSpec("price"),
                  SimpleStringSpec("date", 8),
                  NullTerminatedStringSpec("seller"))
    _untested = True
    _bozo = True

@frameclass
class COMR(Frame):
    "Commercial frame"
    _framespec = (EncodingSpec("encoding"),
                  NullTerminatedStringSpec("price"),
                  NullTerminatedStringSpec("valid"),
                  NullTerminatedStringSpec("contact"),
                  ByteSpec("format"),
                  EncodedStringSpec("seller"),
                  EncodedStringSpec("desc"),
                  NullTerminatedStringSpec("mime"),
                  BinaryDataSpec("logo"))
    _allow_duplicates = True
    _untested = True
    _bozo = True

@frameclass
class ENCR(Frame):
    "Encryption method registration"
    _framespec = (NullTerminatedStringSpec("owner"),
                  ByteSpec("symbol"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True
    _untested = True
    _bozo = True


@frameclass
class GRID(Frame):
    "Group identification registration"
    _framespec = (NullTerminatedStringSpec("owner"),
                  ByteSpec("symbol"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True
    _untested = True
    _bozo = True

@frameclass
class PRIV(Frame):
    "Private frame"
    _framespec = (NullTerminatedStringSpec("owner"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True

@frameclass
class SIGN(Frame):
    "Signature frame"
    _framespec = (ByteSpec("group"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True
    _untested = True
    _bozo = True
    _version = 4

@frameclass
class SEEK(Frame):
    "Seek frame"
    _framespec = (IntegerSpec("offset", 32), )
    _untested = True
    _bozo = True
    _version = 4

@frameclass
class ASPI(Frame):
    "Audio seek point index"
    _framespec = (IntegerSpec("S", 32),
                  IntegerSpec("L", 32),
                  IntegerSpec("N", 16),
                  ByteSpec("b"),
                  ASPISpec("Fi"))
    _version = 4
    _untested = True
    _bozo = True


# ID3v2.3

@frameclass
class TYER(TextFrame):
    """Year
    A numerical string with the year of the recording.
    Replaced by TDRC in id3v2.4
    """
    _version = 3
    
@frameclass
class TDAT(TextFrame):
    """Date
    A numerical string in DDMM format containing the date for the recording.
    Replaced by TDRC in id3v2.4
    """
    _version = 3

@frameclass
class TIME(TextFrame):
    """Time
    A numerical string in HHMM format containing the time for the recording.
    Replaced by TDRC in id3v2.4
    """
    _version = 3

@frameclass
class TORY(TextFrame):
    """Original release year
    Replaced by TDOR in id3v2.4
    """
    _version = 3

@frameclass
class TRDA(TextFrame):
    """Recording dates
    Replaced by TDRC in id3v2.4
    """
    _version = 3

@frameclass
class TSIZ(TextFrame):
    """Size
    Size of the audio file in bytes, excluding the ID3v2 tag.
    Removed in id3v2.4
    """
    _version = 3

@frameclass
class IPLS(CreditsFrame):
    """Involved people list
    Replaced by TMCL and TIPL in id3v2.4
    """
    _bozo = True
    _version = 3

@frameclass
class EQUA(Frame):
    """Equalisation
    Replaced by EQU2 in id3v2.4
    """
    _framespec = (ByteSpec("bits"), BinaryDataSpec("data"))
    _untested = True
    _bozo = True
    _version = 3

@frameclass
class RVAD(Frame):
    """Relative volume adjustment
    Replaced by RVA2 in id3v2.4.
    """
    _framespec = (ByteSpec("signs"), ByteSpec("bits"),
                  RVADIntegerSpec("vol_right", "bits", 0),
                  RVADIntegerSpec("vol_left", "bits", 1),
                  IntegerSpec("peak_right", "bits"),
                  IntegerSpec("peak_left", "bits"),
                  optionalspec(RVADIntegerSpec("vol_right_back", "bits", 2)),
                  optionalspec(RVADIntegerSpec("vol_left_back", "bits", 3)),
                  optionalspec(IntegerSpec("peak_right_back", "bits")),
                  optionalspec(IntegerSpec("peak_left_back", "bits")),
                  optionalspec(RVADIntegerSpec("vol_center", "bits", 4)),
                  optionalspec(IntegerSpec("peak_center", "bits")),
                  optionalspec(RVADIntegerSpec("vol_bass", "bits", 5)),
                  optionalspec(IntegerSpec("peak_bass", "bits")))
    _version = 3

# ID3v2.2

@frameclass
class UFI(UFID): pass
@frameclass
class TT1(TIT1): pass
@frameclass
class TT2(TIT2): pass
@frameclass
class TT3(TIT3): pass
@frameclass
class TP1(TPE1): pass
@frameclass
class TP2(TPE2): pass
@frameclass
class TP3(TPE3): pass
@frameclass
class TP4(TPE4): pass
@frameclass
class TCM(TCOM): pass
@frameclass
class TXT(TEXT): pass
@frameclass
class TLA(TLAN): pass
@frameclass
class TCO(TCON): pass
@frameclass
class TAL(TALB): pass
@frameclass
class TPA(TPOS): pass
@frameclass
class TRK(TRCK): pass
@frameclass
class TRC(TSRC): pass
@frameclass
class TYE(TYER): pass
@frameclass
class TDA(TDAT): pass
@frameclass
class TIM(TIME): pass
@frameclass
class TRD(TRDA): pass
@frameclass
class TMT(TMED): pass
@frameclass
class TFT(TFLT): pass
@frameclass
class TBP(TBPM): pass
@frameclass
class TCR(TCOP): pass
@frameclass
class TPB(TPUB): pass
@frameclass
class TEN(TENC): pass
@frameclass
class TSS(TSSE): pass
@frameclass
class TOF(TOFN): pass
@frameclass
class TLE(TLEN): pass
@frameclass
class TSI(TSIZ): pass
@frameclass
class TDY(TDLY): pass
@frameclass
class TKE(TKEY): pass
@frameclass
class TOT(TOAL): pass
@frameclass
class TOA(TOPE): pass
@frameclass
class TOL(TOLY): pass
@frameclass
class TOR(TORY): pass

@frameclass
class TXX(TXXX): pass

@frameclass
class WAF(WOAF): pass
@frameclass
class WAR(WOAR): pass
@frameclass
class WAS(WOAS): pass
@frameclass
class WCM(WCOM): pass
@frameclass
class WCP(WCOP): pass
@frameclass
class WPB(WPUB): pass

@frameclass
class WXX(WXXX): pass

@frameclass
class IPL(IPLS): pass

@frameclass
class MCI(MCDI): pass
@frameclass
class ETC(ETCO): pass
@frameclass
class MLL(MLLT): pass
@frameclass
class STC(SYTC): pass
@frameclass
class ULT(USLT): pass
@frameclass
class SLT(SYLT): pass

@frameclass
class COM(COMM): pass

@frameclass
class RVA(RVAD): pass
@frameclass
class EQU(EQUA): pass
@frameclass
class REV(RVRB): pass

@frameclass
class PIC(PictureFrame):
    "Attached picture"
    _framespec = (EncodingSpec("encoding"),
                  SimpleStringSpec("format", 3),
                  PictureTypeSpec("type"),
                  EncodedStringSpec("desc"),
                  BinaryDataSpec("data"))
    _allow_duplicates = True
    _version = 2

    def _set_format(self, format):
        if format.lower() in ("jpeg", "jpg", "image/jpeg", "image/jpg"):
            self.format = "JPG"
        elif format.lower() in ("png", "image/png"):
            self.format = "PNG"
        else:
            raise ValueError("invalid image format")

    def _to_version(self, version):
        if version == 2:
            return self
        assert version in (3, 4)
        if self.format.upper() == "PNG":
            mime = "image/png"
        elif self.format.upper() == "JPG":
            mime = "image/jpeg"
        else:
            mime = imghdr.what(io.StringIO(self.data))
            if mime is None:
                raise ValueError("Unknown image format")
            mime = "image/" + mime.lower()
        return APIC(mime=mime, type=self.type, desc=self.desc, data=self.data)
        
    def _str_fields(self):
        img = "{0} bytes of {1} data".format(len(self.data), 
                                             imghdr.what(None, self.data[:32]))
        return ("type={0}, desc={1}, format={2}: {3}"
                .format(repr(self._spec("type").to_str(self.type)),
                        repr(self.desc),
                        repr(self.format),
                        img))

@frameclass
class GEO(GEOB): pass
@frameclass
class CNT(PCNT): pass
@frameclass
class POP(POPM): pass

@frameclass
class BUF(RBUF): pass
@frameclass
class CRM(Frame):
    "Encrypted meta frame"
    _framespec = (NullTerminatedStringSpec("owner"),
                  NullTerminatedStringSpec("content"),
                  BinaryDataSpec("data"))
    _bozo = True
    _untested = True
    _version = 2

@frameclass
class CRA(AENC): pass

@frameclass
class LNK(Frame):
    "Linked information"
    _framespec = (SimpleStringSpec("linked_frame", 3),
                  NullTerminatedStringSpec("url"),
                  BinaryDataSpec("data"))
    _bozo = True
    _untested = True
    _version = 2

# Nonstandard frames
@frameclass
class TCMP(TextFrame): 
    "iTunes: Part of a compilation"
    _nonstandard = True

@frameclass
class TCP(TCMP): pass

@frameclass
class TDES(TextFrame): 
    "iTunes: Podcast description"
    _nonstandard = True
@frameclass
class TDS(TDES): pass

@frameclass
class TGID(TextFrame): 
    "iTunes: Podcast identifier"
    _nonstandard = True
@frameclass
class TID(TGID): pass

@frameclass
class TDR(TDRL):
    "Release date (iTunes extension)"
    _nonstandard = True

@frameclass
class WFED(URLFrame): 
    "iTunes: Podcast feed URL"
    _nonstandard = True
@frameclass
class WFD(WFED): pass

@frameclass
class TCAT(TextFrame): 
    "iTunes: Podcast category"
    _nonstandard = True
@frameclass
class TCT(TCAT): pass

@frameclass
class TKWD(TextFrame): 
    """iTunes: Podcast keywords
    Comma-separated list of keywords.
    """
    _nonstandard = True
@frameclass
class TKW(TKWD): pass

@frameclass
class PCST(Frame):
    """iTunes: Podcast flag.

    If this frame is present, iTunes considers the file to be a podcast.
    Value should be zero.
    """
    _framespec = (IntegerSpec("value", 32),)
    _nonstandard = True
@frameclass
class PCS(PCST): pass

@frameclass
class TST(TSOT):
    _nonstandard = True

@frameclass
class TSA(TSOA):
    _nonstandard = True

@frameclass
class TSP(TSOP):
    _nonstandard = True

@frameclass
class TSO2(TextFrame):
    """iTunes: Album Artist sort order"""
    _nonstandard = True
@frameclass
class TS2(TSO2): pass

@frameclass
class TSOC(TextFrame):
    """iTunes: Sort Composer"""
    _nonstandard = True
@frameclass
class TSC(TSOC): pass

@frameclass
class NCON(Frame):
    """MusicMatch data"""
    _framespec = (BinaryDataSpec("data"),)
    _nonstandard = True

@frameclass
class RGAD(Frame):
    """Replay Gain Adjustment"""
    # http://replaygain.hydrogenaudio.org/file_format_id3v2.html
    _framespec = (IntegerSpec("peak", 32), 
                  IntegerSpec("radio", 16), 
                  IntegerSpec("audiophile", 16))
    _nonstandard = True

@frameclass
class TTSE(TextFrame):
    """Lame encoder command line"""
    _nonstandard = True

@frameclass
class XSOP(TextFrame):
    """MusicBrainz Artist Sortname"""
    _nonstandard = True
    _version = 3

# ID3v1 genre list
genres = (
    "Blues", "Classic Rock", "Country", "Dance", "Disco", "Funk", "Grunge",
    "Hip-Hop", "Jazz", "Metal", "New Age", "Oldies", "Other", "Pop", "R&B",
    "Rap", "Reggae", "Rock", "Techno", "Industrial", "Alternative", "Ska",
    "Death Metal", "Pranks", "Soundtrack", "Euro-Techno", "Ambient",
    "Trip-Hop", "Vocal", "Jazz+Funk", "Fusion", "Trance", "Classical",
    "Instrumental", "Acid", "House", "Game", "Sound Clip","Gospel", "Noise",
    "AlternRock", "Bass", "Soul", "Punk", "Space", "Meditative",
    "Instrumental Pop", "Instrumental Rock", "Ethnic", "Gothic", "Darkwave",
    "Techno-Industrial", "Electronic", "Pop-Folk", "Eurodance", "Dream",
    "Southern Rock", "Comedy", "Cult", "Gangsta", "Top 40", "Christian Rap",
    "Pop/Funk", "Jungle", "Native American", "Cabaret", "New Wave",
    "Psychadelic", "Rave", "Showtunes", "Trailer", "Lo-Fi", "Tribal",
    "Acid Punk", "Acid Jazz", "Polka", "Retro", "Musical", "Rock & Roll",
    "Hard Rock",
    # 80-125: Winamp extensions (Booty Bass?)
    "Folk", "Folk-Rock", "National Folk", "Swing", "Fast Fusion", "Bebob",
    "Latin", "Revival", "Celtic", "Bluegrass", "Avantgarde", "Gothic Rock",
    "Progressive Rock", "Psychedelic Rock", "Symphonic Rock", "Slow Rock",
    "Big Band", "Chorus", "Easy Listening", "Acoustic", "Humour", "Speech",
    "Chanson", "Opera", "Chamber Music", "Sonata", "Symphony", "Booty Bass",
    "Primus", "Porn Groove", "Satire", "Slow Jam", "Club", "Tango", "Samba",
    "Folklore", "Ballad", "Power Ballad", "Rhythmic Soul", "Freestyle",
    "Duet", "Punk Rock", "Drum Solo", "A capella", "Euro-House",
    "Dance Hall",
    # 126-147: Even more esoteric Winamp extensions
    #
    # Note that there are conflicting interpretations for two genre ids:
    #
    #      136  "Christian"    vs. "Christian Gangsta Rap"
    #      140  "Contemporary" vs. "Contemporary Christian"
    #
    # The ones on the left come from the 2003 ID3v1 test suite by Martin Nilsson.
    # http://www.id3.org/Developer_Information?action=AttachFile&do=get&target=id3v1_test_suite.tar.gz
    #
    # The ones on the right are used by TagLib, Mutagen and most other ID3v1 implementations.
    #
    # Nilsson's list is slightly less insane, but we are stuck with
    # "Christian Gangsta Rap".
    #
    "Goa", "Drum & Bass", "Club-House", "Hardcore", "Terror", "Indie",
    "BritPop", "Negerpunk", "Polsk Punk", "Beat", "Christian Gangsta Rap",
    "Heavy Metal", "Black Metal", "Crossover", "Contemporary Christian",
    "Christian Rock", "Merengue", "Salsa", "Thrash Metal", "Anime", "JPop",
    "Synthpop")

__all__ = [ obj.__name__ for obj in globals().values() 
            if is_frame_class(obj)]

tags.Tag.frame_order = tags.FrameOrder(TIT2, TPE1, TALB, TRCK, TPOS, TCOM,
                                       TDRC, TYER, TRDA, TDAT, TIME,
                                       "T.*", COMM, "W*", TXXX, WXXX,
                                       UFID, PCNT, POPM,
                                       APIC, PIC, GEOB, PRIV,
                                       ".*")
