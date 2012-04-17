import json
import os.path
import StringIO

from fabric.api import cd, env, get, local, prefix, put, run, sudo

REPOSITORY = 'git@github.com:sergkop/grakon.git'
CONFIG_FILE_PATH = '/home/serg/data/grakon/passwords/config.json' # TODO: take it as an argument

# TODO: set env attributes like in http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user
# TODO: start using roles

conf = json.load(open(CONFIG_FILE_PATH))

USERNAME = conf['username']

env.hosts = conf['servers'].keys()
env.passwords = conf['servers'] # set passwords for accessing servers

conf['path'] = os.path.join('/home/%s' % USERNAME, conf['path']+'/')
conf['code_path'] = os.path.join(conf['path'], 'source/')
conf['env_path'] = os.path.join(conf['path'], 'env/')
conf['static_path'] = os.path.join(conf['path'], 'static/')

def virtualenv(command):
    with prefix('source %s' % os.path.join(conf['env_path'], 'bin', 'activate')):
        cmd(command)

def cmd(command):
    # TODO: solve 'mesg: /dev/pts/1: Operation not permitted'
    return sudo(command, user=USERNAME)

# TODO: option - is root the owner of the file
def file_from_template(template_path, dest_path):
    template = StringIO.StringIO()
    get(template_path, template)
    put(StringIO.StringIO(template.getvalue() % conf), dest_path)

# TODO: run it on the server with another role
# Use 'dropdb %s' and 'dropuser %s' to clean db; 'deluser --remove-home' to remove linux user
def init_data_server():
    ubuntu_packages = ['postgresql', 'postgresql-client', 'memcached']

    sudo('aptitude -y install %s' % ' '.join(ubuntu_packages))

    sudo('createuser -l -E -S -D -R %s' % conf['database.USER'], user='postgres')
    sudo('createdb -O %s %s' % (conf['database.USER'], conf['database.NAME']), user='postgres')

    postgres_conf = {
        'client_encoding': "'UTF8'",
        'default_transaction_isolation': "'read committed'",
        'timezone': "'UTC'",
    }

    for param, value in postgres_conf.iteritems():
        sudo('echo "ALTER USER %s in DATABASE %s SET %s = %s;" | psql' % (
                conf['database.USER'], conf['database.NAME'], param, value), user='postgres')

    sudo("echo \"ALTER USER %s WITH PASSWORD '%s';\" | psql" % (
            conf['database.USER'], conf['database.PASSWORD']), user='postgres')

def init_system():
    # TODO: block password access (for all accounts), add server ip to mysql's server whitelist,
    #       close ports, activate firewall, add server to load balancer list, reboot server after upgrade (optional),
    #       set files permissions, install sentry

    # Install libraries and applications
    ubuntu_packages = [
        # Python
        'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

        # Utils
        'gcc', 'git', 'graphviz', 'mc', 'htop',

        # Services
        'nginx',

        # Libraries
        'libxslt-dev', 'graphviz-dev', 'python-dev', 'python-pygraphviz',
        'libmemcached-dev', 'postgresql-server-dev-all', # 'libmysqlclient-dev',
    ]

    sudo('aptitude -y update')
    sudo('aptitude -y upgrade')
    sudo('aptitude -y install %s' % ' '.join(ubuntu_packages))

    # TODO: this user can't switch to sudoer mode
    # Create user
    sudo('useradd -s /bin/bash -d /home/%(user)s -m %(user)s -p %(password)s' % {
            'user': USERNAME, 'password': env.passwords[env.host_string]})

    # Set default text editor
    cmd('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /home/%s/.selected_editor' % USERNAME)
    sudo('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /root/.selected_editor')

    # Make user sudoer
    sudo('echo "%s ALL=(ALL:ALL) ALL" >> /etc/sudoers' % USERNAME)

    # Generate ssh key
    cmd('mkdir /home/%s/.ssh' % USERNAME)
    cmd('ssh-keygen -t rsa -f /home/%s/.ssh/id_rsa -N %s -C "%s"' % (
            USERNAME, conf['SSH_KEY_PASSPHRASE'], conf['GITHUB_EMAIL']))

    # TODO: automate it (or change text color)
    print "Copy the following public key and add it to the list of deploy keys on github (https://github.com/sergkop/grakon/admin/keys)"
    cmd('cat /home/%s/.ssh/id_rsa.pub' % USERNAME)

    # Test access to repo
    cmd('ssh -T git@github.com') # TODO: make sure this test is positive

    # Add developers ssh keys to access account
    cmd('echo "%s" >> /home/%s/.ssh/authorized_keys' % ('\n'.join(conf['developers_ssh_pubkey']), USERNAME))

    # Nginx configuration
    sudo('cp /etc/nginx/nginx.conf /etc/nginx/nginx-prev.conf')
    file_from_template(os.path.join(code_path, 'deployment', 'nginx.conf.template'),
            '/etc/nginx/nginx.conf')

def restart_web_server():
    sudo('/etc/init.d/nginx restart')
    sudo(os.path.join(conf['code_path'], 'deployment', 'server.sh'))

    # TODO: commands for data server
    # sudo('/etc/init.d/postgresql restart')
    # sudo('/etc/init.d/memcached restart')

def init_db():
    manage_path = os.path.join(code_path, 'manage.py')
    cmd('python %s syncdb' % manage_path)
    cmd('python %s migrate --fake' % manage_path)
    cmd('python %s import_locations' % manage_path)

def prepare_code():
    env.user = USERNAME # TODO: do we need it?

    cmd('mkdir -p %s %s %s' % (conf['code_path'], conf['env_path'], conf['static_path']))

    cmd('git clone %s %s' % (REPOSITORY, conf['code_path']))

    # TODO: move updating settings to separate method + do backup
    # Create settings file
    file_from_template(os.path.join(conf['code_path'], 'grakon', 'site_settings.py.template'),
            os.path.join(conf['code_path'], 'grakon', 'site_settings.py'))
    # TODO: site_settings.py is owned by root

    # Create virtualenv
    cmd('virtualenv --no-site-packages %s' % conf['env_path'])

    # TODO: pygraphviz may require creating soft link to be used in virtualenv
    virtualenv('pip install -r %s' % os.path.join(conf['code_path'], 'deployment', 'requirements.txt'))

    # fcgi starting script
    file_from_template(os.path.join(conf['code_path'], 'deployment', 'server.sh.template'),
            os.path.join(conf['code_path'], 'deployment', 'server.sh'))
    # TODO: make it executable?

    # TODO: configure socket file (?)

def update_code():
    # TODO: make git pull
    # TODO: python manage.py migrate
    # TODO: delete old files, minify static files, move them to proper dir (use django command) (static/static)
    # TODO: favicon

    restart_web_server()
