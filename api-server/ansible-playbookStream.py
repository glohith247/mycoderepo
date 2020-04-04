import flask, subprocess, time, os, sys
from flask import request, Response
from ansi2html import Ansi2HTMLConverter

app = flask.Flask(__name__)

@app.route('/')
def index():
    def runit():
        conv = Ansi2HTMLConverter()
        PlayBook = './file_check.yaml'
        cmd = 'ansible-playbook -i inventory.ini --key-file ansible.pem file_check.yaml'
        p = subprocess.Popen([cmd],
                             shell = True,
                             stdout = subprocess.PIPE,
                             universal_newlines = True)
        for line in iter(p.stdout.readline,''):
            yield conv.convert(line.rstrip())
        p.communicate()
        exit_code = p.wait()
        yield 'rc = ' + str(exit_code)
    return Response(runit(), mimetype='text/html')
app.run(debug=True, port=5000, host='0.0.0.0')


