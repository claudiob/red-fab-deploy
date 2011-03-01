from datetime import datetime
from fabric.api import *

from fab_deploy.utils import detect_os, run_as
from fab_deploy.system import aptitude_install

def _mysql_is_installed():
	with settings(hide('stderr'), warn_only=True):
		output = run('mysql --version')
	return output.succeeded
	
@run_as('root')
def mysql_install():
	""" Installs MySQL """
	if _mysql_is_installed():
		warn('MySQL is already installed.')
		return

	# Ensure mysql won't ask for a password on installation
	# See the following:
	# http://serverfault.com/questions/19367/scripted-install-of-mysql-on-ubuntu
	# http://www.muhuk.com/2010/05/how-to-install-mysql-with-fabric/

	os = detect_os()
	aptitude_install('debconf-utils')
	
	# get the password
	passwd = env.conf['DB_PASSWORD']
	if not passwd:
		passwd = prompt('Please enter MySQL root password:')
	
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

	run("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

	warn('\n=========\nThe password for mysql "root" user will be set to "%s"\n=========\n' % passwd)
	common_packages = [
		'automysqlbackup',
		'sendmail',
		'mysql-server-%s' % version,
		'python-mysqldb',
		]
	extra_packages = {
		'lenny': [
			'libmysqlclient15-dev',
			],
		'sqeeze': [
			'libmysqlclient-dev',
			],
		'lucid': [
			'libmysqlclient-dev',
			],
		'maverick': [
			'libmysqlclient-dev',
			],
	}
	aptitude_install(" ".join(common_packages + extra_packages[os]))

def mysql_execute(sql, user=None, password=None):
	"""
	Executes passed sql command using mysql shell.
	"""
	user = user
	password = password
	return run("echo '%s' | mysql -u%s -p%s" % (sql, user, password))

def mysql_create_db():
	"""
	Creates an empty mysql database. 
	"""
	mysql_database = prompt('Please enter MySQL database name:')
	mysql_user = prompt('Please enter MySQL username:')
	mysql_password = prompt('Please enter MySQL password for %s:' % mysql_user)
	params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
	mysql_execute('CREATE DATABASE %s %s;' % (mysql_database, params),
		mysql_user, mysql_password)

def mysqldump(dir=None):
	""" Runs mysqldump. Result is stored at <env>/var/backups/ """
	if dir is not None:
		dir = env.conf['SRC_DIR'] + '/var/backups'
		now = datetime.now().strftime("%Y.%m.%d-%H.%M")
		db = env.conf['DB_NAME']
		password = env.conf['DB_PASSWORD']
		run('mysqldump -uroot -p%s %s > %s/%s%s.sql' % (password, db, dir, db, now))

def mysql_backup():
	""" Backup the database """
	run('automysqlbackup')

