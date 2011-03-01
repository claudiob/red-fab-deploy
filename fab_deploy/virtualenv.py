from fabric.api import *

from fab_deploy.utils import run_as

def pip(commands=''):
	""" Runs pip command """
   	run('pip '+ commands)

def pip_install(what='requirements', options=''):
	""" Installs pip requirements listed in ``deploy/<file>.txt`` file. """
	run('pip install %s -r deploy/%s.txt' % (options,what))

def pip_update(what='requirements', options=''):
	""" Updates pip requirements listed in ``deploy/<file>.txt`` file. """
   	run('pip install %s -U -r deploy/%s.txt' % (options,what))

def virtualenv_create(site_packages=True):
	""" 
	Create a virtual environment in the env/ directory
	"""
	if site_packages:
		run('virtualenv env/')
	else:
		run('virtualenv --no-site-packages env/')
	run('ln -s env/bin/activate')

def virtualenv():
	"""
	Context manager. Use it to perform actions inside virtualenv::

		with virtualenv(tagname):
			# virtualenv is active here
	
	"""
	print('source env/bin/activate')
	return prefix('source env/bin/activate')

