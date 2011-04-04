import fabric.api

from fab_deploy.db.mysql import mysql_dump
from fab_deploy.virtualenv import virtualenv

def manage(command, settings=''):
	""" Runs django management command.
	Example::

		fab manage:createsuperuser
	"""
	with fabric.api.cd('/srv/active/'):
		with virtualenv():
			cmd = 'cd project && python manage.py %s' % command
			if settings:
				cmd += ' --settings=%s' % settings
			fabric.api.run(cmd)

def syn(stage=''):
	""" Runs django management command.
	Example::

		fab syn:staging
	""" 
	with fabric.api.cd('/srv/active/project/'):
		with fabric.api.prefix('source ../env/bin/activate'):
			fabric.api.run('./syn %s' % stage)

def migrate(params='', do_backup=True):
	""" Runs migrate management command. Database backup is performed
	before migrations if ``do_backup=False`` is not passed. """
	if do_backup:
		backup_dir = '/srv/active/var/backups/before-migrate'
		fabric.api.run('mkdir -p %s' % backup_dir)
		mysql_dump(backup_dir)
	#TODO: This appears to require django-south
	#manage('migrate --noinput %s' % params)

def syncdb(params=''):
	""" Runs syncdb management command. """
	manage('syncdb --noinput %s' % params)

def compress(params=''):
	""" Runs synccompress management command. """

	#TODO: This appears to require django-synccompress
	with fabric.api.settings(warn_only=True):
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
	with fabric.api.settings(warn_only=True):
		fabric.api.run('./runtests.sh %s' % what)

