from datetime import date, datetime


def strptime(value: str, fmt) -> date:
    return datetime.strptime(value, fmt)


def strftime(value, fmt) -> str:
    return value.strftime(fmt)
