
.. Keep this file in sync with README.md.

   This file is the canonical copy: pyproject.toml ships it to PyPI as the long
   description. README.md exists because GitHub renders it in preference to this
   file, so it is what visitors to the repository see. Any change to one belongs in
   the other, and the "tested through Python X.Y" line below must also match
   README.md, docs/README.rst and the classifiers in pyproject.toml.

.. image:: https://img.shields.io/pypi/v/cooked_input.svg
    :target: https://pypi.org/project/cooked_input/

.. image:: https://img.shields.io/pypi/l/cooked_input.svg
    :target: https://pypi.org/project/cooked_input/

.. image:: https://readthedocs.org/projects/cooked-input/badge/?version=latest
    :target: https://cooked-input.readthedocs.io/en/latest/

.. image:: https://github.com/lwanger/cooked_input/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/lwanger/cooked_input/actions/workflows/tests.yml

.. image:: https://img.shields.io/pypi/pyversions/cooked_input.svg
    :target: https://pypi.org/project/cooked_input/



Cooked Input Project
====================

``cooked_input`` is a Python package for getting, cleaning, converting, and validating input.
If you think of input (raw_input in legacy Python) as raw input, then this is cooked input.

``cooked_input`` provides a simple and safe way to get validated command line input that ranges from the simplest
of Python programs to sophisticated database driven applications. Beginner's can use the provided convenience classes
to get simple inputs from the user. Following the `quick start guide <http://cooked-input.readthedocs.io/en/latest/quick_start.html>`_
you can be up and running in minutes.

More advanced users can easily create custom classes for sophisticated cleaning and validation. ``Cooked_input`` can
also be used to create menus and data tables. The latter tutorials (`part one <http://cooked-input.readthedocs.io/en/latest/tutorial.html>`_ and `part two <http://cooked-input.readthedocs.io/en/latest/tutorial2.html>`_) and examples show several examples ranging from
simple to sophisticated calls.

``Cooked_input`` also provides a pathway to use the same cleaning and validation logic used in the command line
for validating web or GUI based inputs.

Documentation
-------------

The documentation is available at: http://cooked-input.readthedocs.io/en/latest/


Python Support
--------------

cooked_input requires Python 3.10 or later, and has been tested through Python 3.14.
Python 2 is no longer supported (the last release supporting it is v0.5.4).


Release Notes
-------------

The next release is a large one by volume of change, even though it adds no new functionality.
Every function, method and class in the package was annotated with types, and the package now
ships a ``py.typed`` marker so downstream projects actually see them. Running the result through
``ty`` and Ruff -- both now part of CI -- meant reading essentially all of the code, and that
turned up a series of real defects that had been sitting behind an untyped signature. Those fixes
are the bulk of the release.

**There are breaking changes.** Most code will not notice, but they are worth a look before
upgrading:

* ``in_all``, ``in_any`` and ``not_in`` are no longer importable from ``cooked_input``. They were
  always internal plumbing and appeared in no documentation. ``validate()`` is unaffected.
* The module-level validation helpers, and ``SimpleValidator``, now return a real ``bool`` rather
  than passing a validator's truthy return value through.
* ``Table``, ``create_table`` and ``get_menu`` take their options as named keyword-only
  parameters instead of a ``**options`` dictionary. An unrecognised option now raises a
  ``TypeError`` rather than being silently ignored -- which is how a bug in one of the shipped
  examples had gone unnoticed. Code that builds an options dictionary still works by unpacking
  it: ``Table(rows, **options)``.
* ``Cleaner``, ``Convertor`` and ``Validator`` are now real abstract base classes. A subclass
  that never implemented ``__call__`` raises ``TypeError`` when instantiated, where before it
  silently returned **None** from every call.
* A single string given to ``AnyOfValidator`` or ``NoneOfValidator`` is now one choice rather
  than being iterated one character at a time.

See `CHANGELOG.rst <https://github.com/lwanger/cooked_input/blob/master/CHANGELOG.rst>`_ for the
full list, including the defects the type checker found and what each of them affected.


Installation
------------

::

  pip install cooked_input


Project Page
------------

Project information and source code is available at: https://github.com/lwanger/cooked_input


Tutorial
--------

The best way to get started is to read the quick start at: http://cooked-input.readthedocs.io/en/latest/quick_start.html

After that, more advanced usage can be learned from the tutorial at: http://cooked-input.readthedocs.io/en/latest/tutorial.html
