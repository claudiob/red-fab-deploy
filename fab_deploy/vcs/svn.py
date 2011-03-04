import os.path

import fabric.api

def init():
	pass

def up(tagname):
	""" Update the code to the latest revision """
	fabric.api.run('svn up %s' % (
		os.path.join(fabric.api.env.conf['SRC_DIR'], tagname)))

def push(tagname):
	""" Check out the code to the remote repo """
	if tagname == 'trunk':
		dirname = os.path.join(fabric.api.env.conf['REPO'],tagname)
	else:
		dirname = os.path.join(fabric.api.env.conf['REPO'],fabric.api.env.conf['VCS_TAGS'],tagname)
	fabric.api.run('svn co %s %s' % (dirname,
		os.path.join(fabric.api.env.conf['SRC_DIR'],tagname)))

def export(tagname):
	""" Export the repo with tagname to /tmp/<tagname> """
	if tagname == 'trunk':
		dirname = os.path.join(fabric.api.env.conf['REPO'],tagname)
	else:
		dirname = os.path.join(fabric.api.env.conf['REPO'],fabric.api.env.conf['VCS_TAGS'],tagname)
	fabric.api.run('svn export %s %s' % (dirname,
		os.path.join(fabric.api.env.conf['SRC_DIR'],tagname)))
	
def configure():
	""" Configure the repo """
	pass

