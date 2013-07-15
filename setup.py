#! /usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
import flask_assets_compile

setup(
    name='Flask-assets-compile',
    version=flask_assets_compile.__version__,
    url='https://bitbucket.org/anjianshi/flask-assets-compile',
    license='MIT',
    author='anjianshi',
    author_email='anjianshi@gmail.com',
    description='Flask 资源自动编译插件',
    py_modules=['flask_assets_compile'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask>=0.8'],
    keywords=['flask', 'assets', 'python'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)