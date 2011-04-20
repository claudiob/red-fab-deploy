

    django-admin.py startproject grocery
    cd grocery
    echo -e "\nDATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'grocery.db',}}" >> settings.py 
    virtualenv env
    source env/bin/activate
