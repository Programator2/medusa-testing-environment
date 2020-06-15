import yaml
import remote_shell
import test_settings
from logger import log_host
# from virtual import start_machine


def main(args):
    with open("config.yaml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    test_settings.init(config['host_settings'])
    # start_machine()
    log_host('Starting SSH conection')
    # if (remote_shell.connect(argv[0]) == 1):
    #    time.sleep(60)
    #    remote_shell.connect(argv[0])
    ssh = remote_shell.create_session(config['guest_connection'])
    remote_shell.pull_latest_git_version(ssh, config['guest_medusa'],
                                         config['guest_connection']['password']
                                         )

    override_config_options(config, args)
    make_subconfig(config)
    remote_shell.start_testing(ssh, args['category'],
                               config['guest_paths']['scripts'],
                               config['testing_authserver'])


def override_config_options(config, args):
    chosen_authserver = args.get('authserver', None)
    if chosen_authserver in config['authserver'].keys():
        config['testing_authserver'] = chosen_authserver

    verbosity = args.get('verbose', False)
    if verbosity is True:
        config['guest_settings']['verbose'] = True


def make_subconfig(config):
    chosen_authserver = config['testing_authserver']

    subconfig = {}
    subconfig['authserver'] = config['authserver'][chosen_authserver]
    subconfig['paths'] = config['guest_paths']
    subconfig['settings'] = config['guest_settings']

    yamlContent = yaml.dump(subconfig, Dumper=yaml.Dumper)
    with open("guest_scripts/subconfig.yaml", "w") as f:
        f.write(yamlContent)


if __name__ == '__main__':
    main()
