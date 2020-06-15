import yaml
import remote_shell
from logger import log_host
# from virtual import start_machine


def main(args):
    with open("config.yaml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    # start_machine()
    log_host('Starting SSH conection')
    # if (remote_shell.connect(argv[0]) == 1):
    #    time.sleep(60)
    #    remote_shell.connect(argv[0])
    ssh = remote_shell.create_session(config['guest_connection'])
    remote_shell.pull_latest_git_version(ssh, config['guest_medusa'],
                                         config['guest_connection']['password']
                                         )

    make_subconfig(config, args)
    remote_shell.start_testing(ssh, args['category'],
                               config['guest_paths']['scripts'],
                               config['authserver']['default'])


def make_subconfig(config, args):
    chosen_authserver = args.get('authserver', None)

    if chosen_authserver not in config['authserver'].keys():
        chosen_authserver = config['authserver']['default']

    subconfig = {}
    subconfig['authserver'] = config['authserver'][chosen_authserver]
    subconfig['paths'] = config['guest_paths']
    subconfig['settings'] = config['guest_settings']

    yamlContent = yaml.dump(subconfig, Dumper=yaml.Dumper)
    with open("guest_scripts/subconfig.yaml", "w") as f:
        f.write(yamlContent)


if __name__ == '__main__':
    main()
