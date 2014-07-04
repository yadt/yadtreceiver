from socket import gethostname
from string import Template
from os.path import basename
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from twisted.web import resource

from yadtreceiver.psutil_wrapper import get_processes


class AppStatusResource(resource.Resource):
    isLeaf = True

    def __init__(self, receiver):
        self.receiver = receiver
        self.hostname = gethostname()
        super(type(self), self).__init__()

    def render_GET(self, request):
        return STATUS_TEMPLATE.substitute(hostname=self.hostname,
                                          running_commands=self.render_running_yadtshells())

    def render_running_yadtshells(self):
        return "\n".join(self.get_list_of_running_yadtshell_processes_spawned_by_receiver())

    def get_list_of_running_yadtshell_processes_spawned_by_receiver(self):
        yadtshell_script_name = self.receiver.configuration.get("script_to_execute")
        rendered_commands = []
        yadtshell_processes = self.get_python_processes_containing(yadtshell_script_name)
        for p in yadtshell_processes:
            arguments = p.cmdline()[2:]
            clean_arguments = filter(lambda arg: not arg.startswith("--tracking-id"), arguments)

            rendered_commands.append("<tr><td>%s</td><td>yadtshell %s</td><td>%s</td></tr>" % (
                                     basename(p.cwd()), " ".join(clean_arguments), p.pid))
        return rendered_commands

    def get_python_processes_containing(self, script_name):
        python_processes = filter(lambda p: p.name() == "python", get_processes())
        matching_processes = filter(lambda p: script_name in p.cmdline(), python_processes)
        return matching_processes


STATUS_TEMPLATE = Template("""
<html>
<h1>Yadtreceiver on $hostname is operational.</h1>
<h2>Running commands</h2>

<p> <table cellspacing=15 style="border:1px solid black;">
<tr>
  <td><strong>Target</strong></td>
  <td><strong>Command</strong></td>
  <td><strong>PID</strong></td>
</tr>
$running_commands
</table>
</p>
                           """)
