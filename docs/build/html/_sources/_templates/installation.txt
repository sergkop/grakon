.. _ref-installation:

Installation and running server
===============================

Installation
~~~~~~~~~~~~

The installation procedure is well tested for Ubuntu. Other Linux systems and Mac OS should
work as well, however automation script may not work. 

1. Create ssh keys to access github - see `github docs`_
2. Create a folder which will contain all grakon-related files (path - GRAKON_DIR)
3. Get source code::

    git clone git@github.com:sergkop/grakon.git GRAKON_DIR/source

4. Install required packages::

    sudo aptitude install python python-setuptools git python-pip
    sudo pip install fabric --upgrade

5. Run script which automates installation steps::

    cd GRAKON_DIR/source/deployment
    fab developer_init

Running development server
~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Activate virtual enviroment::

    cd GRAKON_DIR/source
    source ../env/bin/activate

2. Run development server::

    python manage.py runserver

3. Website is now accessible at http://127.0.0.1:8000 in your browser. Admin interface - http://127.0.0.1:8000/admin/.
   Admin user is already created (username: grakon, password: grakon).

Server automatically reloads on any change in the code.

Lots of data from database is cached. If you notice any inconsistencies - report to backend developer.
Restarting server resets the cache.

Development process
===================

Commiting code to repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Make sure you haven't introduced bugs in your new code
2. To see the changes you are going to commit use::

    git status

3. Add all changes to commit::

    git add -A

   Adding/removing of particular files can be done using::

    git add file_path / git rm file_path

4. Commit changes::

    git commit -m "your comment here"

5. Push to central repository::

    git push

Getting new code from repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on how much your recent changes interfere with new changes in repository
you might need to commit (not push) your changes first (as described above).::

    git pull

If after update you are seeing some database-related errors - run 'python manage.py migrate'.

If you see some import errors (libraries missing), run::

    pip install -r deployment/requirements.txt

(don't forget 'source ../env/bin/activate'!).

TODO: creating branches

Troubleshooting
===============

* If you are seeing an error::

    ValueError: Unable to configure filter 'require_debug_false': Cannot resolve 'django.utils.log.RequireDebugFalse':
    No module named RequireDebugFalse

  you forgot to activate virtual enviroment::

    source ../env/bin/activate

* If you see ImportError, new libraries might be added in recent commits. In that case you need
  to run

    pip install -r deployment/requirements.txt

* If you see some database errors, try running

    python manage.py migrate

  In case it doesn't help, init_database.sqlite can be copied to database.sqlite to provide
  a ready to use database with some test content.

* TODO: git errors

.. _github docs: http://help.github.com/linux-set-up-git/
