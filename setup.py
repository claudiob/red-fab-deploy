#!/usr/bin/env python
from distutils.core import setup

for cmd in ('egg_info', 'develop', 'upload_sphinx', 'build_sphinx'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

version='0.5'

setup(
    name='red-fab-deploy',
    version=version,
    author='FF0000 Geeks',
    author_email='ff0000geeks@ff0000.com',

    packages=['fab_deploy', 'fab_deploy.vcs'],
    package_data={
        'fab_deploy': [
            'config_templates/*.config',
            'config_templates/*.py',
            'config_templates/hgrc',
            'example_reqs/*.txt',
        ]
    },

    scripts = ['bin/red-fab-deploy'],

    url='http://www.github.com/ff0000/red-fab-deploy/',
    download_url = 'http://www.github.com/ff0000/red-fab-deploy/get/tip.zip',
    license = 'MIT license',
    description = """ Django deployment tool """,

    long_description = open('README.rst').read(),
    requires = ['Fabric', 'jinja2'],

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
