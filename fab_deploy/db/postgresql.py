from datetime import datetime

import fabric.api

from fab_deploy.package import package_install

def _postgresql_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('postgresql --version')
	return output.succeeded

def postgresql_install():
	""" Installs postgreSQL """
	if _postgresql_is_installed():
		fabric.api.warn(fabric.colors.yellow('PostgreSQL is already installed.'))
		return

	package_install(['postgresql-client-common','postgresql-common'])

def postgresql_execute(sql, user='', password=''):
	"""
	Executes passed sql command using postgresql shell.
	"""
	return fabric.api.run("echo '%s' | psql -u%s -p%s" % (sql, user, password))

def postgresql_create_db():
	"""
	Create an empty postgresql database.
	"""
	database = fabric.api.runprompt('Please enter database name:')
	
	fabric.api.run("createdb %s" % (database))

def postgresql_create_user():
	"""
	Creates a new postgresql user.
	"""
	user     = fabric.api.runprompt('Please enter username:')
	new_user = fabric.api.runprompt('Please enter new username:')
	
	fabric.api.run("createuser %s -P -U %s" % (new_user, user))

def postgresql_drop_user():
	""" Drop a postgresql user """
	pass

def postgresql_dump():
	""" Runs postgresqldump. Result is stored at /srv/active/sql/ """
	dir = '/srv/active/sql/'
	pass

def postgresql_load():
	""" Load a postgresql database """
	pass

def postgresql_backup():
	""" Backup the database """
	pass

