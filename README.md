# Python Input Generator

### Record the user mouse and keyboard input and reproduce it.

------

## Install:
Append this in your `.bashrc`, `.profile` or `.bash_aliases` :

```bash
alias pig="<path>/python <path>/pig.py"

```

## Usage:
```bash
# Record your input and reproduce 1 time at the same speed.
pig

# .. 10 time at a faster speed.
pig 10 true
```

## Requires:
- Python 3^ (Tested with 3.8.2)
- Pynput (pip install pynput)