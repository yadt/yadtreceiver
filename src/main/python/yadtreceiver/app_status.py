from socket import gethostname
from string import Template
from os.path import basename
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from twisted.web import resource
try:
    import simplejson as json  # better performance
except ImportError:
    import json

import yadtreceiver
from yadtreceiver.psutil_wrapper import get_processes


class AppStatusResource(resource.Resource):
    isLeaf = True

    def __init__(self, receiver):
        self.receiver = receiver
        self.hostname = gethostname()
        super(type(self), self).__init__()

    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json')
        status_json = {
        "name": "yadtreceiver v{0} on {1}".format(yadtreceiver.__version__, self.hostname),
        "running_commands": self.get_list_of_running_yadtshell_processes_spawned_by_receiver(),
        }
        return json.dumps(status_json, indent=4)

    def get_list_of_running_yadtshell_processes_spawned_by_receiver(self):
        yadtshell_script_name = self.receiver.configuration.get("script_to_execute")
        rendered_commands = []
        yadtshell_processes = self.get_python_processes_containing(yadtshell_script_name)
        for p in yadtshell_processes:
            arguments = p.cmdline()[1:]
            clean_arguments = filter(lambda arg: not arg.startswith("--tracking-id"), arguments)

            rendered_commands.append({
                                     "target": basename(p.cwd()),
                                     "command": " ".join(clean_arguments),
                                     "pid": str(p.pid),
                                     })
        return rendered_commands

    def get_python_processes_containing(self, script_name):
        python_processes = filter(lambda p: p.name() == "python", get_processes())
        matching_processes = filter(lambda p: script_name in p.cmdline(), python_processes)
        return matching_processes
