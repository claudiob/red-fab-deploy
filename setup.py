#!/usr/bin/env python
from distutils.core import setup
import re

# From http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy
# If somebody wants to install the package via "pip install pdfserver" 
# all dependencies should be fulfilled during the install in setup.py. 
# But as the software is to be deployed on a server many users will probably 
# download and extract the source package and then created a virtualenv around 
# it using "pip install -r requirements.txt".
# As I found no simple solution to answer my needs, I extended setup.py to 
# parse the dependencies given in a requirements.txt file. The file is parsed 
# twice, first to extract all dependency names and then again for all URLs for
# packages not found on PyPI. What it doesn't do so far is parse the versioning
# information.
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
    name = "red-fab-deploy",
    packages = ['fab_deploy', 'fab_deploy.db', 'fab_deploy.server', 
        'fab_deploy.vcs'],
    version = "0.0.1",
    # requires => not used, see parse_requirements above
    install_requires = parse_requirements('requirements.txt'),
	dependency_links = parse_dependency_links('requirements.txt'),
    package_data={'fab_deploy': [ # hidden files required by the application
	    'cacert.pem', 'templates/.*rc', 'templates/.vim/*.vim',
        'templates/.vim/doc/*.doc', 'templates/.vim/plugin/*.vim', ]},
    description = "Code deployment tool",
    long_description = open('README.markdown').read(),
    author = 'RED Interactive Agency',
    author_email = 'geeks@ff0000.com',
    url = "https://github.com/ff0000/red-fab-deploy",
    download_url = "https://github.com/ff0000/red-fab-deploy",
    license = 'MIT license',
    keywords = ["django", "admin", "bdd", "tdd", "documentation", "lettuce"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
        ],

)

# To create the package: python setup.py register sdist upload
