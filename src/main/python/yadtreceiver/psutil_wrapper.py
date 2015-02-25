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


def safe_access(default_value):
    def safe_inner(func):
        def wrapped(*args):
            try:
                return func(*args)
            except psutil.AccessDenied:
                return default_value
        return wrapped
    return safe_inner


class Process(object):

    def __init__(self, process):
        self.pid = process.pid
        self.process = process
        self._cmdline = None
        self._cwd = None
        self._name = None

    def name(self):
        if not self._name:
            try:
                return self.process.name()
            except TypeError:  # in old psutil, name is a field
                return self.process.name
        return self._name

    @safe_access("unknown")
    def cwd(self):
        if not self._cwd:
            try:
                return self.process.cwd()
            except AttributeError:  # old psutil does not have cwd()
                return self.process.getcwd()
        return self._cwd

    def cmdline(self):
        if not self._cmdline:
            try:
                self._cmdline = self.process.cmdline()
            except TypeError:  # in old psutil, cmdline is a field
                self._cmdline = self.process.cmdline
        return self._cmdline


def get_processes():
    return (Process(p) for p in psutil.process_iter())
