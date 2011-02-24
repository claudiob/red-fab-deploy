#coding: utf-8
from __future__ import with_statement
from fabric.api import *
from fab_deploy.mysql import mysqldump
from fab_deploy.utils import inside_project

@inside_project
def command_is_available(command):
	with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
		output = run('python manage.py help ' + command)
	return output.succeeded

@inside_project
def manage(command):
	""" Runs django management command.
	Example::

		fab manage:createsuperuser
	"""
	if not command_is_available(command):
		warn('Management command "%s" is not available' % command)
	else:
		run('python manage.py '+ command)

def migrate(params='', do_backup=True):
	""" Runs migrate management command. Database backup is performed
	before migrations if ``do_backup=False`` is not passed. """
	if do_backup:
		backup_dir = env.conf['ENV_DIR']+'/var/backups/before-migrate'
		run('mkdir -p '+ backup_dir)
		mysqldump(backup_dir)
	manage('migrate --noinput %s' % params)

def syncdb(params=''):
	""" Runs syncdb management command. """
	manage('syncdb --noinput %s' % params)

def compress(params=''):
	with settings(warn_only=True):
		manage('synccompress %s' % params)

@inside_project
def test(what=''):
	""" Runs 'runtests.sh' script from project root.
	Example runtests.sh content::

		#!/bin/sh

		default_tests='accounts forum firms blog'
		if [ $# -eq 0 ]
		then
			./manage.py test $default_tests --settings=test_settings
		else
			./manage.py test $* --settings=test_settings
		fi
	"""
	with settings(warn_only=True):
		run('./runtests.sh ' + what)

