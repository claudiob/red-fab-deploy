## Preparing the code for deployment

The `rfd` command can be used to set up the application for deployment.

Before deploying on a remote machine, some information has to collected:

* the public IP of the remote machine
* the private IP of the remote machine
* the location of the repository from where to deploy the code

If the site will be hosted on [Rackspace servers](http://www.rackspace.com), then the [rscurl.sh command line](https://github.com/jsquared/rscurl) can be used to generate a server instance by running:

    ./rscurl -r [Your SVN repository ]-u [Your Rackspace Server username] -a [Your Rackspace Server app key] -c create-server -i 49 -f 1 -n [Your Rackspace Server instance name]

The previous line spawns an "Ubuntu 10.04 LTS (lucid)" machines with 256MB destined to staging and returns a the *public IP*, *private IP* and *administrator password* for the newly created instance, something like:

    ID     Status    Server Name                                       Admin Password                                    Public IP             Private IP          
    ------ --------- ------------------------------------------------- ------------------------------------------------- --------------------- ---------------------
    689705 "BUILD"   "[Your Rackspace Server instance name]"           "[Your Rackspace Server instance password]"       ["[Your public IP]"]  ["[Your private IP]"]    

With this information at hand, run the `rfd` command from the trunk/ folder:

    cd .. # goes one folder back
    rfd [Your Rackspace Server instance name] -p rackspace -u [Your Rackspace Server username] -k [Your Rackspace Server app key] -v [Your private IP] -b [Your public IP] -e [Environment: staging or production]

which will create the appropriate *nginx*, *apache* and *uwsgi* configuration files in the deploy/ folder, and the *fabfile.py* and *fabric.conf* files.
Then type the following two commands to set up the remote server:

    fab update_nodes 
    fab set_hosts:staging provider_as_ec2
    fab set_hosts:staging go_setup:staging -i ubuntu.id_dsa

When the MySQL server prompts for data, fill with name, user 'django' and 
password '', having set those in settings/staging.py (this should have been done before).
The user/password to do this is root/password.

<!-- In case it's not done automatically:
## Setting up the database on the staging machine

$ fab -i deploy/[your private SSH key here] dev mysql_install
$ fab -i deploy/[your private SSH key here] dev mysql_create_db
$ fab -i deploy/[your private SSH key here] dev mysql_create_user

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': os.path.join(PROJECT_ROOT, 'dentsu_vii_staging.db'),
    }
}
-->
    
## Deploying the code from a SVN repository

Deploying is done from a tag in the version control repository, so there should be one.
For instance, to create a new tag in a subversion repository run:

    svn copy [SVN Repo]/trunk [SVN Repo]/tags/release-0.0.1; svn ci -m "Tagging 'trunk' for red-fab-deploy."

and finally deploy that tag to the staging server by running:

    fab set_hosts:staging update_env deploy_full:release-0.0.1 -i ubuntu.id_dsa

## Launching the application on the staging machine

Start the nginx server and uWSGI on Rackspace running:

<!-- THIS SHOULD GO IN THE SCRIPT!! -->
    
    fab set_hosts:staging web_server_setup:staging -i ubuntu.id_dsa
    fab set_hosts:staging web_server_start -i ubuntu.id_dsa

Then execute the commands to set up the project database on the staging machine:

    fab set_hosts:staging syn:staging -i ubuntu.id_dsa

This will ask to create an admin user (write down the password you use here!)
Finally open up the public IP in the browser and see the application running!

## Updating the code and restarting the server

To update the code on the remote machine, run:

    fab set_hosts:staging deploy_project:release-0.0.2 -i ubuntu.id_dsa
    fab set_hosts:staging make_active:release-0.0.2 -i ubuntu.id_dsa
    
and restart the server running:

    fab set_hosts:staging uwsgi_restart -i ubuntu.id_dsa
    fab set_hosts:staging web_server_restart -i ubuntu.id_dsa 

## Cleaning up

    ./rscurl -c delete-server -s [Your Rackspace Server instance ID]
