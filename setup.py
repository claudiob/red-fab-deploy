#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'red-fab-deploy',
    packages=[
		'fab_deploy',
		'fab_deploy.db',
		'fab_deploy.server',
		'fab_deploy.vcs'
		],
	version = '0.0.1'
    author='FF0000 Geeks',
    author_email='ff0000geeks@ff0000.com',

    package_data={
        'fab_deploy': [
            'templates/.*',
            'templates/.vim/*.vim',
            'templates/.vim/doc/*.doc',
            'templates/.vim/plugin/*.vim',
        ]
    },

    url='http://www.github.com/ff0000/red-fab-deploy/',
    download_url = 'http://www.github.com/ff0000/red-fab-deploy/',

    license = 'MIT license',
    description = """ Code deployment tool """,

    long_description = open('README.rst').read(),
    requires = ['fabric', 'cuisine'],

    classifiers = (
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
