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
	passwd = fabric.api.prompt('Please enter MySQL root password:')
	
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

	fabric.api.sudo("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

	fabric.api.warn(fabric.colors.yellow('The password for mysql "root" user will be set to "%s"' % passwd))

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
	return fabric.api.run("echo '%s' | mysql -u%s -p%s" % (sql, user, password))

def mysql_create_db():
	"""
	Creates an empty mysql database. 
	"""
	user     = fabric.api.prompt('Please enter username:')
	database = fabric.api.prompt('Please enter database name:')
	
	params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
	mysql_execute('CREATE DATABASE %s %s;' % (database, params), user)

def mysql_create_user():
	""" Create a new mysql user. """
	user         = fabric.api.prompt('Please enter username:')
	new_user     = fabric.api.prompt('Please enter new username:')
	new_password = fabric.api.prompt('Please enter new password for %s:' % new_user)

	mysql_execute("""GRANT ALL privileges ON *.* TO "%s" IDENTIFIED BY "%s";""" % 
		(new_user, new_password), user)

def mysql_drop_user():
	""" Drop a mysql user. """
	user      = fabric.api.prompt('Please enter username:')
	drop_user = fabric.api.prompt('Please enter username to drop:')

	mysql_execute("DROP USER %s;" % (drop_user), user)

def mysql_dump():
	""" Runs mysqldump. Result is stored at /srv/active/sql/ """
	dir = '/srv/active/sql/'
	fabric.api.run('mkdir -p %s' % dir)
	now = datetime.now().strftime("%Y.%m.%d-%H.%M")
	
	user     = fabric.api.prompt('Please enter username:')
	database = fabric.api.prompt('Please enter database name:')
	
	fabric.api.run('mysqldump -u%s -p %s > %s' % (user, database,
		os.path.join(dir, '%s-%s.sql' % (database, now))))

def mysql_load(filename):
	""" Load MySQL Database with 'mysql DATABASENAME < filename.sql' """
	user     = fabric.api.prompt('Please enter username:')
	database = fabric.api.prompt('Please enter database name:')
	fabric.api.run('mysql %s -u%s -p < %s' % (database, user, filename))

def list_sql_files():
	""" List available sql files in active project """
	fabric.api.run('ls /srv/active/sql')

def mysql_backup():
	""" Backup the database """
	fabric.api.run('automysqlbackup')

