# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = '1.1.3'

setup(name='gaycore',
      version=VERSION,
      description="a tiny and smart cli player of gcore audio, based on Python package curses and mpg123 for Linux or Mac",
      long_description='gaycore listen player using cli enjoy it',
      keywords='python gcore gaycore cli terminal',
      author='yihong0618',
      author_email='zouzou0208@gmail.com',
      url='https://github.com/yihong0618/gaycore',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'requests', 'PyMySQL', 'SQLAlchemy'
      ],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Software Development :: Libraries",
      ],
      entry_points={
          'console_scripts': [
              'gaycore = gaycore.main:run'
          ], }
      )
