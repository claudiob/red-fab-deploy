from fabric.api import *

def package_install(package, options='', update=False):
	""" Installs packages via apt-get. """
	if update: package_update(package)
	if type(package) in (list,tuple): package=" ".join(package)
	sudo('apt-get install %s --yes %s' % (options, package,))

def package_update(package=None):
	""" Update package on the server """
	if package:
		if type(package) in (list,tuple): package=" ".join(package)
		sudo('apt-get update --yes %s' % package)
	else:
		sudo('apt-get update --yes')
	
def package_upgrade(package=None):
	""" Upgrade packages on the server """
	if package:
		if type(package) in (list,tuple): package=" ".join(package)
		sudo('apt-get upgrade --yes %s' % package)
	else:
		sudo('apt-get upgrade --yes')

