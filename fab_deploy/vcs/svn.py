from fabric.api import *
from fab_deploy.utils import upload_config_template

def _get_username_password():
	username = prompt('What is your svn username:')
	password = prompt('What is your svn password:')
	return username, password

def init():
	pass

def up(tagname):
	""" Update the code to the latest revision """
	username, password = _get_username_password()
	run('svn up %s/%s --username %s --password %s ' % (
		env.conf['SRC_DIR'], tagname,
		username, password))

def push(tagname):
	""" Check out the code to the remote repo """
	username, password = _get_username_password()
	run('svn co %s/tags/%s %s --username %s --password %s ' % (
		env.conf['REPO'], tagname , env.conf['SRC_DIR'],
		username, password))

def export(tagname):
	""" Export the repo with tagname to /tmp/<tagname> """
	username, password = _get_username_password()
	local('mkdir -p /tmp/%s' % tagname)
	local('svn export %s/tags/%s /tmp/%s --username %s --password %s ' % (
		env.conf['REPO'], tagname, tagname,
		username, password))
	
def configure():
	""" Configure the repo """
	pass

