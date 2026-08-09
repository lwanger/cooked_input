@echo off
REM Editable install. Replaces the old "python setup.py develop", which no
REM longer works now that packaging is defined by pyproject.toml.
pip install -e .[test]