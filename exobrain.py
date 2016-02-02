#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exobrain

      .__---~~~(~~-_.
   _-'  ) -~~- ) _-" )_
  (  ( `-,_..`.,_--_ '_,)_
 (  -_)  ( -_-~  -_ `,    )
 (_ -_ _-~-__-~`, ,' )__-'))--___--~~~--__--~~--___--__..
 _ ~`_-'( (____;--==,,_))))--___--~~~--__--~~--__----~~~'`=__-~+_-_.
(@)~(@)~~````      `-_(())_-~
"""

import os.path


LIST_INDENT = 4
DEFAULT_ROOT = '~/exobrain'
DEFAULT_EDITOR = 'vim'
DEFAULT_COLORS = """
    list=38;5;37
    list2=38;5;77
    list3=38;5;227
    list4=38;5;209
    number=38;5;210"""


class Exobrain(object):
    def __init__(self, args):
        self.action = args.do
        self.note_name = args.note_name
        self.rootdir = os.path.expanduser(args.r)
        self.prettify = Prettifier(
            os.environ.get("EXOBRAIN_COLORS", DEFAULT_COLORS))

    def run(self):
        if self.action == 'syntax':
            print("TODO")
        elif self.action == 'edit':
            try:
                filename = self.find_note(self.note_name)
            except RuntimeError:
                filename = os.path.join(self.rootdir, self.note_name)
            self.edit_file(filename)
        else:
            filename = self.find_note(self.note_name)
            self.show_note(filename)

    def show_note(self, filename):
        if os.access(filename, os.X_OK):
            import subprocess
            subprocess.call([filename])
        else:
            content = open(filename, 'r').read().rstrip("\n")
            print("\n".join(self.prettify(content)))

    def find_note(self, note_name):
        partial_match = None
        for root, _dirs, files in os.walk(self.rootdir):
            if not partial_match:
                for filename in files:
                    if note_name in filename:
                        partial_match = os.path.join(root, filename)
                        break
            if note_name in files:
                return os.path.join(root, note_name)
        if partial_match:
            return partial_match
        raise RuntimeError("Note not found")

    @staticmethod
    def edit_file(filename):
        import subprocess
        editor = os.environ.get("EDITOR", DEFAULT_EDITOR)
        subprocess.call([editor, filename])

    @staticmethod
    def parse_args():
        import argparse
        parser = argparse.ArgumentParser(description='')
        action = parser.add_mutually_exclusive_group()
        action.add_argument('-e', help='edit the given note',
                            action="store_const", const='edit', dest="do")
        action.add_argument('--help-syntax', action='store_const',
                            const="syntax", dest="do",
                            help="print information on the markup syntax")
        parser.add_argument('-r', help='change the root directory',
                            type=str, metavar='directory',
                            default=DEFAULT_ROOT)
        parser.add_argument('note_name', nargs='?', default='default',
                            metavar="note name")
        return parser.parse_args()


class Prettifier(object):
    def __init__(self, colorscheme):
        self.colorscheme = colorscheme
        self._parsed_scheme = None

    def clr(self, tag, string):
        if not self._parsed_scheme:
            self._parsed_scheme = self.parse_colorscheme(self.colorscheme)
        color = self._parsed_scheme.get(tag, "0")
        return "\033[%sm%s\033[0m" % (color, string)

    @staticmethod
    def parse_colorscheme(colorscheme):
        entries = colorscheme.replace("\n", ":").split(":")
        scheme = dict()
        for entry in entries:
            if "=" in entry:
                key, value = entry.split('=', 1)
                scheme[key.strip()] = value.strip()
        return scheme

    def __call__(self, string):
        import re

        bullet = "\u25cf"
        for line in string.split("\n"):
            def highlight_bullets(match):
                spaces = match.group(1)
                if len(spaces) > LIST_INDENT * 2:
                    return spaces + self.clr("list4", bullet)
                elif len(spaces) > LIST_INDENT * 1:
                    return spaces + self.clr("list3", bullet)
                elif len(spaces) > 0:
                    return spaces + self.clr("list2", bullet)
                else:
                    return spaces + self.clr("list", bullet)

            def highlight_numbers(match):
                return self.clr("number", match.group(1))

            line = re.sub(r"^(\s*)[*-0]", highlight_bullets, line)
            line = re.sub(
                    r"([+-=]?(?:[0-9]\.?[0-9]*(e-?[0-9]+)?|0x[0-9A-Fa-f]+))",
                    highlight_numbers, line)
            yield line

if __name__ == '__main__':
    Exobrain(Exobrain.parse_args()).run()
