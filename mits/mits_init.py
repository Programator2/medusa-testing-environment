import yaml
import remote_shell
import test_settings
import time
from logger import log_host
#from virtual import remote_start_guest_machine


def main(args):
    with open("config.yaml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    guest_conn_info = config['guest_connection']

    test_settings.init(config['host_settings'])
    is_host_virtual_machine = config['host_settings']['is_virtual_machine']
    if not is_host_virtual_machine:
        remote_start_guest_machine()

    log_host('Starting SSH conection')
    ssh = remote_shell.create_session(guest_conn_info)
    is_updated = remote_shell.pull_latest_git_version(
                                         ssh,
                                         config['guest_medusa'],
                                         config['guest_connection']['password']
                                         )
    if is_updated and is_host_virtual_machine is False:
        ssh = wait_for_reset_and_create_new_ssh_session(guest_conn_info)

    override_config_options(config, args)
    make_subconfig(config)
    remote_shell.start_testing(ssh, args['category'],
                               config['guest_paths']['scripts'],
                               config['testing_authserver'])


def wait_for_reset_and_create_new_ssh_session(conn_info):
    time.sleep(60)
    return remote_shell.create_session(conn_info)


def override_config_options(config, args):
    """
    The function is responsible for overriding loaded config if there are some
    user-specified options, which should be overriden
    @param config: (dict) loaded instance with settings
    @param args: (dict) user-specified settings to be overriden
    """
    chosen_authserver = args.get('authserver', None)
    if chosen_authserver in config['authserver'].keys():
        config['testing_authserver'] = chosen_authserver

    verbosity = args.get('verbose', False)
    if verbosity is True:
        config['guest_settings']['verbose'] = True


def make_subconfig(config):
    """
    Make subconfig for guest machine from given config
    @param config: (dict) loaded config
    """
    chosen_authserver = config['testing_authserver']

    subconfig = {}
    subconfig['authserver'] = config['authserver'][chosen_authserver]
    subconfig['paths'] = config['guest_paths']
    subconfig['settings'] = config['guest_settings']
    subconfig['testing_options'] = config['testing_options']

    yamlContent = yaml.dump(subconfig, Dumper=yaml.Dumper)
    with open("guest_scripts/subconfig.yaml", "w") as f:
        f.write(yamlContent)


if __name__ == '__main__':
    main()
