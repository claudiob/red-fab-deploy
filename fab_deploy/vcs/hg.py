from fabric.api import *
from fab_deploy.utils import upload_config_template

BRANCH_OPTION = 'HG_BRANCH'

def init():
    run('hg init')

def up(branch):
    run('hg up -C ' + branch)

def push():
    local('hg push ssh://%s/src/%s/' % (env.hosts[0], env.conf.INSTANCE_NAME))

def configure():
    upload_config_template('hgrc', env.conf['SRC_DIR'] + '/.hg/hgrc')
