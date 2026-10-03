from pathlib import Path

import pytest

from migration_v3.config import MySQLConfigError, load_mysql_config


COMPLETE_ENVIRONMENT = {
    "OPTIMUS_MYSQL_HOST": "127.0.0.1",
    "OPTIMUS_MYSQL_PORT": "3307",
    "OPTIMUS_MYSQL_DATABASE": "optimus_sun_v3_test",
    "OPTIMUS_MYSQL_USER": "environment-user",
    "OPTIMUS_MYSQL_PASSWORD": "environment-password",
}


def _write_env(path, values):
    lines = [f"{name}={value}" for name, value in values.items()]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_loads_configuration_from_explicit_env_file(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, COMPLETE_ENVIRONMENT)

    config = load_mysql_config(env_file=env_file, environ={})

    assert config == {
        "host": "127.0.0.1",
        "port": 3307,
        "database": "optimus_sun_v3_test",
        "user": "environment-user",
        "password": "environment-password",
        "ssl_ca": None,
    }


def test_process_environment_precedes_env_file(tmp_path):
    env_file = tmp_path / ".env"
    file_values = {name: "file-value" for name in COMPLETE_ENVIRONMENT}
    file_values["OPTIMUS_MYSQL_PORT"] = "3306"
    _write_env(env_file, file_values)

    config = load_mysql_config(env_file=env_file, environ=COMPLETE_ENVIRONMENT)

    assert config["host"] == "127.0.0.1"
    assert config["port"] == 3307
    assert config["password"] == "environment-password"


def test_defined_empty_environment_value_does_not_fall_back_to_file(tmp_path):
    env_file = tmp_path / ".env"
    _write_env(env_file, COMPLETE_ENVIRONMENT)
    environment = dict(COMPLETE_ENVIRONMENT)
    environment["OPTIMUS_MYSQL_PASSWORD"] = ""

    with pytest.raises(MySQLConfigError) as caught:
        load_mysql_config(env_file=env_file, environ=environment)

    assert str(caught.value) == "Configuração MySQL ausente: OPTIMUS_MYSQL_PASSWORD"


def test_reports_only_missing_variable_names(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPTIMUS_MYSQL_HOST=secret-host\n", encoding="utf-8")

    with pytest.raises(MySQLConfigError) as caught:
        load_mysql_config(env_file=env_file, environ={})

    message = str(caught.value)
    assert "OPTIMUS_MYSQL_PORT" in message
    assert "OPTIMUS_MYSQL_DATABASE" in message
    assert "OPTIMUS_MYSQL_USER" in message
    assert "OPTIMUS_MYSQL_PASSWORD" in message
    assert "secret-host" not in message


@pytest.mark.parametrize("port", ["not-a-number", "0", "65536"])
def test_invalid_port_error_never_includes_the_value(tmp_path, port):
    env_file = tmp_path / ".env"
    values = dict(COMPLETE_ENVIRONMENT)
    values["OPTIMUS_MYSQL_PORT"] = port
    _write_env(env_file, values)

    with pytest.raises(MySQLConfigError) as caught:
        load_mysql_config(env_file=env_file, environ={})

    assert str(caught.value) == "Configuração MySQL inválida: OPTIMUS_MYSQL_PORT"
    assert port not in str(caught.value)


def test_supports_comments_export_and_quoted_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# local only\n"
        "export OPTIMUS_MYSQL_HOST='localhost'\n"
        "OPTIMUS_MYSQL_PORT=3306 # standard port\n"
        "OPTIMUS_MYSQL_DATABASE=optimus_sun_v3_test\n"
        "OPTIMUS_MYSQL_USER=demo\n"
        'OPTIMUS_MYSQL_PASSWORD="fictitious password"\n',
        encoding="utf-8",
    )

    config = load_mysql_config(env_file=env_file, environ={})

    assert config["host"] == "localhost"
    assert config["port"] == 3306
    assert config["password"] == "fictitious password"


def test_malformed_file_error_does_not_echo_its_content(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("sensitive malformed line\n", encoding="utf-8")

    with pytest.raises(MySQLConfigError) as caught:
        load_mysql_config(env_file=env_file, environ={})

    assert str(caught.value) == "Arquivo .env inválido na linha 1."
    assert "sensitive" not in str(caught.value)


def test_remote_host_requires_ca_without_echoing_host(tmp_path):
    env_file = tmp_path / ".env"
    values = dict(COMPLETE_ENVIRONMENT)
    values["OPTIMUS_MYSQL_HOST"] = "database.internal.example"
    _write_env(env_file, values)

    with pytest.raises(MySQLConfigError) as caught:
        load_mysql_config(env_file=env_file, environ={})

    assert str(caught.value) == "Configuração MySQL ausente: OPTIMUS_MYSQL_SSL_CA"
    assert "database.internal.example" not in str(caught.value)


def test_remote_host_accepts_explicit_ca_setting(tmp_path):
    env_file = tmp_path / ".env"
    values = dict(COMPLETE_ENVIRONMENT)
    values["OPTIMUS_MYSQL_HOST"] = "database.internal.example"
    values["OPTIMUS_MYSQL_SSL_CA"] = "C:/certificates/mysql-ca.pem"
    _write_env(env_file, values)

    config = load_mysql_config(env_file=env_file, environ={})

    assert config["ssl_ca"] == "C:/certificates/mysql-ca.pem"


def test_double_quoted_literal_backslash_is_not_unescaped_twice(tmp_path):
    env_file = tmp_path / ".env"
    values = dict(COMPLETE_ENVIRONMENT)
    del values["OPTIMUS_MYSQL_PASSWORD"]
    _write_env(env_file, values)
    with env_file.open("a", encoding="utf-8") as stream:
        stream.write('OPTIMUS_MYSQL_PASSWORD="literal\\\\nvalue"\n')

    config = load_mysql_config(env_file=env_file, environ={})

    assert config["password"] == r"literal\nvalue"
