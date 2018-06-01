# This file is part of ranger, the console file manager.
# License: GNU GPL version 3, see the file "AUTHORS" for details.
# Author: David Barnett <davidbarnett2@gmail.com>, 2010

"""A library to help to convert ANSI codes to curses instructions."""

from __future__ import (absolute_import, division, print_function)

import re

from ranger.ext.widestring import WideString
from ranger.gui import color


# pylint: disable=invalid-name
ansi_re = re.compile('(\x1b' + r'\[\d*(?:;\d+)*?[a-zA-Z])')
codesplit_re = re.compile(r'38;5;(\d+);|48;5;(\d+);|(\d*);')
reset = '\x1b[0m'
# pylint: enable=invalid-name


def split_ansi_from_text(ansi_text):
    return ansi_re.split(ansi_text)

# For information on the ANSI codes see
# githttp://en.wikipedia.org/wiki/ANSI_escape_code

def parse_attr(code, fg, bg, attr):
  if code == 0:                        # reset colors and attributes
      fg, bg, attr = -1, -1, 0

  elif code == 1:                      # enable attribute
      attr |= color.bold
  elif code == 4:
      attr |= color.underline
  elif code == 5:
      attr |= color.blink
  elif code == 7:
      attr |= color.reverse
  elif code == 8:
      attr |= color.invisible

  elif code == 22:                     # disable attribute
      attr &= not color.bold
  elif code == 24:
      attr &= not color.underline
  elif code == 25:
      attr &= not color.blink
  elif code == 27:
      attr &= not color.reverse
  elif code == 28:
      attr &= not color.invisible

  elif code >= 30 and code <= 37:         # 8 ansi foreground and background colors
      fg = code - 30
  elif code == 39:
      fg = -1
  elif code >= 40 and code <= 47:
      bg = code - 40
  elif code == 49:
      bg = -1

  # 8 aixterm high intensity colors (light but not bold)
  elif code >= 90 and code <= 97:
      fg = code - 90 + 8
  elif code == 99:
      fg = -1
  elif code >= 100 and code <= 107:
      bg = code - 100 + 8
  elif code == 109:
      bg = -1
  return (fg, bg, attr)


def parse_indexed_color(code):
  return code


def parse_rgb(code):
  (r, g, b) = code
  return color.get_color_id(r, g, b)


def parse_color(code):
  if code[0] == 5:
    return parse_indexed_color(code[0])
  elif code[0] == 2:
    return parse_rgb(code[1:])
  else:
    print('unknown color colde {}'.format(code))
    return -1


def parse_ansi_code(code, fg, bg, attr):
  if code[0] == 38:
    fg = parse_color(code[1:])
  elif code[0] == 48:
    bg = parse_color(code[1:])
  else:
    (fg, bg, attr) = parse_attr(code[0], fg, bg, attr)

  return (fg, bg, attr)

def text_with_fg_bg_attr(ansi_text):  # pylint: disable=too-many-branches,too-many-statements
    fg, bg, attr = -1, -1, 0
    for chunk in split_ansi_from_text(ansi_text):
        if chunk and chunk[0] == '\x1b':
            if chunk[-1] != 'm':
                continue
            match = re.match(r'^.\[(.*).$', chunk)
            if not match:
                # XXX I have no test case to determine what should happen here
                continue
            attr_args = match.group(1)

            (fg, bg, attr) = parse_ansi_code(map(int, attr_args.split(';')), fg, bg, attr)

            yield (fg, bg, attr)

        else:
            yield chunk


def char_len(ansi_text):
    """Count the number of visible characters.

    >>> char_len("\x1b[0;30;40mX\x1b[0m")
    1
    >>> char_len("\x1b[0;30;40mXY\x1b[0m")
    2
    >>> char_len("\x1b[0;30;40mX\x1b[0mY")
    2
    >>> char_len("hello")
    5
    >>> char_len("")
    0
    """
    return len(WideString(ansi_re.sub('', ansi_text)))


def char_slice(ansi_text, start, length):
    """Slices a string with respect to ansi code sequences

    Acts as if the ansi codes aren't there, slices the text from the
    given start point to the given length and adds the codes back in.

    >>> test_string = "abcde\x1b[30mfoo\x1b[31mbar\x1b[0mnormal"
    >>> split_ansi_from_text(test_string)
    ['abcde', '\\x1b[30m', 'foo', '\\x1b[31m', 'bar', '\\x1b[0m', 'normal']
    >>> char_slice(test_string, 1, 3)
    'bcd'
    >>> char_slice(test_string, 5, 6)
    '\\x1b[30mfoo\\x1b[31mbar'
    >>> char_slice(test_string, 0, 8)
    'abcde\\x1b[30mfoo'
    >>> char_slice(test_string, 4, 4)
    'e\\x1b[30mfoo'
    >>> char_slice(test_string, 11, 100)
    '\\x1b[0mnormal'
    >>> char_slice(test_string, 9, 100)
    '\\x1b[31mar\\x1b[0mnormal'
    >>> char_slice(test_string, 9, 4)
    '\\x1b[31mar\\x1b[0mno'
    """
    chunks = []
    last_color = ""
    pos = old_pos = 0
    for i, chunk in enumerate(split_ansi_from_text(ansi_text)):
        if i % 2 == 1:
            last_color = chunk
            continue

        chunk = WideString(chunk)
        old_pos = pos
        pos += len(chunk)
        if pos <= start:
            pass  # seek
        elif old_pos < start and pos >= start:
            chunks.append(last_color)
            chunks.append(str(chunk[start - old_pos:start - old_pos + length]))
        elif pos > length + start:
            chunks.append(last_color)
            chunks.append(str(chunk[:start - old_pos + length]))
        else:
            chunks.append(last_color)
            chunks.append(str(chunk))
        if pos - start >= length:
            break
    return ''.join(chunks)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
