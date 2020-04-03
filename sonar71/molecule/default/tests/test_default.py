import os
import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_sonar_user(host):
    sonar = host.user("sonar")
    assert "docker" in sonar.groups


@pytest.mark.parametrize("path", [
    "/apps/sonarqube/", "/apps/postgresql/",
    "/apps/backups",
    "/apps/sonarqube/docker-compose/",
    "/apps/"
])
def test_app_directories_with_ownership(host, path):
    directory = host.file(path)
    assert directory.exists
    assert directory.user == "sonar"
    assert directory.group == "sonar"


@pytest.mark.parametrize("path", [
    "/apps/sonarqube/extensions/", "/apps/sonarqube/conf/"
])
def test_app_directories_without_ownership(host, path):
    directory = host.file(path)
    assert directory.exists


def test_docker_compose_file(host):
    file_location = "/apps/sonarqube/docker-compose/docker-compose.yml"
    docker_compose_file = host.file(file_location)
    assert docker_compose_file.exists


def test_http_package_installed(host):
    package = host.package("nginx")
    assert package.is_installed
    assert package.version.startswith("1.12")


@pytest.mark.parametrize("path", [
    "/etc/ssl/private/",
    "/etc/ssl/certs/"
])
def test_ssl_directories(host, path):
    directory = host.file(path)
    assert directory.exists
    assert directory.user == "root"
    assert directory.group == "root"


def test_nginx_default_site_disabled(host):
    default_config = host.file("/etc/nginx/nginx.conf")
    assert not default_config.contains("server")


def test_ssl_certs(host):
    private_key = host.file("/etc/ssl/private/sonarqube.wsgc.com.key")
    assert private_key.contains("BEGIN RSA PRIVATE KEY")
    assert private_key.contains("MIIEpA")
