#
# fileutil.py
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

"""File manipulation utilities."""

import io
import os.path
import shutil
import tempfile
import signal

from contextlib import contextmanager

def xread(file, length):
    "Read exactly length bytes from file; raise EOFError if file ends sooner."
    data = file.read(length)
    if len(data) != length:
        raise EOFError
    return data

@contextmanager
def opened(filename, mode):
    "Open filename, or do nothing if filename is already an open file object"
    if isinstance(filename, str):
        file = open(filename, mode)
        try: 
            yield file
        finally: 
            if not file.closed:
                file.close()
    else:
        yield filename

@contextmanager
def suppress_interrupt():
    """Suppress KeyboardInterrupt exceptions while the context is active.
    
    The suppressed interrupt (if any) is raised when the context is exited.
    """
    interrupted = False

    def sigint_handler(signum, frame):
        nonlocal interrupted
        interrupted = True
    
    s = signal.signal(signal.SIGINT, sigint_handler)
    try:
        yield None
    finally:
        signal.signal(signal.SIGINT, s)
    if interrupted:
        raise KeyboardInterrupt()

def replace_chunk(filename, offset, length, chunk, in_place=True, max_mem=5):
    """Replace length bytes of data with chunk, starting at offset.
    Any KeyboardInterrupts arriving while replace_chunk is runnning
    are deferred until the operation is complete.

    If in_place is true, the operation works directly on the original
    file; this is fast and works on files that are already open, but
    an error or interrupt may lead to corrupt file contents.  

    If in_place is false, the function prepares a copy first, then
    renames it back over the original file.  This method is slower,
    but it prevents corruption on systems with atomic renames (UNIX),
    and reduces the window of vulnerability elsewhere (Windows).

    If there is no need to move data that is not being replaced, then we use
    the direct method irrespective of in_place.  (In this case an interrupt
    may only corrupt the chunk being replaced.)
    """
    with suppress_interrupt():
        _replace_chunk(filename, offset, length, chunk, in_place, max_mem)

def _replace_chunk(filename, offset, length, chunk, in_place, max_mem):
    assert isinstance(filename, str) or in_place
    with opened(filename, "rb+") as file:
        # If the sizes match, we can simply overwrite the original data.
        if length == len(chunk):
            file.seek(offset)
            file.write(chunk)
            return

        oldsize = file.seek(0, 2)
        newsize = oldsize - length + len(chunk)

        # If the orig chunk is exactly at the end of the file, we can
        # simply truncate the file and then append the new chunk.
        if offset + length == oldsize:
            file.seek(offset)
            file.truncate()
            file.write(chunk)
            return

        if in_place:
            _replace_chunk_in_place(file, offset, length, chunk, oldsize, newsize)
        else: # not in_place
            temp = tempfile.NamedTemporaryFile(dir=os.path.dirname(filename),
                                               prefix="stagger-",
                                               suffix=".tmp",
                                               delete=False)
            try:
                file.seek(0)
                _copy_chunk(file, temp, offset)
                temp.write(chunk)
                file.seek(offset + length)
                _copy_chunk(file, temp, oldsize - offset - length)
            finally:
                temp.close()
                file.close()
            shutil.copymode(filename, temp.name)
            shutil.move(temp.name, filename)
            return


def _copy_chunk(src, dst, length):
    "Copy length bytes from file src to file dst."
    BUFSIZE = 128 * 1024
    while length > 0:
        l = min(BUFSIZE, length)
        buf = src.read(l)
        assert len(buf) == l
        dst.write(buf)
        length -= l

def _replace_chunk_in_place(file, offset, length, chunk, oldsize, newsize):
    if newsize > oldsize:
        file.seek(0, 2)
        file.write(b"\x00" * (len(chunk) - length))
    file.seek(0)
    try:
        import mmap
        m = mmap.mmap(file.fileno(), max(oldsize, newsize))
        try:
            m.move(offset + len(chunk), 
                   offset + length, 
                   oldsize - offset - length)
            m[offset:offset + len(chunk)] = chunk
        finally:
            m.close()
    except (ImportError, EnvironmentError, ValueError):
        # mmap didn't work.  Let's load the tail into a tempfile
        # and construct the result from there.
        file.seek(offset + length)
        temp = tempfile.SpooledTemporaryFile(
            max_size=max_mem * (1<<20),
            prefix="stagger-",
            suffix=".tmp")
        try:
            _copy_chunk(file, temp, oldsize - offset - length)
            file.seek(offset)
            file.truncate()
            file.write(chunk)
            temp.seek(0)
            _copy_chunk(temp, file, oldsize - offset - length)
        finally:
            temp.close()
        return
    else:
        # mmap did work, we just need to truncate any leftover parts
        # at the end
        file.truncate(newsize)
        return
