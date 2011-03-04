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
