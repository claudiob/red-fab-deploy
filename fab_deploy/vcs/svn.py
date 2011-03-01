from fabric.api import *

def _get_username_password():
	username = prompt('What is your svn username:')
	password = prompt('What is your svn password:')
	return username, password

def init():
	pass

def up(tagname):
	""" Update the code to the latest revision """
	run('svn up %s/%s --username %s --password %s ' % (
		env.conf['SRC_DIR'], tagname,))

def push(tagname):
	""" Check out the code to the remote repo """
	run('svn co %s/%s/%s %s/%s --username %s --password %s ' % (
		env.conf['REPO'],env.conf['VCS_TAGS'],tagname, 
		env.conf['SRC_DIR'],tagname,))

def export(tagname):
	""" Export the repo with tagname to /tmp/<tagname> """
	run('svn export %s/%s/%s %s/%s ' % (
		env.conf['REPO'],env.conf['VCS_TAGS'],tagname, 
		env.conf['SRC_DIR'],tagname,))
	
def configure():
	""" Configure the repo """
	pass

