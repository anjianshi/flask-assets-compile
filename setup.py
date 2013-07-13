#! /usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
import assets_compiler

setup(
    name='flask-assets-compiler',
    version=assets_compiler.__version__,
    description='Flask 资源自动编译插件',
    license='License :: OSI Approved :: MIT License',
    platforms='Platform Independent',
    author='anjianshi',
    author_email='anjianshi@gmail.com',
    url='https://bitbucket.org/anjianshi/flask-assets-compiler',
    packages=['assets_compiler'],
    keywords=['flask', 'assets', 'python', 'sdk'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)