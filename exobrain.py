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


class Conf(object):
    INDENT = "EXOBRAIN_INDENT", 4
    ROOT = "EXOBRAIN_ROOT", '~/exobrain'
    EDITOR = "EDITOR", 'vim'
    COLORS = "EXOBRAIN_COLORS", """
        list=38;5;37:list2=38;5;77:list3=38;5;227:list4=38;5;209
        number=38;5;210
        error=1;31
    """

    def __getattr__(self, attribute):
        # Lazily set the attribute by looking up the environment variable and
        # default value in self.ATTRIBUTE
        if hasattr(self, attribute.upper()):
            env_var, default = getattr(self, attribute.upper())
            value = type(default)(os.environ.get(env_var, default))
            setattr(self, attribute, value)
            return value
        raise AttributeError("Unknown attribute: " + attribute)


class Exobrain(object):
    def __init__(self):
        self.conf = Conf()
        args = self.parse_args()
        self.action = args.do
        self.note_name = args.note_name
        self.rootdir = os.path.expanduser(args.r)
        self.verbose = args.verbose
        self.prettify = Prettifier(self.conf)

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
            try:
                filename = self.find_note(self.note_name)
            except RuntimeError:
                print(self.prettify.clr("error", "Error: no such note"))
            else:
                self.show_note(filename)

    def show_note(self, filename):
        if os.access(filename, os.X_OK):
            import subprocess
            subprocess.call([filename])
        else:
            content = open(filename, 'r').read().rstrip("\n")
            print("\n".join(self.prettify(content, verbose=self.verbose)))

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

    def edit_file(self, filename):
        import subprocess
        subprocess.call([self.conf.editor, filename])

    def parse_args(self):
        import argparse
        parser = argparse.ArgumentParser(description='')
        action = parser.add_mutually_exclusive_group()
        parser.add_argument('note_name', nargs='?', default='default',
                            metavar="note name")
        action.add_argument('--help-syntax', action='store_const',
                            const="syntax", dest="do",
                            help="print information on the markup syntax")
        action.add_argument('-e', help='edit the given note',
                            action="store_const", const='edit', dest="do")
        parser.add_argument('-r', help='change the root directory',
                            type=str, metavar='directory',
                            default=self.conf.root)
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="display hidden lines")
        return parser.parse_args()


class Prettifier(object):
    def __init__(self, conf):
        self.conf = conf
        self._parsed_scheme = None

    def clr(self, tag, string):
        if not self._parsed_scheme:
            self._parsed_scheme = self.parse_colorscheme(self.conf.colors)
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

    def __call__(self, string, verbose=False):
        import re

        bullet = "\u25cf"
        for line in string.split("\n"):
            if not verbose and \
                    (line.startswith("|") or line.lstrip().startswith("x ")):
                continue

            def highlight_bullets(match):
                spaces = match.group(1)
                if len(spaces) > self.conf.indent * 2:
                    return spaces + self.clr("list4", bullet)
                elif len(spaces) > self.conf.indent * 1:
                    return spaces + self.clr("list3", bullet)
                elif len(spaces) > 0:
                    return spaces + self.clr("list2", bullet)
                else:
                    return spaces + self.clr("list", bullet)

            def highlight_numbers(match):
                return self.clr("number", match.group(1))

            line = re.sub(r"^(\s*)[*-0](?= )", highlight_bullets, line)
            line = re.sub(
                    r"([+-=]?(?:[0-9]\.?[0-9]*(e-?[0-9]+)?|0x[0-9A-Fa-f]+))",
                    highlight_numbers, line)
            yield line

if __name__ == '__main__':
    Exobrain().run()
