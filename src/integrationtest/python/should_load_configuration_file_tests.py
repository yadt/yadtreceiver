from unittest import TestCase, main

from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from yadtreceiver.configuration import Configuration

class Test (TestCase):
    def setUp(self):
        self.temporary_directory = mkdtemp()


    def tearDown(self):
        rmtree(self.temporary_directory)


    def test(self):
        configuration_filename = join(self.temporary_directory, 'configuration.cfg')

        with open(configuration_filename, 'w') as configuration_file:
            configuration_file.write("""[receiver]
log_filename = /spam/eggs/yadtreceiver.log
targets = spam, eggs
targets_directory = /spam/eggs/targets
script_to_execute = /spam/eggs/yadtshell

[broadcaster]
host = broadcaster.domain.tld
port = 8081

[graphite]
active = yes
host = graphite.domain.tld
port = 2003
""")

        actual_configuration = Configuration.load(configuration_filename)

        self.assertEqual('/spam/eggs/yadtreceiver.log', actual_configuration.log_filename)
        self.assertEqual(set(['spam', 'eggs']), actual_configuration.targets)
        self.assertEqual('/spam/eggs/targets', actual_configuration.targets_directory)
        self.assertEqual('/spam/eggs/yadtshell', actual_configuration.script_to_execute)

        self.assertEqual('broadcaster.domain.tld', actual_configuration.broadcaster_host)
        self.assertEqual(8081, actual_configuration.broadcaster_port)

        self.assertEqual('graphite.domain.tld', actual_configuration.graphite_host)
        self.assertEqual(2003, actual_configuration.graphite_port)
        self.assertEqual(True, actual_configuration.graphite_active)


if __name__ == '__main__':
    main()
