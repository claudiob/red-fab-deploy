from datetime import datetime

from fabric.api import *
from fabric.colors import *

from fab_deploy.package import package_install

def _postgresql_is_installed():
	with settings(hide('stderr'), warn_only=True):
		output = run('postgresql --version')
	return output.succeeded

def postgresql_install():
	""" Installs postgreSQL """
	if _postgresql_is_installed():
		warn(yellow('PostgreSQL is already installed.'))
		return

	package_install(['postgresql-client-common','postgresql-common'])
