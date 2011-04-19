import os

import fabric.api
import fabric.colors

from fab_deploy.file import link

def virtualenv_create(dir='/srv/active/',site_packages=True):
	""" 
	Create a virtual environment in the /<dir>/env/ directory
	"""
	if site_packages:
		fabric.api.run('virtualenv %s' % os.path.join(dir,'env/'))
	else:
		fabric.api.run('virtualenv --no-site-packages %s' % os.path.join(dir,'env/'))
	link('env/bin/activate',do_unlink=True,silent=True)

def virtualenv(dir='/srv/active/'):
	"""
	Context manager. Use it to perform actions inside virtualenv::

		with virtualenv():
			# virtualenv is active here
	
	"""
	fabric.api.puts(fabric.colors.green('source %s' % os.path.join(dir,'env/bin/activate')))
	return fabric.api.prefix('source %s' % os.path.join(dir,'env/bin/activate'))

def pip(dir='/srv/active/',commands=''):
	""" Runs pip command """
	with virtualenv(dir):
   		fabric.api.run('pip %s' % commands)

def pip_install(dir='/srv/active/',what='requirements', options=''):
	""" Installs pip requirements listed in ``deploy/<file>.txt`` file. """
	pip(dir,commands='install %s -r %s/deploy/%s.txt' % (options,dir,what))

def pip_update(dir='/srv/active/',what='requirements', options=''):
	""" Updates pip requirements listed in ``deploy/<file>.txt`` file. """
   	pip(dir,commands='install %s -U -r %s/deploy/%s.txt' % (options,dir,what))

