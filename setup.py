# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='ec2ssh',
    version='0.01',
    entry_points={'console_scripts': ['ec2ssh=ec2ssh.main:wrapped_main']},
    author='Aarni Koskela',
    author_email='akx@iki.fi',
    license='MIT',
    packages=['ec2ssh'],
)
