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
	version = '0.0.1',
    author='RED Interactive Agency',
    author_email='geeks@ff0000.com',

    package_data={
        'fab_deploy': [
			'cacert.pem',
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
    requires = ['fabric', 'libcloud'],

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
