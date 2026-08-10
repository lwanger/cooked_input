
Cooked Input Project
====================

.. The :scale: option made docutils fetch each badge to measure it, which needs
   Pillow and warns on every build. Badges are already the right size, so it is gone.

.. image:: https://img.shields.io/pypi/v/cooked_input.svg
   :alt: PyPi Version
   :target: https://pypi.org/project/cooked_input/

.. image:: https://img.shields.io/pypi/dm/cooked_input.svg
   :alt: PyPi Monthly Downloads
   :target: https://pypi.org/project/cooked_input/

.. image:: https://img.shields.io/pypi/l/cooked_input.svg
   :alt: License
   :target: https://github.com/lwanger/cooked_input/blob/master/LICENSE

.. image:: https://readthedocs.org/projects/cooked-input/badge/?version=latest
   :alt: Documentation Status
   :target: https://cooked-input.readthedocs.io/en/latest/

.. image:: https://github.com/lwanger/cooked_input/actions/workflows/tests.yml/badge.svg
   :alt: Test status
   :target: https://github.com/lwanger/cooked_input/actions/workflows/tests.yml

.. image:: https://img.shields.io/pypi/pyversions/cooked-input.svg
   :alt: PyPi pyversions
   :target: https://pypi.org/project/cooked-input/


``cooked_input`` is a Python package for getting, cleaning, converting, and validating command
line input. If you think of input (raw_input in legacy Python) as raw input, then this is cooked
input.

``cooked_input`` provides a simple and safe way to get validated input that ranges from the simplest
of Python programs to complex command line applications using menus and tables. Beginner's can use the
provided convenience classes to get simple inputs from the user. Following the
`tutorial <http://cooked-input.readthedocs.io/en/latest/tutorial.html>`_ you can be up and running in
minutes. More advanced users can easily create custom classes for sophisticated cleaning and
validation of inputs.

More complicated command line application (CLI) input can take advantage of ``cooked_input``'s ability to create commands,
menus and data tables. The latter tutorials and examples show several examples of more advanced usage.

``Cooked_input`` also provides a pathway to use the same cleaning and validation logic used in the command line
for processing and validating web or GUI based inputs. This allows seamless transition from command line to GUI applications.


Documentation
-------------

Read the full documentation at readthedocs.org:

  - cooked_input documentation at: http://cooked-input.readthedocs.io/en/latest/

Python Support
--------------

  - Python 3.10 or later (tested through Python 3.14)
  - Python 2 is no longer supported (the last release supporting it is v0.5.4)

Installation
------------

From pypi::

  pip install cooked_input

Project Page
------------

Source code and other project information available at: https://github.com/lwanger/cooked_input


Tutorial
--------

The best way to get started is to read the quick start at: http://cooked-input.readthedocs.io/en/latest/quick_start.html

After that, more advanced usage can be learned from the tutorial at: http://cooked-input.readthedocs.io/en/latest/tutorial.html

Finally, part two of the tutorial can be found at: http://cooked-input.readthedocs.io/en/latest/tutorial2.html


Change log
----------

See the :doc:`CHANGELOG <CHANGELOG>` for a list of changes.
