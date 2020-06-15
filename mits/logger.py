verbosity = False


def log_host(message):
    if verbosity is True:
        print(f"{message}")


def log_guest(message):
    if verbosity is True:
        print(f"Guest : {message}")
