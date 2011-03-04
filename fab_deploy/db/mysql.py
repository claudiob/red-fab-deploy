from datetime import datetime

import fabric.api

from fab_deploy.package import package_install
from fab_deploy.utils import detect_os

def _mysql_is_installed():
	with fabric.api.settings(fabric.api.hide('stderr'), warn_only=True):
		output = fabric.api.run('mysql --version')
	return output.succeeded
	
def mysql_install():
	""" Installs MySQL """
	if _mysql_is_installed():
		fabric.api.runwarn(fabric.colors.yellow('MySQL is already installed.'))
		return

	# Ensure mysql won't ask for a password on installation
	# See the following:
	# http://serverfault.com/questions/19367/scripted-install-of-mysql-on-ubuntu
	# http://www.muhuk.com/2010/05/how-to-install-mysql-with-fabric/

	os = detect_os()
	package_install('debconf-utils')
	
	# get the password
	passwd = fabric.api.runprompt('Please enter MySQL root password:')
	
	# get the correct version for installation
	mysql_versions = {
		'lenny': '5.0',
		'sqeeze': '5.1',
		'lucid': '5.1',
		'maverick': '5.1',
	}
	version = mysql_versions[os]

	debconf_defaults = [
		"mysql-server-%s mysql-server/root_password password %s" % (version,passwd),
		"mysql-server-%s mysql-server/root_password_again password %s" % (version,passwd),
	]

	fabric.api.runrun("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

	fabric.api.runwarn(fabric.colors.yellow('The password for mysql "root" user will be set to "%s"' % passwd))

	common_packages = [
		'automysqlbackup',
		'sendmail',
		'mysql-server-%s' % version,
		'python-mysqldb',
		]
	extra_packages = {
		'lenny'   : ['libmysqlclient15-dev',],
		'sqeeze'  : ['libmysqlclient-dev',],
		'lucid'   : ['libmysqlclient-dev',],
		'maverick': ['libmysqlclient-dev',],
	}
	package_install(common_packages + extra_packages[os])

def mysql_execute(sql, user='', password=''):
	"""
	Executes passed sql command using mysql shell.
	"""
	return fabric.api.runrun("echo '%s' | mysql -u%s -p%s" % (sql, user, password))

def mysql_create_db():
	"""
	Creates an empty mysql database. 
	"""
	mysql_user     = fabric.api.runprompt('Please enter MySQL username:')
	mysql_database = fabric.api.runprompt('Please enter MySQL database name:')
	
	params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
	mysql_execute('CREATE DATABASE %s %s;' % (mysql_database, params), mysql_user)

def mysql_create_user():
	"""
	Create a new mysql user.
	"""
	mysql_user     = fabric.api.runprompt('Please enter MySQL username:')
	
	new_user       = fabric.api.runprompt('Please enter new MySQL username:')
	new_password   = fabric.api.runprompt('Please enter new MySQL password for %s:' % new_user)

	mysql_execute("""GRANT ALL privileges ON *.* TO "%s" IDENTIFIED BY "%s";""" % 
		(new_user, new_password), mysql_user)

def mysql_drop_user():
	"""
	Create a new mysql user.
	"""
	mysql_user     = fabric.api.runprompt('Please enter MySQL username:')
	drop_user      = fabric.api.runprompt('Please enter MySQL username to drop:')

	mysql_execute("DROP USER %s;" % (drop_user), mysql_user)

def mysql_dump():
	""" 
	Runs mysqldump. Result is stored at /srv/active/sql/ 
	"""
	dir = '/srv/active/sql/'
	fabric.api.runrun('mkdir -p %s' % dir)
	now = datetime.now().strftime("%Y.%m.%d-%H.%M")
	
	mysql_user     = fabric.api.runprompt('Please enter MySQL username:')
	mysql_database = fabric.api.runprompt('Please enter MySQL database name:')
	
	run('mysqldump -u%s -p %s > %s' % (mysql_user, mysql_database,
		os.path.join(dir, '%s-%s.sql' % (mysql_database, now))))

def mysql_load(filename):
	"""
	try mysql DATABASENAME < filename.sql
	"""
	mysql_user     = fabric.api.runprompt('Please enter MySQL username:')
	mysql_database = fabric.api.runprompt('Please enter MySQL database name:')
	run('mysql %s -u%s -p < %s' % (mysql_database, mysql_user, filename))

def mysql_backup():
	""" Backup the database """
	fabric.api.runrun('automysqlbackup')

