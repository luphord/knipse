#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''knipse setup script.
'''

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = []

test_requirements = []

setup(
    author='luphord',
    author_email='luphord@protonmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='''CLI catalog manager for pix and gThumb''',
    entry_points={
        'console_scripts': [
            'knipse=knipse:main',
        ],
    },
    install_requires=requirements,
    license='MIT license',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='knipse',
    name='knipse',
    py_modules=['knipse'],
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/luphord/knipse',
    version='0.1.1',
    zip_safe=True,
)
