import logger

def init(config):
    """
    Initialization of test settings
    @param config: (dict) deserialized settings from config
    """
    logger.verbosity = config['verbose']
