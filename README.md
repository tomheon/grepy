grepy
=====

Match regular expressions against logical units in python source
(e.g. function or class defs) instead of lines.

Examples
--------

To find all functions in a.py and b.py that contain both 'hello' and
goodbye in order in their bodies (perhaps on different lines):

    grepy.py -f 'hello.*goodbye' a.py b.py

To find all classes with a method called blah followed by another
called heh:

    grepy.py -c 'def blah\(.*def heh\(' a.py b.py

How it Works
------------

grepy.py uses the ast module to walk the python source code, and Armin
Ronacher's codegen.py to backwards-generate the source to match
against from the syntax tree.

Status / Bugs / Etc.
--------------------

This is very much a proof of concept.  I'll probably flesh it out a
bit as I see if / how it's useful.  Use at your own risk.
