
The following commands set up a new `grocery` Django project with a basic 
SQLite database, and a virtual environment with `red-fab-deploy`:

    django-admin.py startproject grocery
    cd grocery
    echo -e "\nDATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'grocery.db',}}" >> settings.py 
    virtualenv env
    source env/bin/activate
    # pip install red-fab-deploy
    pip install -e git+git://github.com/claudiob/red-fab-deploy.git#egg=fab_deploy
    echo -e "\nINSTALLED_APPS += ('fab_deploy', )" >> settings.py
    
