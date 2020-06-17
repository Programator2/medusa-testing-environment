verbosity = False


def log_host(message):
    """
    Logging function used in host machine
    """
    if verbosity is True:
        print(f"{message}")


def log_guest(message):
    """
    Logging function used in guest machine
    """
    if verbosity is True:
        print(f"Guest : {message}")
