import fabric.api

def get_vcs():
	""" Returns a module with current VCS """
	name = fabric.api.env.conf['VCS']
	return __import__(name, fromlist=name.split('.')[1:])

def init():
	get_vcs().init()

def up(tagname):
	""" Runs vcs ``update`` command on server """
	get_vcs().up(tagname)

def push(tagname):
	""" Runs vcs ``checkout`` command on server """
	get_vcs().push(tagname)

def export(tagname):
	""" Runs vcs ``export`` command on server """
	get_vcs().export(tagname)

def configure():
	get_vcs().configure()

