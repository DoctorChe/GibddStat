# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

includes = ['lxml', 'lxml._elementpath', 'lxml.etree', 'atexit']
zip_include_packages = ['lxml', 'lxml._elementpath', 'lxml.etree',
                        'collections', 'ctypes', 'email', 'encodings',
                        'html', 'http', 'importlib', 'pydoc_data',
                        'sortedcontainers', 'sqlite3', 'urllib', 'xml']

include_files = ['db', 'template', 'ui', 'last_values.ini',
                 'e:\WinPython-32bit-3.6.1.0Qt5\python-3.6.1\DLLs\sqlite3.dll']
excludes = ['logging', 'unittest', 'ssl']

options = {
    'build_exe': {
        'includes': includes,
        'zip_include_packages': zip_include_packages,
        'include_files': include_files,
        'excludes' : excludes,
    }
}

executables = [
    Executable('ElectroCalc.py', base=base)
]

setup(name='GibddStat',
      version='1.0',
      description='Парсер сайта статистики ГИБДД',
      options=options,
      executables=executables
      )
