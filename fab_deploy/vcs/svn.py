from fabric.api import *
from fab_deploy.utils import upload_config_template

BRANCH_OPTION = 'SVN_BRANCH'

def init():
	pass

def up(branch):
	""" Update the code to the latest revision """
	run('svn up %s' % branch)

def push():
	""" Check out the code to the local repo """
	local('svn co ssh://%s/src/%s/' % (env.hosts[0], env.conf.INSTANCE_NAME))

def configure():
	""" Configure the repo """
	pass

def export():
	""" Export the repo """
	run('svn export %(repo)s %(dest)s' % env)

