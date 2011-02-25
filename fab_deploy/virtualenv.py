from fabric.api import *

from fab_deploy.utils import inside_project, run_as

#@inside_project
@run_as('root')
def pip(commands=''):
    """ Runs pip command """
    run('pip '+ commands)

#@inside_project
@run_as('root')
def pip_install(what='requirements', options=''):
    """ Installs pip requirements listed in ``deploy/<file>.txt`` file. """
    run('pip install %s -r %s/deploy/%s.txt' % (options,env.conf['SRC_DIR'],what))

#@inside_project
@run_as('root')
def pip_update(what='requirements', options=''):
    """ Updates pip requirements listed in ``deploy/<file>.txt`` file. """
    run('pip install %s -U -r %s/deploy/%s.txt' % (options,env.conf['SRC_DIR'],what))

def virtualenv_create():
    run('mkdir -p %s' % env.conf['ENV_DIR'])
    run('mkdir -p %s' % env.conf['SRC_DIR'])
    with cd(env.conf['ENV_DIR']):
        run('virtualenv --no-site-packages %(INSTANCE_NAME)s' % env.conf)

