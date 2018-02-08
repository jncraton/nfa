NFA
===

[![Build Status](https://travis-ci.org/jncraton/nfa.svg?branch=master)](https://travis-ci.org/jncraton/nfa)

A Python 3 NFA implementation.

Getting Started
---------------

This assumes that you already have a basic environment setup with Python 3 and make available. Consult your documentation for your operating systems for more information. On Debian based systems, this should just be `sudo apt install build-essential python3`.

First, install package dependencies using pip (or pip3 depending on your environment):

`pip install -r requirements.txt`

Now, you can play around with the package using a Python REPL:

```python
~/nfa> python3
Python 3.x.x
GCC on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from nfa import NFA
>>> n = NFA.from_re('ab')
>>> n.accept('ab')
True
>>> n.accept('a')
False
>>> n.accept('abc')
False
>>> 
```
