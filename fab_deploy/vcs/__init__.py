#from fabric.api import env
#
#def get_vcs():
#    """ Returns a module with current VCS """
#    name = env.conf.VCS
#    return __import__(name, fromlist=name.split('.')[1:])
#
#def init():
#    get_vcs().init()
#
#def push(tagname):
#    get_vcs().push(tagname)
#
#def up(tagname):
#    get_vcs().up(tagname)
#
#def configure():
#    get_vcs().configure()
#
