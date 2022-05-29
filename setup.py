#!/usr/bin/env python

from distutils.core import setup

setup(
    name='mqtt2nec',
    version='1.0',
    description='Receive nec IR remote command to send to Arduino',
    author='Jules Robichaud-Gagnon',
    author_email='j.robichaudg@gmail.com',
    url='https://github.com/jrobichaud/mqtt2nec/',
    py_modules=['mqtt2nec'],
    install_requires=["paho-mqtt", "pyserial"],
)
