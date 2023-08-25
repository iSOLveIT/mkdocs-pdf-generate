from datetime import datetime


def strptime(value: str, format_str: str) -> datetime:
    """
    Parse a datetime object from a string using the specified format.

    :param value: The string representing the datetime value.
    :param format_str: The format string specifying the expected datetime format.
    :return: A datetime object parsed from the input string.
    """
    return datetime.strptime(value, format_str)


def strftime(dt_obj: datetime, format_str: str) -> str:
    """
    Format a datetime object as a string using the specified format.

    :param dt_obj: The datetime object to be formatted.
    :param format_str: The format string specifying the desired output format.
    :return: The formatted datetime string.
    """
    return dt_obj.strftime(format_str)
