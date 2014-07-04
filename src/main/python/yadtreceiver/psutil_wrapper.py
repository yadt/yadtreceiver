import psutil


"""
Since backwards compatibility is not a concern of psutil, this wraps
process_iter() to make it work on all versions.

Older psutil versions (those that ship in RHEL6 repos) expose contents of
the Process class through fields.
Newer psutil versions expose those contents through methods (you can choose
blocking/nonblocking, and the result is cached).
The function get_processes does not block on newer psutil versions and
always returns items where contents are exposed through methods.
"""

class Process(object):

    def __init__(self, process):
        self.pid = process.pid
        try:
            self._name = process.name()
            self._cwd = process.cwd()
            self._cmdline = process.cmdline()
        except TypeError:
            self._name = process.name
            self._cwd = process.getcwd()
            self._cmdline = process.cmdline

    def name(self):
        return self._name

    def cwd(self):
        return self._cwd

    def cmdline(self):
        return self._cmdline


def get_processes():
    return (Process(p) for p in psutil.process_iter())
