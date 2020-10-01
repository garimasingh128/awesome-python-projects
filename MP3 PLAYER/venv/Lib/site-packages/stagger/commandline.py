#
# commandline.py
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

import sys
import codecs
import locale
import warnings
import os
import textwrap
from optparse import OptionParser, OptionGroup

import stagger
import stagger.fileutil
from stagger.id3 import *

def create_parser():
    parser = OptionParser(usage="%prog [command] [options] file1.mp3 [file2.mp3...]",
                          version="%prog " + stagger.versionstr)

    # General options
    parser.add_option("-l", "--list", action="store_true", dest="list",
                      help="List known frame types and exit")

    parser.add_option("-f", "--frameid",
                      action="store_true", dest="frameid",
                      help="Print low-level frame ids instead of descriptive names")

    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      help="Suppress warning messages on stderr")

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Explain what is being done")
    parser.add_option("-n", "--no-act", 
                      action="store_false", dest="act", default=True,
                      help="Don't actually change any files; implies --verbose.")

    # Command group
    group = OptionGroup(parser, "Commands")
    group.add_option("-p", "--print", action="store_true", dest="print",
                     help="Print tag contents (default)")
    group.add_option("-d", "--delete", action="store_true", dest="delete",
                      help="Delete tags")

    group.add_option("-s", "--set", action="append", nargs=2, dest="set",
                     metavar="FRAME VALUE",
                     help="Set FRAME to VALUE")

    group.add_option("-r", "--remove", action="append", dest="remove",
                     metavar="FRAME",
                     help="Remove all instances of FRAME")

    parser.add_option_group(group)

    # Debug group
    group = OptionGroup(parser, "Debugging options")
    group.add_option("--dump",
                     action="store", dest="dump", metavar="FILE",
                     help="Dump raw binary tag from FILE to stdout")

    group.add_option("--load",
                     action="store", dest="load", metavar="FILE",
                     help="Load binary tag dump from stdin and apply to FILE")

    group.add_option("--stats",
                     action="store_true", dest="stats",
                     help="Print resource usage statistics before termination")
    parser.add_option_group(group)

    return parser

def print_stats():
    try:
        statfile = open("/proc/" + str(os.getpid()) + "/status", "r")
        print(statfile.read(), file=sys.stderr)
    except IOError:
        pass
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        print("utime={0}".format(usage.ru_utime), file=sys.stderr)
        print("stime={0}".format(usage.ru_stime), file=sys.stderr)
        print("maxrss={0}".format(usage.ru_maxrss), file=sys.stderr)
        print("ixrss={0}".format(usage.ru_ixrss), file=sys.stderr)
        print("page_faults={0}".format(usage.ru_majflt), file=sys.stderr)
        print("block_input={0}".format(usage.ru_inblock), file=sys.stderr)
        print("block_output={0}".format(usage.ru_oublock), file=sys.stderr)
    except (ImportError, AttributeError, ValueError):
        pass # Give up


def main():
    warnings.simplefilter("always", stagger.Warning)
    
    # Work around idiotical python encoding heuristics:
    # Use locale-specified encoding on both stdout and stderr,
    # regardless of whether they are ttys
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.buffer)
    sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr.buffer)
    
    parser = create_parser()
    (options, args) = parser.parse_args()
    
    if not options.act:
        options.verbose = True
    
    
    def check_cmds(parser, options):
        cmds = ("dump", "load", "delete", "print", "list", "set", "remove")
        num = sum(1 for cmd in cmds if getattr(options, cmd, False))
        if num > 1:
            parser.error("conflicting commands")
    
    check_cmds(parser, options)
    
    def verbose(*args, **kwargs):
        if options.verbose:
            print(*args, **kwargs)
    
    par = { "act": options.act, "verbose": options.verbose }
    
    try:
        if options.dump:
            sys.stdout.stream.write(stagger.util.get_raw_tag_data(options.dump))
    
        elif options.load:
            data = sys.stdin.buffer.read()
            if not data.startswith(b"ID3"):
                parser.error("invalid tag data")
                exit(1)
            stagger.util.set_raw_tag_data(options.load, data, **par)
    
        elif options.list:
            def wraplist(strings):
                return textwrap.fill(", ".join(strings), width=78,
                                     initial_indent="    ",
                                     subsequent_indent="    ")
            def print_frame_list(header, predicate):
                print(header)
                frameids = [frameid for (frameid, framecls)
                            in stagger.tags.Tag.known_frames.items()
                            if predicate(framecls) ]
                frameids.sort()
                print(wraplist(frameids))
                print()
            
            for version in [2, 3, 4]:
                complement = set((2, 3, 4))
                complement.remove(version)
                print_frame_list("ID3v2.{0}-only frame ids:".format(version),
                                 lambda framecls: framecls._in_version(version)
                                 and not framecls._in_version(*complement))
            print_frame_list("Frame ids in both v2.3 and v2.4:",
                             lambda framecls: framecls._in_version(3)
                             and framecls._in_version(4))
    
            print("Frame names (usable in all versions):")
            print(wraplist(stagger.tags.Tag._friendly_names))
    
        elif options.delete:
            for filename in args:
                with stagger.util.print_warnings(filename, options):
                    if options.act:
                        stagger.delete_tag(filename)
                    verbose("{0}: tag deleted".format(filename))
    
        elif options.set:
            for filename in args:
                with stagger.util.print_warnings(filename, options):
                    try:
                        stagger.util.set_frames(filename, dict(options.set), **par)
                        sys.stderr.flush()
                        sys.stdout.flush()
                    except (KeyError, ValueError) as e:
                        print(e.args[0], file=sys.stderr)
                        exit(1)
    
        elif options.remove:
            for filename in args:
                with stagger.util.print_warnings(filename, options):
                    stagger.util.remove_frames(filename, options.remove, **par)
                    sys.stderr.flush()
                    sys.stdout.flush()
    
        else: # print
            for filename in args:
                with stagger.util.print_warnings(filename, options):
                    tag = None
                    try:
                        tag = stagger.read_tag(filename)
                        print("{0}: ID3v2.{1} tag with {2} frames"
                              .format(filename, tag.version, len(tag)))
                        sys.stderr.flush()
                        sys.stdout.flush()
                    except stagger.NoTagError:
                        print(filename + ":error: No tag", file=sys.stderr)
                    except stagger.Error as e:
                        print(filename + ":error: " + ", ".join(e.args), 
                              file=sys.stderr)
                    except EOFError:
                        print(filename + ":error: End of file while reading tag")

                with stagger.util.print_warnings(filename, options):
                    if tag:
                        if options.frameid:
                            for frame in tag.frames():
                                print("   {0}".format(str(frame)))
                        else:
                            for name in tag._friendly_names:
                                val = getattr(tag, name.replace("-", "_"))
                                if val:
                                    print("{0:>18}: {1}".format(name.title(), val))
                        print()
                    sys.stderr.flush()
                    sys.stdout.flush()
    
    except IOError as e:
        print("{0}: {1}".format(e.filename, e.strerror), file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        exit(1)
    
    if options.stats:
        print_stats()
    
    exit(0)

if __name__ == '__main__':
    main()
