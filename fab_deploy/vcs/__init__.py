from fabric.api import env

def get_vcs():
	""" Returns a module with current VCS """
	name = env.conf['VCS']
	return __import__(name, fromlist=name.split('.')[1:])

def init():
	get_vcs().init()

def up(tagname):
	""" Runs vcs ``update`` command on server """
#	delete_pyc()
	get_vcs().up(tagname)
#	compress()
#	touch_web_server()

def push(tagname):
	""" Runs vcs ``checkout`` command on server """
	get_vcs().push(tagname)

def export(tagname):
	""" Runs vcs ``export`` command on server """
	get_vcs().export(tagname)

def configure():
	get_vcs().configure()

#def make_clone(tagname):
#	""" Creates repository clone on remote server. """
#	run('mkdir -p %s' % env.conf['SRC_DIR'])
#	with cd(env.conf['SRC_DIR']):
#		with settings(warn_only=True):
#			svn.init()
#	svn.push(tagname)
#	with cd(env.conf['SRC_DIR']):
#		vcs.up(tagname)
#	svn.configure()

#def push(*args):
#	''' Run it instead of your VCS push command.
#
#	Arguments:
#
#	* notest - don't run tests
#	* syncdb - run syncdb before code reloading
#	* migrate - run migrate before code reloading
#	* pip_update - run pip_update before code reloading
#	* norestart - do not reload source code
#	'''
#	allowed_args = set(['force', 'notest', 'syncdb', 'migrate', 'pip_update', 'norestart'])
#	for arg in args:
#		if arg not in allowed_args:
#			puts('Invalid argument: %s' % arg)
#			puts('Valid arguments are: %s' % allowed_args)
#			return
#
#	vcs.push()
#	delete_pyc()
#	with cd('src/%s'env.conf['INSTANCE_NAME']):
#		vcs.up()
#
#	if 'pip_update' in args:
#		pip_update()
#	if 'syncdb' in args:
#		syncdb()
#	if 'migrate' in args:
#		migrate()
#	compress()
#	if 'norestart' not in args:
#		touch_web_server()
#	if 'notest' not in args:
#		test()
