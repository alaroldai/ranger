# This file is part of ranger, the console file manager.
# License: GNU GPL version 3, see the file "AUTHORS" for details.

"""Contains abbreviations to curses color/attribute constants.

Multiple attributes can be combined with the | (or) operator, toggled
with ^ (xor) and checked for with & (and). Examples:

attr = bold | underline
attr |= reverse
bool(attr & reverse) # => True
attr ^= reverse
bool(attr & reverse) # => False
"""

from __future__ import (absolute_import, division, print_function)

import curses

DEFAULT_FOREGROUND = curses.COLOR_WHITE
DEFAULT_BACKGROUND = curses.COLOR_BLACK
COLOR_PAIRS = {10: 0}


def withattr(**kwargs):
  def decorator(f):
    for (k, v) in kwargs.items():
      setattr(f, k, v)
    return f
  return decorator


@withattr(NextColorIndex=0)
@withattr(Colors=None)
@withattr(PredefinedColorCount=24)
def get_color_id(r, g, b):
  if not get_color_id.Colors:
    get_color_id.Colors = {
        curses.color_content(color) : color
        for color in (black, blue, cyan, green, magenta, red, white, yellow)
    }

  colors = get_color_id.Colors
  predefined_color_count = get_color_id.PredefinedColorCount
  (r, g, b) = (int(1000 * (float(c) / 256.0)) for c in (r, g, b))

  if (r, g, b) not in colors.keys():
    if len(colors) + predefined_color_count >= curses.COLORS or not curses.can_change_color():
      return -1
    colid = get_color_id.NextColorIndex % (curses.COLORS - predefined_color_count) + predefined_color_count
    curses.init_color(colid, r, g, b)
    colors[(r, g, b)] = colid
    get_color_id.NextColorIndex += 1
  return colors[(r, g, b)]


def get_color(fg, bg):
    """Returns the curses color pair for the given fg/bg combination."""

    key = (fg, bg)
    if key not in COLOR_PAIRS:
        size = len(COLOR_PAIRS)
        try:
            curses.init_pair(size, fg, bg)
        except curses.error:
            # If curses.use_default_colors() failed during the initialization
            # of curses, then using -1 as fg or bg will fail as well, which
            # we need to handle with fallback-defaults:
            if fg == -1:  # -1 is the "default" color
                fg = DEFAULT_FOREGROUND
            if bg == -1:  # -1 is the "default" color
                bg = DEFAULT_BACKGROUND

            try:
                curses.init_pair(size, fg, bg)
            except curses.error:
                # If this fails too, colors are probably not supported
                pass
        COLOR_PAIRS[key] = size

    return COLOR_PAIRS[key]


# pylint: disable=invalid-name,bad-whitespace
black      = curses.COLOR_BLACK
blue       = curses.COLOR_BLUE
cyan       = curses.COLOR_CYAN
green      = curses.COLOR_GREEN
magenta    = curses.COLOR_MAGENTA
red        = curses.COLOR_RED
white      = curses.COLOR_WHITE
yellow     = curses.COLOR_YELLOW
default    = -1

normal     = curses.A_NORMAL
bold       = curses.A_BOLD
blink      = curses.A_BLINK
reverse    = curses.A_REVERSE
underline  = curses.A_UNDERLINE
invisible  = curses.A_INVIS

default_colors = (default, default, normal)
# pylint: enable=invalid-name,bad-whitespace
