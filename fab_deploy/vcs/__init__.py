from fabric.api import env

def get_vcs():
    """ Returns a module with current VCS """
    name = env.conf.VCS
    return __import__(name, fromlist=name.split('.')[1:])

def push():
    get_vcs().push()

def up(branch=None):
    get_vcs().up(branch or default_branch())

def init():
    get_vcs().init()

def configure():
    get_vcs().configure()

def default_branch():
    return env.conf.get(get_vcs().BRANCH_OPTION, None)
