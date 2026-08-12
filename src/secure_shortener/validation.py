import ipaddress
import socket
from collections.abc import Callable, Iterable
from urllib.parse import urlparse

Resolver = Callable[[str], Iterable[str]]


def system_resolver(host: str) -> Iterable[str]:
    return {info[4][0] for info in socket.getaddrinfo(host, None)}


def validate_destination(value: str, resolver: Resolver = system_resolver) -> str:
    if len(value) > 2048:
        raise ValueError("destination exceeds 2048 characters")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("destination must use http or https")
    if parsed.username or parsed.password:
        raise ValueError("destination must not contain credentials")
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("local destinations are not allowed")
    try:
        addresses = (
            [ipaddress.ip_address(host)]
            if not _is_hostname(host)
            else [ipaddress.ip_address(a) for a in resolver(host)]
        )
    except (ValueError, OSError, socket.gaierror) as exc:
        raise ValueError("destination host could not be resolved") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("destination must resolve only to global addresses")
    return value


def _is_hostname(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return True
    return False
