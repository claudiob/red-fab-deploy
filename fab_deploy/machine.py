"""
Much of this code was compiled from:

http://incubator.apache.org/libcloud/getting-started.html
http://agiletesting.blogspot.com/2010/12/using-libcloud-to-manage-instances.html
http://agiletesting.blogspot.com/2011/01/libcloud-042-and-ssl.html

Ubuntu 10.4 image sizes:
	http://uec-images.ubuntu.com/lucid/current/
"""

import simplejson

from pprint import pprint
import os

import fabric.api
import fabric.colors
import fabric.contrib


from libcloud.compute.base import NodeImage, NodeLocation, NodeSize
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import libcloud.security

from fab_deploy.package import package_install, package_update

#=== SSL Security

libcloud.security.VERIFY_SSL_CERT = True
libcloud.security.CA_CERTS_PATH.append("cacert.pem")

#=== CONF Defaults
#CONF_FILE = os.path.join(os.getcwd(),'fabric.conf')

SERVER = {'nginx':{},'uwsgi':{}}
DB     = {
	'mysql': {
		'name'     :'',     # not default
		'user'     :'',     # not root
		'password' :'',     # not root
		#'slave'    :'db1',  # reference to master database
	},
}

#=== Cloud Defaults
EC2_IMAGE = 'ami-9a8b79f3' # Ubuntu 10.04, 32-bit instance
EC2_MACHINES = {
	'development' : {
		'dev1' : {
			'services': dict(SERVER, **DB),
			'size':'m1.small',},
	},
	'production' : {
		# Use the Amazon Elastic Load Balancer
		'web1' : {
			'services': SERVER,
			'size':'m1.small',},
		'web2' : {
			'services': SERVER,
			'size':'m1.small',},
		'dbs1' : {
			'services': DB,
			'size':'m1.small',},
		'dbs2' : {
			'services': {'slave':'dbs1'},
			'size':'m1.small',},
	},
}

PROVIDER_DICT = {
	'ec2_us_west': {
		'image'      : EC2_IMAGE,
		'location'   : 'us-west-1b',
		'machines'   : EC2_MACHINES,
	},
	'ec2_us_east': {
		'image'      : EC2_IMAGE,
		'location'   : 'us-east-1b',
		'machines'   : EC2_MACHINES,
	},
	'rackspace': {
		'image'      : '49', # Ubuntu 10.04, 32-bit instance
		'location'   : '0',  # Rackspace has only one location
		'machines'   : {
			'development' : {
				'dev1'  : {
					'services': dict(SERVER, **DB),
					'size':'1',}, # 256MB  RAM, 10GB
			},
			'production' : {
				'load1' : {
					'services': {'nginx':{}},
					'size':'2',}, # 512MB  RAM, 20GB
				'web1'  : {
					'services': {'uwsgi':{}},
					'size':'2',}, # 512MB  RAM, 20GB
				'web2'  : {
					'services': {'uwsgi':{}},
					'size':'2',}, # 512MB  RAM, 20GB
				'dbs1'  : {
					'services': DB,
					'size':'3',}, # 1024MB RAM, 40GB
				'dbs2'  : {
					'services': {'slave':'dbs1'},
					'size':'3',}, # 1024MB RAM, 40GB
			},
		},
	},
}

#=== Conf File

def write_conf(node_dict,filename=''):
	if not filename:
		filename = fabric.api.env.conf['CONF_FILE']
	""" Overwrite the conf file with dictionary values """
	obj = simplejson.dumps(node_dict, sort_keys=True, indent=4)
	f = open(filename,'w')
	f.write(obj)
	f.close()

def generate_config(provider='ec2_us_east'):
	""" Generate a default json config file for your provider """
	_provider_exists(provider)
	conf_file = fabric.api.env.conf['CONF_FILE']
	if os.path.exists(conf_file):
		if not fabric.contrib.console.confirm("Do you wish to overwrite the config file %s?" % (conf_file), default=False):
			conf_file = os.path.join(os.getcwd(),fabric.api.prompt('Enter a new filename:'))

	write_conf(PROVIDER_DICT[provider],filename=conf_file)
	print fabric.colors.green('Successfully generated config file %s' % conf_file)

def get_provider_dict():
	""" Get the dictionary of provider settings """
	conf_file = fabric.api.env.conf['CONF_FILE']
	return simplejson.loads(open(conf_file,'r').read())

def stage_exists(stage):
	""" Abort if provider does not exist """
	PROVIDER = get_provider_dict()
	if stage not in PROVIDER['machines'].keys():
		fabric.api.abort(fabric.colors.red('Stage "%s" is not available' % stage))

#=== Private Methods

def _get_provider_name():
	return fabric.api.env.conf['PROVIDER']

def _provider_exists(provider):
	""" Abort if provider does not exist """
	
	if provider not in PROVIDER_DICT.keys():
		fabric.api.abort(fabric.colors.red('Provider "%s" is not available, choose from %s' % (provider,PROVIDER_DICT.keys())))

def _get_driver(provider):
	""" Get the driver for the given provider """
	_provider_exists(provider)
	if provider == 'ec2_us_west':
		driver = get_driver(Provider.EC2_US_WEST)
	elif provider == 'ec2_us_east':
		driver = get_driver(Provider.EC2_US_EAST)
	elif provider == 'rackspace':
		driver = get_driver(Provider.RACKSPACE)
	return driver
	
def _get_access_secret_keys(provider):
	""" Get the access and secret keys for the given provider """
	_provider_exists(provider)
	if 'ec2' in provider:
		if 'AWS_ACCESS_KEY_ID' in fabric.api.env.conf and 'AWS_SECRET_ACCESS_KEY' in fabric.api.env.conf:
			access_key = fabric.api.env.conf['AWS_ACCESS_KEY_ID']
			secret_key = fabric.api.env.conf['AWS_SECRET_ACCESS_KEY']
		else:
			fabric.api.abort(fabric.colors.red('Must have AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in env'))
	elif provider == 'rackspace':
		if 'RACKSPACE_USER' in fabric.api.env.conf and 'RACKSPACE_KEY' in fabric.api.env.conf:
			access_key = fabric.api.env.conf['RACKSPACE_USER']
			secret_key = fabric.api.env.conf['RACKSPACE_KEY']
		else:
			fabric.api.abort(fabric.colors.red('Must have RACKSPACE_USER and RACKSPACE_KEY in env'))
	return access_key, secret_key

def _get_connection():
	""" Get the connection for the given provider """
	provider = _get_provider_name()
	_provider_exists(provider)
	access_key, secret_key = _get_access_secret_keys(provider)
	driver = _get_driver(provider)
	return driver(access_key,secret_key)

def _get_stage_machines(stage):
	""" Return a list of server names for stage """
	stage_exists(stage)
	PROVIDER = get_provider_dict()
	return [name for name in PROVIDER['machines'][stage].keys()]

#=== AWS Specific Code

def ec2_create_key(keyname):
	""" Create a pem key on an amazon ec2 server. """
	resp = _get_connection().ex_create_keypair(name=keyname)
	key_material = resp.get('keyMaterial')
	if not key_material:
		fabric.api.abort(fabric.colors.red("Key Material was not returned"))
	private_key = '%s.pem' % keyname
	f = open(private_key, 'w')
	f.write(key_material + '\n')
	f.close()
	os.chmod(private_key, 0600)

def ec2_authorize_port(name,protocol,port):

	if protocol not in ['tcp','udp','icmp']:
		fabric.api.abort(fabric.colors.red('Protocol must be one of tcp, udp, or icmp'))
	
	if int(port) < -1 or int(port) > 65535:
		fabric.api.abort(fabric.colors.red('Ports must fall between 0 and 65535'))
		
	results = []
	params = {'Action': 'AuthorizeSecurityGroupIngress',
			'GroupName': name,
			'IpProtocol': protocol,
			'FromPort': port,
			'ToPort': port,
			'CidrIp': '0.0.0.0/0'}

	try:
		node_driver = _get_connection()
		results.append(
			node_driver.connection.request(node_driver.path, params=params.copy()).object
		)
	except Exception, e:
		if e.args[0].find("InvalidPermission.Duplicate") == -1:
			raise e
	
	return results
	
#=== List Node Instances

def list_nodes():
	""" Return a list of nodes """
	return _get_connection().list_nodes()

def list_node_images():
	""" Return a list of node images """
	return _get_connection().list_images()

def list_node_sizes():
	""" Return a list of node sizes """
	return _get_connection().list_sizes()

def list_node_locations():
	""" Return a list of node locations """
	return _get_connection().list_locations()

#=== Get Node Instance

def get_node(name):
	""" Get a node by name """
	for node in list_nodes():
		if node.name == name: return node

def get_node_image(image_id):
	""" 
	Return a node image from list of available images.
	If an image is not found matching the given id then a
	default NodeImage object will be created.
	"""
	for image in list_node_images():
		if image.id == image_id: return image
	return NodeImage(id=image_id,name="",driver="")

def get_node_size(size_id):
	""" 
	Return a node size from list of available sizes.
	If a size is not found matching the given id then a
	default NodeSize object will be created.
	"""
	for size in list_node_sizes():
		if size.id == size_id: return size
	id        = size_id
	name      = ""
	ram       = None
	disk      = None
	bandwidth = None
	price     = None
	driver    = ""
	return NodeSize(id,name,ram,disk,bandwidth,price,driver)

def get_node_location(location_id):
	""" 
	Return a node location from list of available locations.
	If a location is not found matching the given id then a
	default NodeLocation object will be created.
	"""
	provider = _get_provider_name()
	for location in list_node_locations():
		if 'ec2' in provider:
			if location.availability_zone.name == location_id: return location
		else:
			if location.id == location_id: return location
	return NodeLocation(id="",availability_zone=location,name="",country="",driver="")

#=== Print Singular Node Instances

def print_node(name):
	""" Pretty print a node by name """
	pprint(get_node(name).__dict__)

def print_node_image(id):
	""" Pretty print a node image by id """
	pprint(get_node_image(id).__dict__)

def print_node_size(id):
	""" Pretty print a node size by id """
	pprint(get_node_size(id).__dict__)

def print_node_location(id):
	""" Pretty print a node locaiton by id """
	pprint(get_node_location(id).__dict__)

#=== Print List of Node Instances

def print_nodes():
	""" Pretty print the list of nodes """
	for n in list_nodes():
		pprint(n.__dict__)

def print_node_images():
	""" Pretty print the list of node images """
	for i in list_node_images():
		pprint(i.__dict__)

def print_node_sizes():
	""" Pretty print the list of node sizes """
	for s in list_node_sizes():
		pprint(s.__dict__)

def print_node_locations():
	""" Pretty print the list of node locations """
	for l in list_node_locations():
		pprint(l.__dict__)

#=== Create and Deploy Nodes

def create_node(name, **kwargs):
	""" Create a node server """
	PROVIDER = get_provider_dict()
	keyname  = kwargs.get('keyname',None)
	image    = kwargs.get('image',get_node_image(PROVIDER['image']))
	size     = kwargs.get('size','')
	location = kwargs.get('location',get_node_location(PROVIDER['location']))
	
	if 'ec2' in fabric.api.env.conf['PROVIDER']:
		node = _get_connection().create_node(name=name, ex_keyname=keyname, 
				image=image, size=size, location=location)
    	
		# TODO: This does not work until libcloud 0.4.3
		tags = {'name':name,}
		_get_connection().ex_create_tags(node,tags)

	else:
		if keyname:
			pubkey = open(keyname,'r').read()
			from libcloud.compute.base import NodeAuthSSHKey
			key = NodeAuthSSHKey(pubkey)
		else: key=None
		node = _get_connection().create_node(name=name, auth=key,
				image=image, size=size, location=location)
	    
	print fabric.colors.green('Node %s successfully created' % name)
	return node

def deploy_nodes(stage='development',keyname=None):
	""" Deploy nodes based on stage type """
	stage_exists(stage)
	#if not keyname:
	#	fabric.api.abort(fabric.colors.red("Must supply valid keyname."))

	if not fabric.contrib.console.confirm("Do you wish to stage %s servers on %s with the following names: %s?" % (stage, _get_provider_name(), ', '.join(_get_stage_machines(stage))), default=False):
		fabric.api.abort(fabric.colors.red("Aborting node deployment."))

	PROVIDER = get_provider_dict()
	for name in PROVIDER['machines'][stage]:
		node_dict = PROVIDER['machines'][stage][name]
		if 'uuid' not in node_dict or not node_dict['uuid']:
			size = get_node_size(node_dict['size'])
			node = create_node(name,keyname=keyname,size=size,image=node_dict.get('image'))
			node_dict.update({'id': node.id, 'uuid' : node.uuid,})
			PROVIDER['machines'][stage][name] = node_dict
		else:
			fabric.api.warn(fabric.colors.yellow("%s machine %s already exists" % (stage,name)))
	
	write_conf(PROVIDER)

def update_nodes():

	# TODO: Should wait and restart if not updated

	PROVIDER = get_provider_dict()
	for stage in PROVIDER['machines']:
		for name in PROVIDER['machines'][stage]:
			if 'id' in PROVIDER['machines'][stage][name]:
				id = PROVIDER['machines'][stage][name]['id']
				for node in list_nodes():
					if node.__dict__['id'] == id:

						if 'private_ip' in node.__dict__:
							private_ip = node.__dict__['private_ip']
						else:
							private_ip = [node.__dict__.get('extra', {}).get('private_dns')]
						
						if 'public_ip' in node.__dict__:
							public_ip = node.__dict__['public_ip']
						else:
							public_ip = [node.__dict__.get('extra', {}).get('dns_name')]
						
						info = {
							'uuid'       : node.__dict__['uuid'],
							'private_ip' : private_ip,
							'public_ip'  : public_ip,
						}
						PROVIDER['machines'][stage][name].update(info)

	write_conf(PROVIDER)

def save_as_ami(name, arch='i386'):
	config = get_provider_dict()
	# Copy pk and cert to /tmp, somehow
	fabric.api.put(fabric.api.env.conf['AWS_X509_PRIVATE_KEY'], '/tmp/pk.pem')
	fabric.api.put(fabric.api.env.conf['AWS_X509_CERTIFICATE'], '/tmp/cert.pem')
	
	fabric.contrib.files.sed('/etc/apt/sources.list', 'universe$', 'universe multiverse', use_sudo=True)
	package_update()
	package_install('ec2-ami-tools', 'ec2-api-tools')
	
	fabric.api.sudo('ec2-bundle-vol -c /tmp/cert.pem -k /tmp/pk.pem -u %s -s 10240 -r %s' % (fabric.api.env.conf['AWS_ID'], arch))
	fabric.api.sudo('ec2-upload-bundle -b %s -m /tmp/image.manifest.xml -a %s -s %s --location %s' % (fabric.api.env.conf['AWS_AMI_BUCKET'], fabric.api.env.conf['AWS_ACCESS_KEY_ID'], fabric.api.env.conf['AWS_SECRET_ACCESS_KEY'], config['location'][:-1]))
	result = fabric.api.sudo('ec2-register -C /tmp/cert.pem -K /tmp/pk.pem --region %s %s/image.manifest.xml -n %s' % (config['location'][:-1], fabric.api.env.conf['AWS_AMI_BUCKET'], name))
	fabric.api.run('rm /tmp/pk.pem')
	fabric.api.run('rm /tmp/cert.pem')
	
	ami = result.split()[1]
	
def launch_auto_scaling(stage = 'development'):
	config = get_provider_dict()
	from boto.ec2.autoscale import AutoScaleConnection, AutoScalingGroup, LaunchConfiguration, Trigger
	conn = AutoScaleConnection(fabric.api.env.conf['AWS_ACCESS_KEY_ID'], fabric.api.env.conf['AWS_SECRET_ACCESS_KEY'], host='%s.autoscaling.amazonaws.com' % config['location'][:-1])
	
	for name, values in config.get(stage, {}).get('autoscale', {}):
		if any(group.name == name for group in conn.get_all_groups()):
			fabric.api.warn(fabric.colors.orange('Autoscale group %s already exists' % name))
			continue
		lc = LaunchConfiguration(name = '%s-launch-config' % name, image_id = values['image'],  key_name = config['key'])
		conn.create_launch_configuration(lc)
		ag = AutoScalingGroup(group_name = name, load_balancers = values.get('load-balancers'), availability_zones = [config['location']], launch_config = lc, min_size = values['min-size'], max_size = values['max-size'])
		conn.create_auto_scaling_group(ag)
		if 'min-cpu' in values and 'max-cpu' in values:
			tr = Trigger(name = '%s-trigger' % name, autoscale_group = ag, measure_name = 'CPUUtilization', statistic = 'Average', unit = 'Percent', dimensions = [('AutoScalingGroupName', ag.name)],
						 period = 60, lower_threshold = values['min-cpu'], lower_breach_scale_increment = '-1', upper_threshold = values['max-cpu'], upper_breach_scale_increment = '2', breach_duration = 60)
			conn.create_trigger(tr)
		
	 	
	
