"""Secure local configuration for the MySQL v3 migration tools.

The process environment always wins over values from the local ``.env`` file.
This module deliberately has no dependency on python-dotenv so the migration
utilities can validate their configuration before importing the MySQL driver.
"""

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = ROOT / ".env"

MYSQL_ENVIRONMENT = {
    "host": "OPTIMUS_MYSQL_HOST",
    "port": "OPTIMUS_MYSQL_PORT",
    "database": "OPTIMUS_MYSQL_DATABASE",
    "user": "OPTIMUS_MYSQL_USER",
    "password": "OPTIMUS_MYSQL_PASSWORD",
}
MYSQL_OPTIONAL_ENVIRONMENT = {
    "ssl_ca": "OPTIMUS_MYSQL_SSL_CA",
}
_LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}

_ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class MySQLConfigError(RuntimeError):
    """Raised for missing or invalid MySQL configuration."""


def _unquote(value, line_number):
    if not value or value[0] not in ("'", '"'):
        return value.split(" #", 1)[0].rstrip()

    quote = value[0]
    escaped = False
    end = None
    for index, character in enumerate(value[1:], start=1):
        if quote == '"' and character == "\\" and not escaped:
            escaped = True
            continue
        if character == quote and not escaped:
            end = index
            break
        escaped = False

    trailing = "" if end is None else value[end + 1 :].strip()
    if end is None or (trailing and not trailing.startswith("#")):
        raise MySQLConfigError(f"Arquivo .env inválido na linha {line_number}.")

    result = value[1:end]
    if quote == '"':
        replacements = {"\\": "\\", '"': '"', "n": "\n", "r": "\r", "t": "\t"}
        unescaped = []
        index = 0
        while index < len(result):
            if result[index] == "\\" and index + 1 < len(result):
                next_character = result[index + 1]
                if next_character in replacements:
                    unescaped.append(replacements[next_character])
                    index += 2
                    continue
            unescaped.append(result[index])
            index += 1
        result = "".join(unescaped)
    return result


def _read_env_file(path):
    path = Path(path)
    if not path.is_file():
        return {}

    values = {}
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as error:
        raise MySQLConfigError("Não foi possível ler o arquivo .env.") from error

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise MySQLConfigError(f"Arquivo .env inválido na linha {line_number}.")

        name, raw_value = line.split("=", 1)
        name = name.strip()
        if not _ENVIRONMENT_NAME.fullmatch(name):
            raise MySQLConfigError(f"Arquivo .env inválido na linha {line_number}.")
        values[name] = _unquote(raw_value.strip(), line_number)
    return values


def load_mysql_config(env_file=None, environ=None):
    """Load MySQL settings without mutating ``os.environ``.

    A key present in the process environment has precedence even when its value
    is empty. Empty required values are reported as missing by variable name.
    """

    environment = os.environ if environ is None else environ
    file_values = _read_env_file(DEFAULT_ENV_FILE if env_file is None else env_file)
    selected = {
        variable: environment[variable] if variable in environment else file_values.get(variable, "")
        for variable in MYSQL_ENVIRONMENT.values()
    }
    optional = {
        variable: environment[variable] if variable in environment else file_values.get(variable, "")
        for variable in MYSQL_OPTIONAL_ENVIRONMENT.values()
    }

    missing = [variable for variable in MYSQL_ENVIRONMENT.values() if not selected[variable].strip()]
    if missing:
        raise MySQLConfigError("Configuração MySQL ausente: " + ", ".join(missing))

    port_name = MYSQL_ENVIRONMENT["port"]
    try:
        port = int(selected[port_name])
    except (TypeError, ValueError) as error:
        raise MySQLConfigError(f"Configuração MySQL inválida: {port_name}") from error
    if not 1 <= port <= 65535:
        raise MySQLConfigError(f"Configuração MySQL inválida: {port_name}")

    ssl_ca_name = MYSQL_OPTIONAL_ENVIRONMENT["ssl_ca"]
    host = selected[MYSQL_ENVIRONMENT["host"]].strip()
    ssl_ca = optional[ssl_ca_name].strip()
    if host.casefold() not in _LOOPBACK_HOSTS and not ssl_ca:
        raise MySQLConfigError("Configuração MySQL ausente: " + ssl_ca_name)

    return {
        "host": host,
        "port": port,
        "database": selected[MYSQL_ENVIRONMENT["database"]],
        "user": selected[MYSQL_ENVIRONMENT["user"]],
        "password": selected[MYSQL_ENVIRONMENT["password"]],
        "ssl_ca": ssl_ca or None,
    }


def mysql_config_from_env(env_file=None, environ=None):
    """Compatibility name for callers migrating from the original CLI helper."""

    return load_mysql_config(env_file=env_file, environ=environ)
