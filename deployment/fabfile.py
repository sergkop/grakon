import json
import os.path
import StringIO

from fabric.api import cd, env, get, local, prefix, put, run, sudo
from fabric.contrib.files import sed

REPOSITORY = 'git@github.com:sergkop/grakon.git'

# TODO: start using roles
# TODO: command to upgrade requirements.txt packages

def web_server():
    config_path = '/home/serg/data/grakon/passwords/config.json' # TODO: take it as an argument
    env.conf = json.load(open(config_path))

    env.hosts = env.conf['servers'].keys()
    env.passwords = env.conf['servers'] # set passwords for accessing servers

    env.deploy_user = env.conf['username']

    # Paths
    proj_path = env.conf['path'] = os.path.join('/home/%s' % env.deploy_user, env.conf['path']+'/') # project dir
    env.code_path = env.conf['code_path'] = os.path.join(proj_path, 'source/') # source code dir
    env.env_path = env.conf['env_path'] = os.path.join(proj_path, 'env/') # virtualenv dir
    env.manage_path = os.path.join(env.code_path, 'manage.py') # path to manage.py

    # TODO: logs directory should be located on database server
    env.logs_path = env.conf['logs_path'] = os.path.join(proj_path, 'logs/')

    # Static files
    env.static_path = env.conf['static_path'] = os.path.join(proj_path, 'static/')
    env.STATIC_ROOT = env.conf['STATIC_ROOT'] = os.path.join(env.static_path, 'static/')

UBUNTU_PACKAGES = [
    # Python
    'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

    # Utils
    'gcc', 'git', 'graphviz', 'mc', 'htop',

    # Libraries
    'libxslt-dev', 'graphviz-dev', 'python-dev', 'python-pygraphviz',
    'libmemcached-dev', 'postgresql-server-dev-all', # 'libmysqlclient-dev',
    'libjpeg8', 'libjpeg8-dev', 'libfreetype6', 'libfreetype6-dev', 'zlib1g-dev',
]

def virtualenv(command):
    with prefix('source %s' % os.path.join(env.env_path, 'bin', 'activate')):
        cmd(command)

def cmd(command):
    # TODO: solve 'mesg: /dev/pts/1: Operation not permitted' issue
    return sudo(command, user=env.deploy_user)

# TODO: option - is root the owner of the file
def file_from_template(template_path, dest_path, data):
    template = StringIO.StringIO()
    get(template_path, template)
    put(StringIO.StringIO(template.getvalue() % data), dest_path)

# TODO: run it on the server with another role
# TODO: configure db backups
# Use 'sudo su postgres', 'dropdb %s' and 'dropuser %s' to clean db; 'deluser --remove-home' to remove linux user
def init_data_server():
    ubuntu_packages = ['postgresql', 'postgresql-client', 'memcached', 'rabbitmq-server']

    sudo('aptitude -y install %s' % ' '.join(ubuntu_packages))

    sudo('createuser -l -E -S -D -R %s' % env.conf['database.USER'], user='postgres')
    sudo('createdb -O %s %s' % (env.conf['database.USER'], env.conf['database.NAME']), user='postgres')

    postgres_conf = {
        'client_encoding': "'UTF8'",
        'default_transaction_isolation': "'read committed'",
        'timezone': "'UTC'",
    }

    for param, value in postgres_conf.iteritems():
        sudo('echo "ALTER ROLE %s in DATABASE %s SET %s = %s;" | psql' % (
                env.conf['database.USER'], env.conf['database.NAME'], param, value), user='postgres')

    sudo("echo \"ALTER USER %s WITH PASSWORD '%s';\" | psql" % (
            env.conf['database.USER'], env.conf['database.PASSWORD']), user='postgres')

def init_system():
    # TODO: block password access (for all accounts), add server ip to mysql's server whitelist,
    #       close ports, activate firewall, add server to load balancer list, reboot server after upgrade (optional),
    #       set files permissions, install sentry

    # Install libraries and applications
    ubuntu_packages = UBUNTU_PACKAGES + [
        # Services
        'nginx',
    ]
    sudo('aptitude -y update')
    sudo('aptitude -y upgrade')
    sudo('aptitude -y install %s' % ' '.join(ubuntu_packages))

    # TODO: this user can't switch to sudoer mode
    # Create user
    sudo('useradd -s /bin/bash -d /home/%(user)s -m %(user)s -p %(password)s' % {
            'user': env.deploy_user, 'password': env.passwords[env.host_string]})

    # Set default text editor
    cmd('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /home/%s/.selected_editor' % env.deploy_user)
    sudo('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /root/.selected_editor')

    # Make user sudoer
    sudo('echo "%s ALL=(ALL:ALL) ALL" >> /etc/sudoers' % env.deploy_user)

    # Generate ssh key
    cmd('mkdir /home/%s/.ssh' % env.deploy_user)
    cmd('ssh-keygen -t rsa -f /home/%s/.ssh/id_rsa -N %s -C "%s"' % (
            env.deploy_user, env.conf['SSH_KEY_PASSPHRASE'], env.conf['GITHUB_EMAIL']))

    print "\033[92mCopy the following public key and add it to the list of deploy keys on github (https://github.com/sergkop/grakon/admin/keys)\033[0m"
    cmd('cat /home/%s/.ssh/id_rsa.pub' % env.deploy_user)

    # TODO: stop here to wait while key is added to github
    # Test access to repo
    # TODO: this command causes error
    cmd('ssh -T git@github.com') # TODO: make sure this test is positive

    # Add developers ssh keys to access account
    cmd('echo "%s" >> /home/%s/.ssh/authorized_keys' % ('\n'.join(env.conf['developers_ssh_pubkey']), env.deploy_user))

def restart_web_server():
    sudo('/etc/init.d/nginx restart')
    sudo(os.path.join(env.code_path, 'deployment', 'server.sh'))

    # TODO: commands for data server
    # sudo('/etc/init.d/postgresql restart')
    sudo('/etc/init.d/memcached restart')

    # TODO: start supervisord if not started
    # TODO: restart celery (via superuserd?) - no root

def init_db():
    virtualenv('python %s syncdb --all' % env.manage_path) # TODO: don't create superuser before migrate
    virtualenv('python %s migrate --fake' % env.manage_path)
    virtualenv('python %s import_locations' % env.manage_path)

def prepare_code():
    env.user = env.deploy_user # TODO: do we need it?

    cmd('mkdir -p %s %s %s %s' % (
            env.code_path, env.env_path, env.STATIC_ROOT,
            os.path.join(env.logs_path, 'superuserd'))
    )

    cmd('git clone %s %s' % (REPOSITORY, env.code_path))
    # TODO: detect if requirements.txt was updated in git pull and run pip install -r requirements.txt
    # TODO: how to pass ssh-key password?

    # TODO: move updating settings to separate method + do backup
    # Create settings file
    file_from_template(os.path.join(env.code_path, 'grakon', 'site_settings.py.template'),
            os.path.join(env.code_path, 'grakon', 'site_settings.py'), env.conf)
    # TODO: site_settings.py is owned by root

    # Create virtualenv
    cmd('virtualenv --no-site-packages %s' % env.env_path)

    # TODO: pygraphviz may require creating soft link to be used in virtualenv
    virtualenv('pip install -r %s' % os.path.join(env.code_path, 'deployment', 'requirements.txt'))

    # PIL requires custom installation to activate JPEG support
    virtualenv('pip install -I pil --no-install')
    sed(os.path.join(env.env_path, 'build', 'pil', 'setup.py'),
            '# standard locations',
            'add_directory(library_dirs, "/usr/lib/x86_64-linux-gnu")')
    virtualenv('pip install -I pil --no-download')

    # fcgi starting script
    server_sh_path = os.path.join(env.code_path, 'deployment', 'server.sh')
    file_from_template(os.path.join(env.code_path, 'deployment', 'templates', 'server.sh.template'),
            server_sh_path, env.conf)
    sudo("chmod +x %s" % server_sh_path)

    # superuserd config file
    file_from_template(os.path.join(env.code_path, 'deployment', 'templates', 'supervisor.conf.template'),
            os.path.join(env.code_path, 'deployment', 'supervisor.conf'), env.conf)

    # TODO: change socket file owner to nginx user (www-data)

    # TODO: uwsgi deployment

    # Nginx configuration
    sudo('cp /etc/nginx/nginx.conf /etc/nginx/nginx-prev.conf')
    file_from_template(os.path.join(env.code_path, 'deployment', 'templates', 'nginx.conf.template'),
            '/etc/nginx/nginx.conf', env.conf)

    deploy_static_files()

# TODO: all static files must be hosted on one server
def deploy_static_files():
    # TODO: delete old files (?), minify static files
    virtualenv('python %s collectstatic -c --noinput' % env.manage_path)
    virtualenv('cp %sfavicon.ico %sfavicon.ico' % (env.STATIC_ROOT, env.static_path))
    virtualenv('cp %s %srobots.txt' % (
            os.path.join(env.code_path, 'grakon', 'templates', 'robots.txt'), env.static_path))
    virtualenv('python %s code_data %sjs/code_data.js' % (env.manage_path, env.STATIC_ROOT))

# TODO: optionally run pip install -r requirements.txt (with upgrade?)
def update_code():
    # TODO: perform db backup
    with cd(env.code_path):
        cmd('git pull')
    virtualenv('python %s migrate' % env.manage_path)
    deploy_static_files()
    restart_web_server()

def developer_init():
    code_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.abspath(os.path.join(code_path, '..', 'env'))

    packages = UBUNTU_PACKAGES + ['rabbitmq-server']
    local('sudo aptitude -y install %s' % ' '.join(packages))

    # Copy settings file
    local('cp %s %s' % (os.path.join(code_path, 'grakon', 'site_settings.py.example'),
            os.path.join(code_path, 'grakon', 'site_settings.py')))

    # Create virtualenv
    local('virtualenv --no-site-packages %s' % env_path)

    virtualenv_cmd = "/bin/bash -l -c 'source %s && %%s'" % \
            os.path.join(env_path, 'bin', 'activate')

    # TODO: pygraphviz may require creating soft link to be used in virtualenv
    local(virtualenv_cmd % ('pip install -r %s' % os.path.join(code_path, 'deployment', 'requirements.txt')))

    # PIL requires custom installation to activate JPEG support
    local(virtualenv_cmd % 'pip install -I pil --no-install')

    # Insert line in setup.py
    setuppy_path = os.path.join(env_path, 'build', 'pil', 'setup.py')
    lines = list(open(setuppy_path).readlines())
    line_index = [i for i in range(len(lines)) if '# standard locations' in lines[i]][0]
    lines.insert(line_index+1, '        add_directory(library_dirs, "/usr/lib/x86_64-linux-gnu")\n')
    open(setuppy_path, 'w').writelines(lines)

    local(virtualenv_cmd % 'pip install -I pil --no-download')

    # Copy database file
    local('cp %s %s' % (os.path.join(code_path, 'init_database.sqlite'),
            os.path.join(code_path, 'database.sqlite')))
