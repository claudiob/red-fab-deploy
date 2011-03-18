#!/usr/bin/env python
from distutils.core import setup
import re

"""
Some methods were grabbed from:
http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy

"""
def parse_requirements(file_name):
	requirements = []
	for line in open(file_name, 'r').read().split('\n'):
		if re.match(r'(\s*#)|(\s*$)', line):
			continue
		if re.match(r'\s*-e\s+', line):
			requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
		elif re.match(r'\s*-f\s+', line):
			pass
		else:
			requirements.append(line)
	
	return requirements

def parse_dependency_links(file_name):
	dependency_links = []
	for line in open(file_name, 'r').read().split('\n'):
		if re.match(r'\s*-[ef]\s+', line):
			dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
	
	return dependency_links

setup(
    name = 'red-fab-deploy',
    packages=[
		'fab_deploy',
		'fab_deploy.db',
		'fab_deploy.server',
		'fab_deploy.vcs'
		],
	version = 'v0.0.1',
    author='RED Interactive Agency',
    author_email='geeks@ff0000.com',

    package_data={
        'fab_deploy': [
			'cacert.pem',
            'templates/.*rc',
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
    install_requires = parse_requirements('requirements.txt'),#['fabric', 'apache-libcloud'],
	dependency_links = parse_dependency_links('requirements.txt'),

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
