import os.path

import fabric.api

from fab_deploy.file import link_exists
from fab_deploy.package import package_update, package_upgrade, package_install
from fab_deploy.utils import detect_os

def service(service, command):
	""" Give a command to a service """
	if service not in ['apache','nginx','uwsgi']:
		return
	fabric.api.sudo('service %s %s' % (service,command))

def set_host_name(hostname):
	""" Set the host name on a server """
	pass

def prepare_server():
	""" Prepares server: installs system packages. """
	setup_backports()
	install_common_software()

def setup_backports():
	""" Adds backports repo to apt sources. """
	os = detect_os()
	backports = {
		'lenny': 'http://backports.debian.org/debian-backports lenny-backports main contrib non-free',
		'squeeze': 'http://backports.debian.org/debian-backports squeeze-backports main contrib non-free',
	}

	if os not in backports:
		fabric.api.warn(fabric.colors.yellow("Backports are not available for %s" % os))
		return

	fabric.api.run("echo 'deb %s' > /etc/apt/sources.list.d/backports.sources.list" % backports[os])
	with fabric.api.settings(warn_only=True):
		package_update()
		package_upgrade()

def install_common_software():
	""" Installs common system packages. """
	common_packages = [
		'ack-grep',
		'build-essential',
		'curl',
		'gcc',
		'libcurl3-dev',
		'libjpeg-dev',
		'libssl-dev',
		'memcached',
		'psmisc',
		'python2.6',
		'python2.6-dev',
		'python-imaging',
		'python-pip',
		'python-setuptools',
		'python-software-properties',
		'python-virtualenv',
		'rsync',
		'screen',
		'subversion',
		'zlib1g-dev',
	]
	extra_packages = {
		'lenny': [],
		'sqeeze': [],
		'lucid': [],
		'maverick': [],
	}

	os = detect_os()
	if os not in extra_packages:
		abort(fabric.colors.red('Your OS (%s) is currently unsupported.' % os))
	
	with fabric.api.settings(warn_only=True):
		package_update()
		package_upgrade()

	package_install(common_packages + extra_packages[os])

	vcs_options = {'lenny': '-t lenny-backports'}
	package_install(['mercurial','git-core'], vcs_options.get(os, ""))

def _user_exists(username):
	""" Determine if a user exists """
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('id %s' % username)
	return output.succeeded

def usage_disk():
	""" Return disk usage """
	fabric.api.run("df -kP")

def usage_mem():
	""" Return memory usage """
	fabric.api.run("cat /proc/meminfo")

def usage_cpu():
	""" Return cpu usage """
	fabric.api.run("cat /proc/stat")

def usage_system():
	""" Return system usage stats """
	usage_disk()
	usage_mem()
	usage_system()

