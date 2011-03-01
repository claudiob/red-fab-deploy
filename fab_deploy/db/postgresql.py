from datetime import datetime
from fabric.api import *

from fab_deploy.utils import run_as
from fab_deploy.system import aptitude_install

def _postgresql_is_installed():
	with settings(hide('stderr'), warn_only=True):
		output = run('postgresql --version')
	return output.succeeded

@run_as('root')
def postgresql_install():
	""" Installs postgreSQL """
	if _postgresql_is_installed():
		warn('PostgreSQL is already installed.')
		return

	aptitude_install('postgresql-client-common postgresql-common')
