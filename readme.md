NFA
===

[![Build Status](https://travis-ci.org/jncraton/nfa.svg?branch=master)](https://travis-ci.org/jncraton/nfa)

A Python 3 NFA implementation.

Getting Started
---------------

This assumes that you already have a basic environment with [Python 3](https://www.python.org/) and [make](https://www.gnu.org/software/make/) available. Consult the documentation for these applications if you need to install them. On Debian based systems, this should just be `sudo apt install build-essential python3`.

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

Testing
-------

This package contains many inline doctests for both individual methods and package-level behaviors. The test suite can be run as `python3 -m doctest nfa/nfa.py` or more simply:

```
make test
```

If you'd like more detail on individual tests that are executed you may run:

```
make test-verbose
```

These tests are all run automatically by Travis, and you can see the results [here](https://travis-ci.org/jncraton/nfa).

I've included a basic limited email validator as part of the package. It includes and passes the following doctests:

```python
>>> ev = NFA.email_validator()
>>> ev.accept('abc@dsu.edu')
True
>>> ev.accept('abc@pluto.dsu.edu')
True
>>> ev.accept('11@123.com')
True
>>> ev.accept('a.b.ab')
False
>>> ev.accept('ab@ab')
False
>>> ev.accept('ab@ab.abcd')
False
```

Homework
--------

This package is part of a homework assignment. The completed homework is available directly [here](https://rawgit.com/jncraton/nfa/master/hw1.html).


