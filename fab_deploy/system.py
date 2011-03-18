import os.path

import fabric.api
import fabric.colors

from fab_deploy.file import link_exists
from fab_deploy.package import package_update, package_upgrade, package_install
from fab_deploy.utils import detect_os

def service(service, command):
	""" Give a command to a service """
	if service not in ['apache', 'nginx', 'uwsgi']:
		return
	fabric.api.sudo('service %s %s' % (service, command))

def get_internal_ip():
	""" Returns the internal IP address """
	command = """ifconfig eth0 | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}'"""
	return fabric.api.run(command)

def get_hostname():
	""" Get the host name on a server """
	return fabric.api.run('hostname')

def set_hostname(hostname):
	""" Set the host name on a server """
	host_text = "127.0.0.1 %s" % hostname
	if not fabric.contrib.files.contains('/etc/hosts',host_text,use_sudo=True):
		# TODO: Figure out why fabric.contrib.files.append doesn't work here
		# It's likely that append wants a list of strings, so giving simply
		# a string means it will interpret it as a list of characters, which
		# is the opposite of what you'd want.
		fabric.api.sudo('echo "%s" >> /etc/hosts' % host_text)
	
	if hostname != get_hostname():
		fabric.api.sudo('hostname %s' % hostname)

def prepare_server():
	""" Prepares server: installs system packages. """
	setup_backports()
	install_common_software()

def setup_backports():
	""" Adds backports repo to apt sources. """
	os = detect_os()
	backports = {
		'lenny'    : 'http://backports.debian.org/debian-backports lenny-backports main contrib non-free',
		'squeeze'  : 'http://backports.debian.org/debian-backports squeeze-backports main contrib non-free',
		'lucid'    : 'http://archive.ubuntu.com/ubuntu lucid-backports main universe multiverse restricted',
		'maverick' : 'http://archive.ubuntu.com/ubuntu maverick-backports main universe multiverse restricted',
	}

	if os in backports:
		fabric.api.puts(fabric.colors.green("Installing available backports for %s" % os))
		return

	fabric.api.run("echo 'deb %s' > /etc/apt/sources.list.d/backports.sources.list" % backports[os])
	with fabric.api.settings(warn_only = True):
		package_update()
		package_upgrade()

def install_common_software():
	""" Installs common system packages. """
	common_packages = [
		'ack-grep',
		'build-essential',
		'curl',
		'gcc',
		'ipython',
		'libcurl3-dev',
		'libjpeg-dev',
		'libssl-dev',
		'ntp',
		'psmisc',
		'python2.6',
		'python2.6-dev',
		'python-imaging',
		'python-mysqldb',
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
		fabric.api.abort(fabric.colors.red('Your OS (%s) is currently unsupported.' % os))

	with fabric.api.settings(warn_only = True):
		package_update()
		package_upgrade()

	package_install(common_packages + extra_packages[os])

	vcs_options = {'lenny': '-t lenny-backports'}
	package_install(['mercurial', 'git-core'], vcs_options.get(os, ""))

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

