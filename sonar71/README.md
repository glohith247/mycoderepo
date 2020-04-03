Ansible Role: sonar71
=========

A role that sets up Sonarqube 7.1 using a docker compose project.

Wait why are you using virtualbox for molecule?  Well... docker in docker doesn't work the best, so there were tasks that failed because it doesn't have access to the filesystem the same way as outside DnD (aufs failures on docker-compose step).

Requirements
------------

None

Role Variables
--------------

None

Dependencies
------------

This depends on the WSI Docker role

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: sonar71 }
      become: true

License
-------

Proprietary

