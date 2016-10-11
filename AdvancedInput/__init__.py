#!/usr/bin/env python3.3
# -*- coding: utf8 -*-
#
# Wrapper for python's input or raw_input function. Allows the usage of
#  the arrow keys and history
#
# Copyright (c) 2016	NorthernSec
# Copyright (c)	2016	Pieter-Jan Moreels
# This software is licensed under the Original BSD License

# Imports
import sys,tty,termios,string,shutil,re

class AdvancedInput():
  def __init__(self):
    self.history = []
    self.controlChars = dict.fromkeys(range(32))


  def _getCh(self):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


  def _print_buffer(self, _buffer, index=0, cursor=None):
    cursor = cursor if cursor else ""
    sys.stdout.write('\r' + ' '*(shutil.get_terminal_size().columns) + '\r',)
    _printable = _buffer.translate(self.controlChars)
    COLORS = re.compile("\\033\[.{1,2}m")
    _cursor = cursor
    for _color in set([x.group() for x in COLORS.finditer(_cursor)]):
      _cursor=_cursor.replace(_color, "")
    _cursor    = _cursor.translate(self.controlChars)
    sys.stdout.write('\r'+cursor + _printable+"\r"+"\x1b[C"*(index+len(_cursor)))
    sys.stdout.flush()


  def input(self, cursor=None):
    _buffer = ""          # Buffer var
    _buffer_right = ""    # Var for manipulating the buffer with left & right arrow
    _history_index = 0    # For scrolling through the history
    _history_buffer = ""  # Back up buffer while scrolling through history
    self._print_buffer("", cursor=cursor) # Print cursor
    while not _buffer.endswith("\r"):
      while True:
        k=self._getCh()
        if k!='': break
      # Check backspace
      if   k == "\x7F": _buffer = _buffer[:-1]
      elif k == "\x04": raise EOFError
      elif k == "\x03": raise KeyboardInterrupt
      else: _buffer+=k

      # Delete button pressed
      if    _buffer [-4:] == '\x1b[3~':
        _buffer = _buffer[:-4]
        if len(_buffer_right) is not 0: _buffer_right = _buffer_right[1:]
      # Check if any of the arrow keys are pressed
      elif  _buffer[-3:] in ['\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D']:
        arrow = _buffer[-3:]
        _buffer = _buffer[:-3]
        if   arrow=='\x1b[A': # UP
          if _history_index < len(self.history):
            if _history_index == 0: # Store buffer if not in history yet
              _history_buffer = _buffer+_buffer_right
            _buffer_right = ""
            _history_index += 1
            _buffer = self.history[-_history_index]
        elif arrow=='\x1b[B': # DOWN
          if _history_index > 0:
            _history_index -= 1
            _buffer_right = ""
            if _history_index == 0: # Restore buffer
              _buffer = _history_buffer
            else:
              _buffer = self.history[-_history_index]
        elif arrow=='\x1b[C': # Right
          if len(_buffer_right) is not 0:
            _buffer = _buffer+_buffer_right[0]
            _buffer_right = _buffer_right[1:]
        elif arrow=='\x1b[D': # Left
          _buffer_right = _buffer[-1:]+_buffer_right
          _buffer = _buffer[:-1]
      # Print buffer the clean way
      self._print_buffer(_buffer+_buffer_right, index=len(_buffer), cursor=cursor)
    # Append to history & return
    _buffer = _buffer[:-1] # Strip off return char
    _buffer = _buffer + _buffer_right
    if _buffer: self.history.append(_buffer)
    # Clear line before returning
    sys.stdout.write("\n")
    #sys.stdout.write('\r'+' ' * (shutil.get_terminal_size().columns) + '\r',)
    return _buffer.translate(self.controlChars)
