#! /usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import flask_assets_compile

setup(
    name='Flask-assets-compile',
    version=flask_assets_compile.__version__,
    url='https://github.com/anjianshi/flask-assets-compile',
    license='MIT',
    author='anjianshi',
    author_email='anjianshi@gmail.com',
    description='Flask assets auto compile extension',
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