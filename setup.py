#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
import teimed

setup(
    name='teimed',
    version=teimed.__version__,
    py_modules=['teimed'],
    packages=['teimed'],
    scripts=["teimdict.py",
             "teimedit.py",
             "teimlineword.py",
             "prjmgr.py",
             "teimspan.py",
             "teimxmllint.py",
             "teimxml.py",
             "ualog.py" ],
    author="Marta Materni",
    author_email="marta.materni@gmail.com",
    description="Tools per TEI",
    long_description=open('README.rst').read(),
    include_package_data=True,
    url='http://github.com/gmaterni/mmtei',
    license="new BSD License",
    install_requires=['lxml'],
    classifiers=['Development Status :: 1 - Planing',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: Italiano',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python 3.6.',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'],
    entry_points={
        'console_scripts': [
            'teimedinfo = teimed.info:list_modules',
        ],
    },
)
