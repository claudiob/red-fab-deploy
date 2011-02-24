from fabric.api import *
from fab_deploy.utils import upload_config_template

BRANCH_OPTION = 'SVN_BRANCH'

def init():
	pass

def up():
	""" Update the code to the latest revision """
	username = prompt('What is your svn username:')
	password = prompt('What is your svn password:')
	run('svn up %s --username %s --password %s ' % (
		env.conf['SRC_DIR'],
		username, password))

def push():
	""" Check out the code to the local repo """
	username = prompt('What is your svn username:')
	password = prompt('What is your svn password:')
	run('svn co %s %s --username %s --password %s ' % (
		env.conf['REPO'], env.conf['SRC_DIR'],
		username, password))

def configure():
	""" Configure the repo """
	pass

def export():
	""" Export the repo """
	run('svn export %(repo)s %(dest)s' % env)

