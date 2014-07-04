from unittest import TestCase

from mock import patch, Mock

from yadtreceiver.psutil_wrapper import get_processes


class BackwardsCompatibilityTests(TestCase):

    @patch("yadtreceiver.psutil_wrapper.psutil")
    def test_new_psutil(self, psutil):
        p1 = Mock()
        p1.name.return_value = "python"
        p1.cmdline.return_value = ["foo", "bar"]
        p1.cwd.return_value = "/any/dir"
        p1.pid = 42
        processes = [p1]
        psutil.process_iter.return_value = (p for p in processes)

        actual_processes = [p for p in get_processes()]

        self.assertEqual(len(actual_processes), 1)
        self.assertEqual(actual_processes[0].pid, 42)
        self.assertEqual(actual_processes[0].name(), "python")
        self.assertEqual(actual_processes[0].cmdline(), ["foo", "bar"])
        self.assertEqual(actual_processes[0].cwd(), "/any/dir")

    @patch("yadtreceiver.psutil_wrapper.psutil")
    def test_old_psutil(self, psutil):
        p1 = Mock()
        p1.name = "python"
        p1.cmdline = ["foo", "bar"]
        p1.getcwd.return_value = "/any/dir"
        p1.pid = 42
        processes = [p1]
        psutil.process_iter.return_value = (p for p in processes)

        actual_processes = [p for p in get_processes()]

        self.assertEqual(len(actual_processes), 1)
        self.assertEqual(actual_processes[0].pid, 42)
        self.assertEqual(actual_processes[0].name(), "python")
        self.assertEqual(actual_processes[0].cmdline(), ["foo", "bar"])
        self.assertEqual(actual_processes[0].cwd(), "/any/dir")
