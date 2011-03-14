import fabric.api

def get_vcs():
	""" Returns a module with current VCS """
	name = fabric.api.env.conf['VCS']
	return __import__(name, fromlist=name.split('.')[1:])

def init():
	get_vcs().init()

def up(tagname,local=False):
	""" Runs vcs ``update`` command on server """
	get_vcs().up(tagname,local)

def push(tagname,local=False):
	""" Runs vcs ``checkout`` command on server """
	get_vcs().push(tagname,local)

def export(tagname,local=False):
	""" Runs vcs ``export`` command on server """
	get_vcs().export(tagname,local)

def configure():
	get_vcs().configure()

