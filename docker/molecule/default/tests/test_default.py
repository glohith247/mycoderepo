import os
import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_docker_is_installed(host):
    package = host.package("docker-ce.x86_64")
    assert package.is_installed
    assert package.version.startswith("17")


def test_docker_daemon(host):
    file = host.file("/etc/docker/daemon.json")
    assert file.user == "root"
    assert file.group == "root"
    assert file.mode == 0o644


def test_pip_repo(host):
    pipconf = host.file("/etc/pip.conf")
    assert pipconf.exists
    assert pipconf.contains("snapshotrepo.wsgc.com")


def test_pip_package(host):
    pip_package = host.package("python2-pip")
    assert pip_package.is_installed


@pytest.mark.parametrize("package", [
    "docker-compose"
])
def test_pip_packages_installed(host, package):
    packages = host.pip_package.get_packages()
    assert package in packages


def test_docker_running_and_enabled(host):
    service = host.service("docker")
    assert service.is_running
    assert service.is_enabled


@pytest.mark.parametrize("find_me", [
    "docker-dev.wsgc.com",
    "container-registry.nonprod.wsgc.com"
])
def test_insecure_registry_check(host, find_me):
    daemonconfig = host.file("/etc/docker/daemon.json")
    assert daemonconfig.contains(find_me)
