import os.path

from fabric.api import cd, local, run

CODE_DIR_PATH = '/home/serg/sites/grakon'
VIRTUALENV_DIR_PATH = '/home/serg/env/grakon'
REPOSITORY = 'git@github.com:sergkop/grakon.git'

"""
Commands for: restart all services, update code (static files, migrate, restart server, etc.)
"""

def init_system(run=run):
    # TODO: create user serg, home directory, add ssh key of developer to be able to access it,
    #       set bash as default shell, make it sudoer, put ssh key to access git repository from the server
    #       create directories, install required software, add server ip to mysql's server whitelist,
    #       close ports, (add server to load balancer list), configure services (nginx, postfix, etc.)
    #       set files permissions, set .selected_editor, init database (optional)
    run('mkdir -p %s' % CODE_DIR_PATH)
    run('mkdir -p %s' % VIRTUALENV_DIR_PATH)

    ubuntu_packages = [
        # Python
        'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

        # Utils
        'git', 'mc',

        # Services
        'nginx', 'postfix',

        # Libraries
        'libmysqlclient-dev', 'libxslt-dev',
    ]

    sudo('aptitude install %s' % ' '.join(ubuntu_packages))

    # TODO: use external configuration file with all passwords, server ips, etc.

def init_system_local():
    init_system(run=local)

def prepare_code(run=run):
    run('git clone %s %s' % (REPOSITORY, CODE_DIR_PATH))

    # Create settings file
    run('cp %s %s' % (
            os.path.join(CODE_DIR_PATH, 'grakon', 'site_settings.py.example'),
            os.path.join(CODE_DIR_PATH, 'grakon', 'site_settings.py')
    ))

    # Create virtualenv
    run('virtualenv --no-site-packages %s' % VIRTUALENV_DIR_PATH)
    run('pip install -r %s' % os.path.join(CODE_DIR_PATH, 'requirements.txt'))

    # TODO: make lxml accessible from virtualenv

    # TODO: configure settings, 

def prepare_code_local():
    prepare_code(run=local)

def host_type():
    run('ls /home/serg/')
    #run('cp -r /home/serg/sites/grakon_site/ /home/serg/tempdata/grakon_site1/')
