Ansible
-------
Everything related to Ansible.

# Installing

We're using a virtual environment with Ansible and Molecule, so install is as easy as:

Create the virtual environment by running the following in the root of the repo after checkout

    python3 -m venv venv

To activate the virtual environment run this from the root of the repo

    source venv/bin/activate

To install

    pip install -r requirements.txt

## Using Vagrant

There's a vagrant setup for your dev environment as part of this repo, to use it...

Run `vagrant up` to setup the VM

Run `vagrant ssh` to get into the VM

Run `vagrant reload` if you need to reboot/reload the VM

Run `vagrant destroy` if you need to destroy the VM for any reason

After `vagrant up` builds the vm, you'll need to login to the VM with `vagrant ssh` then login to our docker registry with `docker login docker-dev.wsgc.com`

You can find the repo synced at `/vagrant`

Now you can do all the things :)

# External Dependencies

External dependencies are manage by a `requirements.yml` placed inside the playbook folder.

The below command installs all declared roles inside `ext-roles/`.

```
ansible-galaxy install -r path/to/playbook/requirements.yml -p ext-roles/ --force
```

NOTE: You should **always** run ansible commands from the root directory so that ansible picks the correct [ansible.cfg](http://docs.ansible.com/ansible/latest/intro_configuration.html) (current directory).


# Ansible Version

2.7.1

# Testing

We've adopted [molecule][1] as our method of testing roles and playbooks.  Here's a few tips for working with [molecule][1].

 - Use it to scaffold your new role with `molecule init role --role-name foo`.  This will create all the needed files.
 - If your playbook uses a requirements file, the file needs to be duplicated into `molecule/default/requirements.yml`, unfortunately a symlink doesn't behave as it should
 - When testing a playbook (not a role), you will want to add this stanza to `molecule/default/playbook.yml` to exercise your playbook `- import_playbook: ../../sonar.yml`

Typical steps for execution of tests may be

 1. `molecule create` - this will create the docker environment(s) for testing
 1. `molecule dependency` - this will download any requirements for the playbook automatically
 1. `molecule lint` - this will execute the lint process on the project
 1. `molecule converge` - this executes the ansible playbook/role against the environment(s)
 1. `molecule idempotence` - this executes the playbook/role against the environment(s) with the expectation that nothing changes the 2nd time
 1. `molecule verify` - this runs your unit/integration tests for the playbook/role against the environment(s)

`molecule test` will do all these things in serial, and destroy the environment(s) at the end, but it's probably best to understand the above and use the above in the majority of cases

If you have difficulties getting molecule working on your local, use the `Vagrantfile` included in this repo to provision an ubuntu vm configured to run molecule/docker.

## Docker customization

The standard container for molecule will be centos7, but there may be a need to customize some packages or capabilities of the container for testing purposes.

 - If you need to add additional packages in the docker (not needed by the role/playbook), these can be customized in the appropirate portion of `Dockerfile.j2`.
 - If you need additional capabilities available in the docker container, you'll add that to `molecule.yml`.  For example, for roles that utilize systemd-based services, you will need to add the following to fully enable systemd:

```
    privileged: true
    command: /usr/sbin/init
    capabilities:
      - SYS_PTRACE
```
 - If you need to expose ports for testing, you'll need to add that to `create.yml` so its done on every environment, as well as `molecule.yml` for every instance of the environment.  For example:

`create.yml`
```
    - name: Create molecule instance(s)
      docker_container:
        ...stuff...
        ports: "{{ item.ports | default(omit) }}"
```

`molecule.yml`
```
platforms:
  - name: instance
    image: centos:7
    ...stuff...
    ports:
      - 9000:9000
```

 - If testing a playbook, you'll need to add the inventory targeted in the playbook to the instance (sonar in my example)

`molecule.yml`
```
platforms:
  - name: instance
    image: centos:7
    ...stuff...
    groups:
      - sonar
```

# Enrypting / Decrypting variables

We use [Ansible Vault](https://docs.ansible.com/ansible/2.4/vault.html) to maintain sensitive information such as passwords.

You should run all vault commands from the root folder of this repository, otherwise you'll need to specify a vault password file.

Encrypting a variable:

```
echo -n 'mysecret' | ansible-vault encrypt_string --name --stdin-name
```

Decrypting a variable (Remove tabs and spaces):

```
echo '$ANSIBLE_VAULT;1.1;AES256
66316261313864356265383538313934393966356465333235656664343738613537316661356432
6162373762313731306464313232306539386666306666370a623236356666663739666666343438
61613137626132646466393664363435326565396135333832313538393336346239326439313738
6636643333633131350a393830373536313338383032373130383536383330643564343766386463
3331' | ansible-vault decrypt /dev/stdin --output=/dev/stderr > /dev/null
```

# Further Reading

See [Ansible at WSI](https://confluence.wsgc.com/display/ES/Ansible+at+WSI) for thoughts that went into this repository layout.


[1]: https://github.com/metacloud/molecule
