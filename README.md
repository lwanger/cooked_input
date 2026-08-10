<!--
Keep this file in sync with README.rst.

README.rst is the canonical copy: pyproject.toml ships it to PyPI as the long
description. This Markdown copy exists because GitHub renders README.md in
preference to README.rst, so it is what visitors to the repository see. Any change
to one belongs in the other, and the "tested through Python X.Y" line below must
also match README.rst, docs/README.rst and the classifiers in pyproject.toml.
-->

[![PyPi Version](https://img.shields.io/pypi/v/cooked_input.svg)](https://pypi.org/project/cooked_input/)
[![License](https://img.shields.io/pypi/l/cooked_input.svg)](https://pypi.org/project/cooked_input/)
[![Documentation Status](https://readthedocs.org/projects/cooked-input/badge/?version=latest)](https://cooked-input.readthedocs.io/en/latest/)
[![Tests](https://github.com/lwanger/cooked_input/actions/workflows/tests.yml/badge.svg)](https://github.com/lwanger/cooked_input/actions/workflows/tests.yml)
[![PyPi pyversions](https://img.shields.io/pypi/pyversions/cooked_input.svg)](https://pypi.org/project/cooked_input/)

# Cooked Input Project

`cooked_input` is a Python package for getting, cleaning, converting, and validating input.
If you think of input (raw_input in legacy Python) as raw input, then this is cooked input.

`cooked_input` provides a simple and safe way to get validated command line input that ranges from the simplest
of Python programs to sophisticated database driven applications. Beginner's can use the provided convenience classes
to get simple inputs from the user. Following the [quick start guide](http://cooked-input.readthedocs.io/en/latest/quick_start.html)
you can be up and running in minutes.

More advanced users can easily create custom classes for sophisticated cleaning and validation. `Cooked_input` can
also be used to create menus and data tables. The latter tutorials
([part one](http://cooked-input.readthedocs.io/en/latest/tutorial.html) and
[part two](http://cooked-input.readthedocs.io/en/latest/tutorial2.html)) and examples show several examples ranging from
simple to sophisticated calls.

`Cooked_input` also provides a pathway to use the same cleaning and validation logic used in the command line
for validating web or GUI based inputs.

## Documentation

The documentation is available at: http://cooked-input.readthedocs.io/en/latest/

## Python Support

cooked_input requires Python 3.10 or later, and has been tested through Python 3.14.
Python 2 is no longer supported (the last release supporting it is v0.5.4).

## Installation

```
pip install cooked_input
```

## Project Page

Project information and source code is available at: https://github.com/lwanger/cooked_input

## Tutorial

The best way to get started is to read the quick start at: http://cooked-input.readthedocs.io/en/latest/quick_start.html

After that, more advanced usage can be learned from the tutorial at: http://cooked-input.readthedocs.io/en/latest/tutorial.html
