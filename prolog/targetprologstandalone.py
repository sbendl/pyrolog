"""
A simple standalone target for the prolog interpreter.
"""

import sys
from prolog.interpreter.translatedmain import repl, execute

# __________  Entry point  __________

from prolog.interpreter.continuation import Engine
from prolog.interpreter import term
e = Engine()
engine.DEBUG = False
term.DEBUG = False

def entry_point(argv):
    #from pypy.jit.codegen.hlinfo import highleveljitinfo
    #if highleveljitinfo.sys_executable is None:
    #    highleveljitinfo.sys_executable = argv[0]
    if len(argv) == 2:
        execute(e, argv[1])
    try:
        repl(e)
    except SystemExit:
        return 1
    return 0

# _____ Define and setup target ___

# XXX this should suggest --stackless somehow

def target(driver, args):
    driver.exe_name = 'pyrolog-%(backend)s'
    return entry_point, None

def portal(driver):
    from prolog.interpreter.portal import get_portal
    return get_portal(driver)

if __name__ == '__main__':
    entry_point(sys.argv)
