from config import SDRConfig

config = SDRConfig()


def debug(flag: str) -> bool:
    return getattr(config, flag, False)
