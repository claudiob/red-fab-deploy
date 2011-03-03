from fabric.api import *
from fabric.colors import *

from fab_deploy.db.mysql import mysql_dump
from fab_deploy.virtualenv import virtualenv

def manage(command):
	""" Runs django management command.
	Example::

		fab manage:createsuperuser
	"""
	with cd('/srv/active/project/'):
		with virtualenv():
			run('python manage.py %s' % command)

def migrate(params='', do_backup=True):
	""" Runs migrate management command. Database backup is performed
	before migrations if ``do_backup=False`` is not passed. """
	if do_backup:
		backup_dir = '/srv/active/var/backups/before-migrate'
		run('mkdir -p %s' % backup_dir)
		mysql_dump(backup_dir)
	#TODO: This appears to require django-south
	#manage('migrate --noinput %s' % params)

def syncdb(params=''):
	""" Runs syncdb management command. """
	manage('syncdb --noinput %s' % params)

def compress(params=''):
	""" Runs synccompress management command. """

	#TODO: This appears to require django-synccompress
	with settings(warn_only=True):
		manage('synccompress %s' % params)

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
		run('./runtests.sh %s' % what)

