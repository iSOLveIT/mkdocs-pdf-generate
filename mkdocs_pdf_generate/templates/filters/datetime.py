from datetime import datetime


def strptime(value: str, fmt) -> datetime:
    return datetime.strptime(value, fmt)


def strftime(value, fmt) -> str:
    return value.strftime(fmt)
