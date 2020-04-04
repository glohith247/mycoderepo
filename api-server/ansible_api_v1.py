#!/usr/bin/env python

import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
import json2html
import logging
import flask, subprocess, time, os, sys
from flask import jsonify
from flask import request, Response
from ansi2html import Ansi2HTMLConverter

LOCALLOGS   = True

class ResultCallback(CallbackBase):
        """A sample callback plugin used for performing an action as results come in

        If you want to collect all results into a single object for processing at
        the end of the execution, look into utilizing the ``json`` callback plugin
        or writing your own custom callback plugin
        """
        def v2_runner_on_ok(self, result, **kwargs):
                """Print a json representation of the result

                This method could store the result in an instance attribute for retrieval later
                """
                host = result._host
                print(json.dumps({host.name: result._result}, indent=4))


app = flask.Flask(__name__)
@app.route('/')
def run_playbook():
    try:
  #since the API is constructed for CLI it expects certain options to always be set in the context object
      context.CLIARGS = ImmutableDict(connection='local', module_path=['modules'], forks=10, become=None,
                                                                      become_method=None, become_user=None, check=False, diff=False, syntax=False, private_key_file='./ansible.pem', ansible_ssh_user='ubuntu', start_at_task='')

      # initialize needed objects
      loader = DataLoader() # Takes care of finding and reading yaml, json and ini files
      passwords = {}
      # dict(vault_pass='secret')

      # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
      results_callback = ResultCallback()

      # create inventory, use path to host config file as source or hosts in a comma separated string
      inventory = InventoryManager(loader=loader, sources='./inventory.ini')

      # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
      variable_manager = VariableManager(loader=loader, inventory=inventory)
      results_callback = ResultCallback()
      playbooks = ['./file_check.yaml']

      # variable_manager.extra_vars={"ansible_ssh_user":"root" , "ansible_ssh_pass":"passwd"}
      callback = ResultCallback()

      pd = PlaybookExecutor(
              playbooks=playbooks,
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              passwords={}
              )
      result = pd.run()
      # conv = Ansi2HTMLConverter()
      # old_stdout = sys.stdout
      # sys.stdout = mystdout = StringIO()
      # mystdout.reset() 
      # result = pd.run()
      # sys.stdout = old_stdout 
      # mystdout.seek(0)
      # if  mystdout.readline():
      #   for line in mystdout: 
      #     yield conv.convert(line.rstrip())

      return jsonify({'success': True, 'msg': result})

    except Exception, e:
        return jsonify({'success': False, 'msg': str(e)})
    

                #     yield conv.convert(line.rstrip())
                # yield 'rc = '
        # return Response(run_playbook(), mimetype='text/html')
                # print(result)
                # return result
                # pd._tqm._stdout_callback = callback

                # try:
                #     result = pd.run()
                #     print(callback)
                #     return callback

                # except Exception as e:
                #     print e

if __name__ == '__main__': 
        if LOCALLOGS:
                handler = logging.StreamHandler()
                handler.setLevel(logging.INFO)
                handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
                app.logger.addHandler(handler)
        app.run(host='0.0.0.0', port=5000, threaded=True)

