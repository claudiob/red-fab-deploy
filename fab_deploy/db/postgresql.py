from datetime import datetime

from fabric.api import *
from fabric.colors import *

from fab_deploy.package import package_install
from fab_deploy.utils import run_as

def _postgresql_is_installed():
	with settings(hide('stderr'), warn_only=True):
		output = run('postgresql --version')
	return output.succeeded

@run_as('root')
def postgresql_install():
	""" Installs postgreSQL """
	if _postgresql_is_installed():
		warn(yellow('PostgreSQL is already installed.'))
		return

	package_install(['postgresql-client-common','postgresql-common'])
