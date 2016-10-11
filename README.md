# AdvancedInput
AdvancedInput is a package to make a wrapper for python's `input` and
 `raw_input` functions. It adds the functionality to use the arrow keys.
 Left and right will move the cursor through the text. Up and down will
 browse the history.

## Usage
```
from AdvancedInput import AdvancedInput
_in = AdvancedInput()
x = _in.input("> ")
print(x)
```
