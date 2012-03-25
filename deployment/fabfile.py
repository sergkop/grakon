import os.path

from fabric.api import cd, env, local, prefix, run, sudo

# TODO: set env attributes like in http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user

CODE_DIR_PATH = '/home/serg/sites/grakon'
VIRTUALENV_DIR_PATH = '/home/serg/env/grakon'
REPOSITORY = 'git@github.com:sergkop/grakon.git'

# TODO: Commands for: restart all services, update code (static files, migrate, restart server, etc.)

def virtualenv(command):
    with prefix('source %s' % os.path.join(VIRTUALENV_DIR_PATH, 'bin', 'activate')):
        run(command)

def init_system():
    # TODO: create user serg, home directory, add ssh key of developer to be able to access it,
    #       set bash as default shell, make it sudoer, put ssh key to access git repository from the server
    #       create directories, install required software, add server ip to mysql's server whitelist,
    #       close ports, activate firewall, (add server to load balancer list), configure services (nginx, postfix, etc.)
    #       set files permissions, set .selected_editor, init database (optional), install sentry,
    #       minify static files, set different cache time headers for static files
    run('mkdir -p %s' % CODE_DIR_PATH)
    run('mkdir -p %s' % VIRTUALENV_DIR_PATH)

    ubuntu_packages = [
        # Python
        'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

        # Utils
        'gcc', 'git', 'graphviz', 'mc',

        # Services
        'nginx', #'postfix',

        # Libraries
        'libmysqlclient-dev', 'libxslt-dev', 'graphviz-dev', # python-dev?
    ]

    sudo('aptitude install %s' % ' '.join(ubuntu_packages))

    # TODO: use external configuration file with all passwords, server ips, etc.

def prepare_code():
    # TODO: if code is already there - make git pull and update it
    run('git clone %s %s' % (REPOSITORY, CODE_DIR_PATH))

    # Create settings file
    run('cp %s %s' % (
            os.path.join(CODE_DIR_PATH, 'grakon', 'site_settings.py.example'),
            os.path.join(CODE_DIR_PATH, 'grakon', 'site_settings.py')
    ))
    # TODO: configure settings

    # Create virtualenv
    run('virtualenv --no-site-packages %s' % VIRTUALENV_DIR_PATH)

    virtualenv('pip install -r %s' % os.path.join(CODE_DIR_PATH, 'deployment', 'requirements.txt'))

def host_type():
    run('source /home/serg/env/grakon/bin/activate')
    #run('ls /home/serg/')
    #run('cp -r /home/serg/sites/grakon_site/ /home/serg/tempdata/grakon_site1/')
