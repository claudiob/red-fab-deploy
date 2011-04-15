import fabric.api

def _redis_is_installed():
	with fabric.api.settings(fabric.api.hide('running','stdout','stderr'), warn_only=True):
		output = fabric.api.run('dpkg-query --show redis-server')
	return output.succeeded

def redis_install():
	""" Install redis-server. """
	if _redis_is_installed():
		fabric.api.warn(fabric.colors.yellow('Redis-server is already installed'))
		return

	package_install(['redis-server'])

def redis_setup():
	""" Setup redis-server. """
	pass

def redis_start():
	""" Start Nginx """
	fabric.api.run('redis-server')


