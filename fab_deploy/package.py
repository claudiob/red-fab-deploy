import fabric.api

def package_install(package, options = '', update = False):
	""" Installs packages via apt-get. """
	if update: package_update(package)
	if type(package) in (list, tuple): package = " ".join(package)
	fabric.api.sudo('apt-get install %s --yes %s' % (options, package,))

def package_update(package = None):
	""" Update package on the server """
	if package:
		if type(package) in (list, tuple): package = " ".join(package)
		fabric.api.sudo('apt-get update --yes %s' % package)
	else:
		fabric.api.sudo('apt-get update --yes')

def package_upgrade(package = None):
	""" Upgrade packages on the server """
	if package:
		if type(package) in (list, tuple): package = " ".join(package)
		fabric.api.sudo('apt-get upgrade --yes %s' % package)
	else:
		fabric.api.sudo('apt-get upgrade --yes')

def package_add_repository(repo):
	fabric.api.sudo('add-apt-repository %s' % repo)
	package_update()

