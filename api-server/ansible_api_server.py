#!/usr/bin/env python

import os
import sys
from collections import namedtuple

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible import context
from ansible.module_utils.common.collections import ImmutableDict


import flask, subprocess, time, os, sys
from flask import request, Response
from ansi2html import Ansi2HTMLConverter


app = flask.Flask(__name__)
@app.route('/')
def index():
    def runit():
        conv = Ansi2HTMLConverter()
        loader = DataLoader()

        inventory = InventoryManager(loader=loader, sources='./inventory.ini')
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        playbook_path = './file_check.yaml'

        if not os.path.exists(playbook_path):
            print '[INFO] The playbook does not exist'
            sys.exit()

        # Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check','diff'])
        # options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, remote_user='ubuntu', private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root', verbosity=None, check=False, diff=False)
        context.CLIARGS = ImmutableDict(connection='local', module_path=['./modules'], forks=10, become=None,
                                        become_method=None, become_user=None, check=False, diff=False,syntax=False,private_key_file='./ansible.pem')
        # variable_manager.extra_vars = {'hosts': 'client'} 
        variable_manager = VariableManager(loader=loader, inventory=inventory) # This can accomodate various other command line arguments.`

        passwords = {}

        pbex = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords=passwords)

        results = pbex.run()

        for line in iter(results.readline,''):
            yield conv.convert(line.rstrip())
        p.communicate()
        exit_code = p.wait()
        yield 'rc = ' + str(exit_code)
    return Response(runit(), mimetype='text/html')
app.run(debug=True, port=5000, host='0.0.0.0')
# # #########

# #!/usr/bin/env python

# import json
# import shutil
# from ansible.module_utils.common.collections import ImmutableDict
# from ansible.parsing.dataloader import DataLoader
# from ansible.vars.manager import VariableManager
# from ansible.inventory.manager import InventoryManager
# from ansible.playbook.play import Play
# from ansible.executor.task_queue_manager import TaskQueueManager
# from ansible.plugins.callback import CallbackBase
# from ansible import context
# import ansible.constants as C

# class ResultCallback(CallbackBase):
#     """A sample callback plugin used for performing an action as results come in

#     If you want to collect all results into a single object for processing at
#     the end of the execution, look into utilizing the ``json`` callback plugin
#     or writing your own custom callback plugin
#     """
#     def v2_runner_on_ok(self, result, **kwargs):
#         """Print a json representation of the result

#         This method could store the result in an instance attribute for retrieval later
#         """
#         host = result._host
#         print(json.dumps({host.name: result._result}, indent=4))

# # since the API is constructed for CLI it expects certain options to always be set in the context object
# context.CLIARGS = ImmutableDict(connection='local', module_path=['/to/mymodules'], forks=10, become=None,
#                                 become_method=None, become_user=None, check=False, diff=False)

# # initialize needed objects
# loader = DataLoader() # Takes care of finding and reading yaml, json and ini files
# passwords = dict(vault_pass='secret')

# # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
# results_callback = ResultCallback()

# # create inventory, use path to host config file as source or hosts in a comma separated string
# inventory = InventoryManager(loader=loader, sources='localhost,')

# # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
# variable_manager = VariableManager(loader=loader, inventory=inventory)

# # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
# play_source =  dict(
#         name = "Ansible Play",
#         hosts = 'localhost',
#         gather_facts = 'no',
#         tasks = [
#             dict(action=dict(module='shell', args='ls'), register='shell_out'),
#             dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
#          ]
#     )

# # Create play object, playbook objects use .load instead of init or new methods,
# # this will also automatically create the task objects from the info provided in play_source
# play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

# # Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
# tqm = None
# try:
#     tqm = TaskQueueManager(
#               inventory=inventory,
#               variable_manager=variable_manager,
#               loader=loader,
#               passwords=passwords,
#               stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
#           )
#     result = tqm.run(play) # most interesting data for a play is actually sent to the callback's methods
# finally:
#     # we always need to cleanup child procs and the structures we use to communicate with them
#     if tqm is not None:
#         tqm.cleanup()

#     # Remove ansible tmpdir
#     shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)




