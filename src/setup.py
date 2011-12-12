# -*- coding: utf-8 -*-
#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
      name='ac_api_client',
      version='0.1',
      description='client lib for an activecollab api',
      author='Thomas Sittig',
      author_email='thomas.sittig@googlemail.com',
      url='https://github.com/thomassittig/PyActiveCollab-API-Client',
      packages=find_packages(),
      long_description="""
      """,
      classifiers=[
          "License :: MIT",
          "Programming Language :: Python",
          "Development Status :: 1 - Alpha",
          "Intended Audience :: Developers",
          "Topic :: Internet",
          ],
      keywords='networking eventlet nonblocking internet',
      license='MIT',
      install_requires=[
        'setuptools',
        ],
)

