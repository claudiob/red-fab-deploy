"""
Much of this code was compiled from:

http://incubator.apache.org/libcloud/getting-started.html
http://agiletesting.blogspot.com/2010/12/using-libcloud-to-manage-instances.html

Ubuntu 10.4 image sizes:
	http://uec-images.ubuntu.com/lucid/current/
"""

import os

import fabric.api
import fabric.colors

from libcloud.base import NodeImage, NodeSize
from libcloud.types import Provider
from libcloud.providers import get_driver

EC2_MACHINES = {
	'development' : {
		'dev1' : 'm1.small',
	},
	'production' : {
		# Use the Amazon Elastic Load Balancer
		'web1' : 'm1.small',
		'web2' : 'm1.small',
		'dbs1' : 'm1.small',
		'dbs2' : 'm1.small',
	},
}

PROVIDER_DICT = {
	'ec2_us_west': {
		'image'      : 'ami-9a8b79f3', # Ubuntu 10.04, 32-bit instance
		'location'   : 'us-west-b1',
		'machines'   : EC2_MACHINES,
	},
	'ec2_us_east': {
		'image'      : 'ami-9a8b79f3', # Ubuntu 10.04, 32-bit instance
		'location'   : 'us-east-b1',
		'machines'   : EC2_MACHINES,
	},
	'rackspace': {
		'image'      : '49', # Ubuntu 10.04, 32-bit instance
		'location'   : '0',  # Rackspace has only one location
		'machines'   : {
			'development' : {
				'dev1' : '1', # 256MB RAM, 10GB
			},
			'production' : {
				'load1' : '2', # 512MB RAM, 20GB
				'web1'  : '2', # 512MB RAM, 20GB
				'web2'  : '2', # 512MB RAM, 20GB
				'dbs1'  : '3', # 1024MB RAM, 40GB
				'dbs1'  : '3', # 1024MB RAM, 40GB
			},
		},
	},
}

def _get_provider_name():
	return fabric.api.env.conf['PROVIDER']

def _provider_exists(provider):
	""" Abort if provider does not exist """
	if provider not in PROVIDER_DICT.keys():
		fabric.api.abort(fabric.colors.red('Provider is %s is not available' % provider))

def _get_provider_dict(provider):
	""" Get the dictionary of provider settings """
	_provider_exists(provider)
	return PROVIDER_DICT[provider]

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
	
def _get_access_secret_key(provider):
	""" Get the access and secret keys for the given provider """
	_provider_exists(provider)
	if 'ec2' in provider:
		access_key = fabric.api.env.conf['AWS_ACCESS_KEY_ID']
		secret_key = fabric.api.env.conf['AWS_SECRET_ACCESS_KEY']
	elif provider == 'rackspace':
		access_key = fabric.api.env.conf['RACKSPACE_USER']
		secret_key = fabric.api.env.conf['RACKSPACE_KEY']
	return access_key, secret_key

def _get_connection():
	""" Get the connection for the given provider """
	provider = _get_provider_name()
	_provider_exists(provider)
	access_key, secret_key = _get_access_secret_key(provider)
	driver = _get_driver(provider)
	return driver(access_key,secret_key)

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

def list_nodes():
	return _get_connection().list_nodes()

def list_node_images():
	return _get_connection().list_images()

def list_node_sizes():
	return _get_connection().list_sizes()

def list_node_locations():
	return _get_connection().list_locations()

def get_node(name):
	for node in list_nodes():
		if node.name == name: return node

def get_node_image(image_id):
	""" 
	Return a node image from list of available images.
	If an image is not found matching the given id then a
	default NodeImage object will be created.
	"""
	for image in list_images():
		if image.id == image_id: return image
	return NodeImage(id=image_id,name="",driver="")

def get_node_size(size_id):
	""" 
	Return a node size from list of available sizes.
	If a size is not found matching the given id then a
	default NodeSize object will be created.
	"""
	for size in list_sizes():
		if size.id == size_id: return size
	return NodeSize(id=size_id,name="",ram=None,disk=None,
			bandwith=None,price=None,driver="")

def get_node_location(location_id):
	""" 
	Return a node location from list of available locations.
	If a location is not found matching the given id then a
	default NodeLocation object will be created.
	"""
	for location in list_locations():
		if location.availability_zone.name == location_id: return location
	return NodeLocation(id="",availability_zone=location,name="",country="",driver="")

def create_node(name, **kwargs):
	""" Create a node server """
	PROVIDER = _get_provider_dict(_get_provider_name())
	keyname  = kwargs.get('keyname',None)

	image    = kwargs.get('image',get_node_image(PROVIDER['image']))
	size     = kwargs.get('size',get_node_size(PROVIDER['size']))
	location = kwargs.get('location',get_node_location(PROVIDER['location']))

	if keyname:
		node = _get_connection().create_node(name=name, ex_keyname=keyname, 
				image=image, size=size, location=location)
	else:
		node = _get_connection().create_node(name=name, 
				image=image, size=size, location=location)

def deploy_nodes(stage='development',keyname=None):
	""" Deploy nodes based on stage type """
	PROVIDER = _get_provider_dict(_get_provider_name())
	if stage not in PROVIDER['machines']:
		fabric.api.abort(fabric.colors.red('Staging settings for %s are not available' % stage))
	
	for name in PROVIDER['machines'][stage]:
		size  = PROVIDER['machines'][stage][name]
		create_node(name,keyname=keyname,size=size)

