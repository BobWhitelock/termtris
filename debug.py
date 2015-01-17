import config

def debug(*args):
    if config.DEBUG:
        print(*args)