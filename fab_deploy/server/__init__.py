from fab_deploy.server.apache import (apache_install, apache_setup,
	apache_start, apache_stop, apache_restart, 
	apache_touch_wsgi, apache_make_wsgi,
	apache_make_config, apache_setup_locale, )
from fab_deploy.server.nginx import (nginx_install, nginx_setup,
	nginx_start, nginx_stop, nginx_restart, )
from fab_deploy.server.uwsgi import (uwsgi_install, uwsgi_setup,
	uwsgi_start, uwsgi_stop, uwsgi_restart, )
from fab_deploy.server.web import (web_server_install, web_server_setup, 
	web_server_start, web_server_stop, web_server_restart, web_server_touch)
