#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Match regular expressions in python source files, using python source
primitives (for example a function definition or class definition) as
the regexp boundaries instead of a line.

For example, if you wanted to find all functions in a.py and b.py that
called a function 'hello' and another function 'goodbye', perhaps on
different lines, you would use:

grepy.py -f 'hello.*goodbye' a.py b.py

This is proof-of-concept-y at this point.
"""

from ast import NodeVisitor, parse
from optparse import OptionParser
import re

import codegen


def _fmt_res(where, source):
    """
    Format a hit in the source.
    """
    return "---\n%s:\n\n%s\n---" % (where, source)


class GrepVisitor(NodeVisitor):
    """
    Base functionality for matching a regular expression in source.
    """

    def __init__(self, finder, results, where):
        """
        - `finder`: the regular expression to match against

        - `results`: a list to which to append any positive hits

        - `where`: a string indicating which unit of source the regexp
          was matched against (for example, 'Function')
        """
        self.finder = finder
        self.results = results
        self.where = where

    def grep_visit(self, node):
        """
        Transform node into source, and append a hit to results if the
        regexp matches the source.
        """
        source = codegen.to_source(node)
        if self.finder.search(source):
            self.results.append(_fmt_res(self.where,
                                         source))


class FunctionVisitor(GrepVisitor):
    """
    Matches regexps against functions.
    """

    def __init__(self, finder, results):
        """
        - `finder`: the regular expression to match against

        - `results`: a list to which to append any positive hits
        """
        super(FunctionVisitor, self).__init__(finder, results, 'Function')

    def visit_FunctionDef(self, node):
        """
        Match the regexp against the function in node.
        """
        self.grep_visit(node)


class ClassVisitor(GrepVisitor):
    """
    Matches regexps against classes.
    """

    def __init__(self, finder, results):
        """
        - `finder`: the regular expression to match against

        - `results`: a list to which to append any positive hits
        """
        super(ClassVisitor, self).__init__(finder, results, 'Class')

    def visit_ClassDef(self, node):
        """
        Match the regexp against the class in node.
        """
        self.grep_visit(node)


def main(regexp, files, to_search):
    """
    - `regexp`: the regular expression to match

    - `files`: list of files to attempt to match against

    - `to_search`: an array of 0 or more of ('function', 'class'),
      indicating which primitives to search.
    """
    finder = re.compile(regexp, re.DOTALL)
    visitor_types = {'function': FunctionVisitor,
                     'class': ClassVisitor}
    results = {}

    for f in files:
        results[f] = []
        with open(f, 'rb') as fil:
            body = fil.read()
            parsed = parse(body)
            visitors = [visitor_types[ts](finder,
                                          results[f]) for ts in to_search]
            for v in visitors:
                v.visit(parsed)

    for (f, rs) in results.items():
        if rs:
            print "**%s**" % f
            for r in rs:
                print r


if __name__ == '__main__':
    usage = "usage: %prog [options] regexp <file[s]>"
    parser = OptionParser(usage=usage)
    parser.add_option("-f",
                      "--function",
                      dest='search_function',
                      action="store_true",
                      help="Treat function as search unit")
    parser.add_option("-c",
                      "--class",
                      dest='search_class',
                      action="store_true",
                      help="Treat class as search unit")
    (options, args) = parser.parse_args()

    to_search = []
    if options.search_function:
        to_search.append('function')
    if options.search_class:
        to_search.append('class')

    regexp = args[0]
    files = args[1:]

    main(regexp, files, to_search)
