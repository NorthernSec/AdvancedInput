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
import sys,tty,termios,shutil,re

class AdvancedInput():
  def __init__(self):
    self.history = []
    self.controlChars = dict.fromkeys(range(32))


  def _print_buffer(self, _buffer, index=0, cursor=None):
    try:
      cursor = cursor if cursor else ""
      _printable = _buffer.translate(self.controlChars)
      COLORS = re.compile("\\033\[.{1,2}m")
      _cursor = cursor
      for _color in set([x.group() for x in COLORS.finditer(_cursor)]):
        _cursor=_cursor.replace(_color, "")
      _curslen    = len(_cursor.translate(self.controlChars))
      cols = shutil.get_terminal_size().columns
      if _curslen >= cols: raise(Exception("Cursor wrapping not supported yet"))
      _print = _printable
      if _curslen+len(_printable) >= cols:
        _print_len = cols - _curslen
        if index > _print_len - 1:   # start moving right
          if index > len(_printable) - _print_len: # last part reached
            _print = _printable[index-_print_len+1:index+1]
          else:                                    # keep scrolling
            _print = _printable[-_print_len+1:]
        else:                        # stay put
          _print = _printable[:_print_len]
      arrow = _curslen + min(index, len(_print))
      sys.stdout.write('\r' + ' '*(cols) + '\r',)
      sys.stdout.write('\r'+cursor + _print+"\r"+"\x1b[C"*arrow)
      sys.stdout.flush()
    except Exception as e:
      print(e)
      raise(e)


  def input(self, cursor=None, buffer=None, hooks=None):
    _buffer = buffer if buffer else ""  # Buffer var
    _buffer_right = ""    # Var for manipulating the buffer with left & right arrow
    _history_index = 0    # For scrolling through the history
    _history_buffer = ""  # Back up buffer while scrolling through history
    self._print_buffer(_buffer, len(_buffer), cursor=cursor) # Print cursor
    _hooks = hooks if hooks and type(hooks) is dict else {}
    while not _buffer.endswith("\r"):
      while True:
        k=_getCh()
        if k!='': break
      # Check backspace
      if   k == "\x7F": _buffer = _buffer[:-1]
      elif k == "\x04": raise EOFError
      elif k == "\x03": raise KeyboardInterrupt
      else: _buffer+=k

      # Check hooks
      found_hook = False
      for _h, _f in _hooks.items():
        if _buffer[-len(_h):] == _h:
          _buffer = _buffer[:-len(_h)]
          result = _f(buffer=_buffer, rbuffer=_buffer_right, key=_h)
          if result and result.get('buffer'):  _buffer = result.get('buffer')
          if result and result.get('rbuffer'): _buffer_right = result.get('rbuffer')
          if result and result.get('cursor'):
              cursor = result.get('cursor')
              self._print_buffer(_buffer, len(_buffer), cursor=cursor)
          found_hook = True
          break

      if not found_hook:
        # Delete button pressed
        if    _buffer [-4:] in ['\x1b[3~', '\x1b[5~', '\x1b[6~']:
          key = _buffer[:-4]
          _buffer = _buffer[:-4]
          if   key=='\x1b[3~': # Delete button
            if len(_buffer_right) is not 0: _buffer_right = _buffer_right[1:]
          if   key=='\x1b[5~': # Page-Up button
            pass
          if   key=='\x1b[6~': # Page-Up button
            pass
        # Check if any of the arrow keys are pressed
        elif  _buffer[-3:] in ['\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D',
                               '\x1b[H', '\x1b[F']:
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
          elif arrow=='\x1b[H': # Home
            _buffer_right = _buffer+_buffer_right
            _buffer = ""
          elif arrow=='\x1b[F': # End
            _buffer = _buffer+_buffer_right
            _buffer_right = ""

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


def _getCh():
  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  try:
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  return ch


def confirm(text=None, default=None):
  text = text if text and type(text) is str else ""
  accept =  ['Y', 'y']
  decline = ['N', 'n']
  if   default == None:  curs = "[y/n] "
  elif default == True:
    curs = "[Y/n] "; accept.append('\r')
  elif default == False:
    curs = "[y/N] "; decline.append('\r')
  else: raise(TypeError)
  sys.stdout.write(text+" "+curs)
  sys.stdout.flush()
  while True:
    k=_getCh()
    if k in accept+decline: break
  print() # New line
  return True if k in accept else False


# Easy to use wrapper if you don't want history
def get_input(cursor = None, buffer=None):
  return AdvancedInput().input(cursor, buffer)


def get_raw_input():
  buffer = ""
  while not buffer.endswith("\r"):
    buffer+=_getCh()
  return buffer[:-1]
