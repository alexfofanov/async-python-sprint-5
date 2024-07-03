import uuid
from datetime import UTC, datetime


def aware_utcnow() -> datetime:
    """
    Получение времени в UTC с указанием временной зоны
    """

    return datetime.now(UTC)


def naive_utcnow() -> datetime:
    """
    Получение времени в UTC без указания временной зоны
    """

    return aware_utcnow().replace(tzinfo=None)


def is_uuid(str_to_test, version=4) -> bool:
    """
    Проверка UUID
    """

    try:
        uuid.UUID(str_to_test, version=version)
    except ValueError:
        return False

    return True
