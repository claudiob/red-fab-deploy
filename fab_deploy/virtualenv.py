from fabric.api import *

from fab_deploy.utils import run_as, virtualenv

def pip(commands=''):
    """ Runs pip command """
   	run('pip '+ commands)

def pip_install(what='requirements', options=''):
    """ Installs pip requirements listed in ``deploy/<file>.txt`` file. """
    run('pip install %s -r deploy/%s.txt' % (options,what))

def pip_update(what='requirements', options=''):
    """ Updates pip requirements listed in ``deploy/<file>.txt`` file. """
   	run('pip install %s -U -r deploy/%s.txt' % (options,what))

def virtualenv_create():
	""" 
	Create a virtual environment with no site packages in the
	current directory
	"""
    run('virtualenv --no-site-packages .')

