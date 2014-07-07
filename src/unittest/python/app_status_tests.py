from unittest import TestCase

from yadtreceiver.app_status import AppStatusResource

from mock import patch, Mock


class AppStatusResourceTests(TestCase):

    @patch("yadtreceiver.app_status.gethostname")
    def setUp(self, gethostname):
        gethostname.return_value = "any-hostname"
        self.receiver = Mock()
        self.app_status = AppStatusResource(self.receiver)

    def test_should_cache_hostname_when_instantiated(self):
        self.assertEqual(self.app_status.hostname, "any-hostname")

    @patch("yadtreceiver.psutil_wrapper.psutil")
    def test_should_filter_processes_when_they_are_not_python(self, psutil):
        p1 = Mock()
        p1.name.return_value = "python"
        p1.cmdline.return_value = ["bar", "searchterm", "rebar"]
        p2 = Mock()
        p2.name.return_value = "java"
        p2.cmdline.return_value = ["bar", "searchterm", "rebar"]
        psutil.process_iter.return_value = [p1, p2]

        result = self.app_status.get_python_processes_containing("searchterm")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cmdline(), ["bar", "searchterm", "rebar"])

    @patch("yadtreceiver.psutil_wrapper.psutil")
    def test_should_filter_processes_when_they_are_not_matching_the_term(self, psutil):
        p1 = Mock()
        p1.name.return_value = "python"
        p1.cmdline.return_value = ["bar", "searchterm", "rebar"]
        p2 = Mock()
        p2.name.return_value = "python"
        p2.cmdline.return_value = ["bar", "fuuuuu", "rebar"]
        psutil.process_iter.return_value = [p1, p2]

        result = self.app_status.get_python_processes_containing("searchterm")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cmdline(), ["bar", "searchterm", "rebar"])

    @patch("yadtreceiver.psutil_wrapper.psutil")
    def test_should_filter_processes_when_they_are_neither_python_nor_matching_the_term(self, psutil):
        p1 = Mock()
        p1.name.return_value = "python"
        p1.cmdline.return_value = ["bar", "foo", "rebar"]
        p2 = Mock()
        p2.name.return_value = "rustc"
        p2.cmdline.return_value = ["bar", "fuuuuu", "rebar"]
        psutil.process_iter.return_value = [p1, p2]

        result = self.app_status.get_python_processes_containing("foo")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name(), "python")

    @patch("yadtreceiver.app_status.AppStatusResource.get_python_processes_containing")
    def test_should_return_yadtshell_processes(self, processes):
        self.receiver.configuration.get.return_value = "yadtshell"
        p1 = Mock()
        p1.cmdline.return_value = ["python", "yadtshell", "update", "--destroy"]
        p1.cwd.return_value = "p1_directory"
        p1.pid = 1
        p2 = Mock()
        p2.cmdline.return_value = ["python", "yadtshell", "status"]
        p2.cwd.return_value = "p2_directory"
        p2.pid = 2
        processes.return_value = [p1, p2]

        self.assertEqual(
            self.app_status.get_list_of_running_yadtshell_processes_spawned_by_receiver(),
            [{'command': 'yadtshell update --destroy', 'pid': '1', 'target': 'p1_directory'},
             {'command': 'yadtshell status', 'pid': '2', 'target': 'p2_directory'}])

    @patch("yadtreceiver.app_status.AppStatusResource.get_python_processes_containing")
    def test_should_return_yadtshell_processes_with_stripped_tracking_id(self, processes):
        self.receiver.configuration.get.return_value = "yadtshell"
        p1 = Mock()
        p1.cmdline.return_value = ["python", "yadtshell", "update", "--reboot", "--tracking-id='any-value'"]
        p1.cwd.return_value = "p1_directory"
        p1.pid = 1
        processes.return_value = [p1]

        self.assertEqual(
            self.app_status.get_list_of_running_yadtshell_processes_spawned_by_receiver(),
            [{'command': 'yadtshell update --reboot', 'pid': '1', 'target': 'p1_directory'}])
