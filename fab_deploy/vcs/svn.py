import os.path

import fabric.api

def init():
	pass

def up(tagname,local=False):
	""" Update the code to the latest revision """
	if local:
		command = 'svn up %s' % (tagname)
		fabric.api.local(command)
	else:
		command = 'svn up %s' % (os.path.join(fabric.api.env.conf['SRC_DIR'], tagname))
		fabric.api.run(command)

def push(tagname,local=False):
	""" Check out the code to the remote repo """
	if tagname == 'trunk':
		dirname = os.path.join(fabric.api.env.conf['REPO'],tagname)
	else:
		dirname = os.path.join(fabric.api.env.conf['REPO'],fabric.api.env.conf['VCS_TAGS'],tagname)
	if local:
		command = 'svn co %s %s' % (dirname, tagname)
		fabric.api.local(command)
	else:
		command = 'svn co %s %s' % (dirname, os.path.join(fabric.api.env.conf['SRC_DIR'],tagname))
		fabric.api.run(command)

def export(tagname,local=False):
	""" Export the repo with tagname to /tmp/<tagname> """
	if tagname == 'trunk':
		dirname = os.path.join(fabric.api.env.conf['REPO'],tagname)
	else:
		dirname = os.path.join(fabric.api.env.conf['REPO'],fabric.api.env.conf['VCS_TAGS'],tagname)
	if local:
		command = 'svn export %s %s' % (dirname, tagname)
		fabric.api.local(command)
	else:
		command = 'svn export %s %s' % (dirname, os.path.join(fabric.api.env.conf['SRC_DIR'],tagname))
		fabric.api.run(command)
	
def configure():
	""" Configure the repo """
	pass

