import fabric.api
import fabric.colors

from fab_deploy.file import link

def virtualenv_create(site_packages=True):
	""" 
	Create a virtual environment in the env/ directory
	"""
	if site_packages:
		fabric.api.run('virtualenv env/')
	else:
		fabric.api.run('virtualenv --no-site-packages env/')
	link('env/bin/activate',do_unlink=True,silent=True)

def virtualenv():
	"""
	Context manager. Use it to perform actions inside virtualenv::

		with virtualenv():
			# virtualenv is active here
	
	"""
	fabric.api.puts(fabric.colors.green('source env/bin/activate'))
	return fabric.api.prefix('source env/bin/activate')

def pip(commands=''):
	""" Runs pip command """
	with fabric.api.cd('/srv/active/'):
		with virtualenv():
   			fabric.api.run('pip %s' % commands)

def pip_install(what='requirements', options=''):
	""" Installs pip requirements listed in ``deploy/<file>.txt`` file. """
	pip(commands='install %s -r deploy/%s.txt' % (options,what))

def pip_update(what='requirements', options=''):
	""" Updates pip requirements listed in ``deploy/<file>.txt`` file. """
   	pip(commands='install %s -U -r deploy/%s.txt' % (options,what))

