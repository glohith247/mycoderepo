Ansible Role: docker
=========

A brief description of the role goes here.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here.

Role Variables
--------------

`defaults/main.yml` contains the following variables

```
docker_package: docker-ce-17.09.0.ce-1.el7.centos.x86_64
docker_daemon_data_path: "/apps/data/docker"
docker_daemon_insecure_registry: "harbor.services.labs.wsgc.com"
```

`docker_package` must be uploaded to artifactory before it'll work (it's there... just an FYI if any updates are needed)
`docker_daemon_data_path` is used when creating the docker daemon config file to specifiy where docker data goes
`docker_daemon_insecure_registry` is used to specify an insecure registry

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      become: true
      roles:
         - { role: docker }

License
-------

Proprietary

