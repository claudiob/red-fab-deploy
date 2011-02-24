from fabric.api import *

from fab_deploy.apache import apache_touch_wsgi
from fab_deploy.utils import inside_project

@inside_project
def pip(commands=''):
    """ Runs pip command """
    run('pip '+ commands)

@inside_project
def pip_install(what='requirements', options='', restart=True):
    """ Installs pip requirements listed in ``deploy/<file>.txt`` file. """
    run('pip install %s -r deploy/%s.txt' % (options, what))
    if restart:
        apache_touch_wsgi()

@inside_project
def pip_update(what='requirements', options='', restart=True):
    """ Updates pip requirements listed in ``deploy/<file>.txt`` file. """
    run('pip install %s -U -r deploy/%s.txt' % (options, what))
    if restart:
        apache_touch_wsgi()

def virtualenv_create():
    run('mkdir -p %s' % env.conf['ENV_DIR'])
    run('mkdir -p %s' % env.conf['SRC_DIR'])
    with cd(env.conf['ENV_DIR']):
        run('virtualenv --no-site-packages %s' % env.conf['INSTANCE_NAME'])

