#   yadtreceiver
#   Copyright (C) 2012 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Michael Gruber'

from unittest import TestCase, main

from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

from yadtreceiver.configuration import load


class Test (TestCase):

    def setUp(self):
        self.temporary_directory = mkdtemp()

    def tearDown(self):
        rmtree(self.temporary_directory)

    def test(self):
        configuration_filename = join(
            self.temporary_directory, 'configuration.cfg')

        with open(configuration_filename, 'w') as configuration_file:
            configuration_file.write("""[receiver]
log_filename = /spam/eggs/yadtreceiver.log
targets = spam, eggs
targets_directory = /spam/eggs/targets
script_to_execute = /spam/eggs/yadtshell
python_command = /spam/eggs/python
hostname = spameggs

[broadcaster]
host = broadcaster.domain.tld
port = 8081

[graphite]
active = yes
host = graphite.domain.tld
port = 2003
""")

        actual_configuration = load(configuration_filename)

        self.assertEqual(
            '/spam/eggs/yadtreceiver.log', actual_configuration['log_filename'])
        self.assertEqual(
            set(['spam', 'eggs']), actual_configuration['targets'])
        self.assertEqual(
            '/spam/eggs/targets', actual_configuration['targets_directory'])
        self.assertEqual(
            '/spam/eggs/yadtshell', actual_configuration['script_to_execute'])
        self.assertEqual(
            '/spam/eggs/python', actual_configuration['python_command'])
        self.assertEqual('spameggs', actual_configuration['hostname'])

        self.assertEqual('broadcaster.domain.tld',
                         actual_configuration['broadcaster_host'])
        self.assertEqual(8081, actual_configuration['broadcaster_port'])

        self.assertEqual(
            'graphite.domain.tld', actual_configuration['graphite_host'])
        self.assertEqual(2003, actual_configuration['graphite_port'])
        self.assertEqual(True, actual_configuration['graphite_active'])


if __name__ == '__main__':
    main()
