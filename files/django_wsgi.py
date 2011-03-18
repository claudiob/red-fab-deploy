import os, sys
PATH = os.path.join(os.path.dirname(__file__), '..')
sys.path += [
	os.path.join(PATH, 'project/apps'), 
	os.path.join(PATH, 'project'), 
	os.path.join(PATH, '..'), 
	PATH]
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings.%(ENVIRONMENT)s'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
