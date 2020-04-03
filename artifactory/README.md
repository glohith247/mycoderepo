Ansible Role: artifactory
=========

A role that sets up artifactory 6.x

Requirements
------------

None

Role Variables
--------------

- artifactory_database: mysql(default is derby)
- repo_type: snapshot(ex: snapshot, release, cacheab, cacherk)

Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: artifactory }
      become: true

License
-------

Proprietary
