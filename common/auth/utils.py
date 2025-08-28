import re
from typing import Optional, Tuple


def os_version(  # noqa: WPS210
    user_agent_header: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Получаем ОС и версию клиента из хедеров.

    :param user_agent_header: Строка с User-Agent.

    :returns: Кортеж (os, version)
    """
    regexp_os_version = re.compile(
        r"version: (?P<version>.*\d{1})(\(.*\)|) "
        r"device: (?P<device>.*) OS: (?P<os>\w+)",
    )

    user_agent = re.search(regexp_os_version, user_agent_header)
    if not user_agent:
        return None, None
    version = user_agent.group("version")
    device = user_agent.group("device")
    os_str = user_agent.group("os")
    os_device = f"{os_str}{device}"
    if os_str == "Web":
        os = "Web"
    elif os_str == "iOS":
        os = "iOS"
    elif "Android" in os_device:
        os = "Android"
    else:
        os = None
    return os, version
