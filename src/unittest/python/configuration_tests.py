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

import unittest

from mock import Mock, call, patch

from yadtreceiver.configuration import (DEFAULT_BROADCASTER_HOST,
                                        DEFAULT_BROADCASTER_PORT,
                                        DEFAULT_LOG_FILENAME,
                                        DEFAULT_PYTHON_COMMAND,
                                        DEFAULT_SCRIPT_TO_EXECUTE,
                                        DEFAULT_TARGETS,
                                        DEFAULT_TARGETS_DIRECTORY,
                                        SECTION_BROADCASTER,
                                        SECTION_RECEIVER,
                                        ReceiverConfigLoader,
                                        ReceiverConfig,
                                        load)
from yadtcommons.configuration import YadtConfigParser


class ReceiverConfigLoaderTests (unittest.TestCase):

    def test_should_create_instance_of_SafeConfigParser(self):
        parser = ReceiverConfigLoader()

        name_of_type = parser._parser.__class__.__name__
        self.assertEqual('YadtConfigParser', name_of_type)

    def test_should_return_broadcaster_host_option(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = 'broadcaster.host'
        mock_loader._parser = mock_parser

        actual_broadcaster_host = ReceiverConfigLoader.get_broadcaster_host(
            mock_loader)

        self.assertEqual('broadcaster.host', actual_broadcaster_host)
        self.assertEqual(
            call(SECTION_BROADCASTER, 'host', DEFAULT_BROADCASTER_HOST), mock_parser.get_option.call_args)

    def test_should_return_broadcaster_port_option(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option_as_int.return_value = 8081
        mock_loader._parser = mock_parser

        actual_broadcaster_port = ReceiverConfigLoader.get_broadcaster_port(
            mock_loader)

        self.assertEqual(8081, actual_broadcaster_port)
        self.assertEqual(
            call(SECTION_BROADCASTER, 'port', DEFAULT_BROADCASTER_PORT), mock_parser.get_option_as_int.call_args)

    @patch('yadtreceiver.configuration.socket')
    def test_should_return_hostname_from_receiver_section(self, mock_socket):
        mock_socket.gethostname.return_value = 'localhost'

        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = 'actual.hostname'
        mock_loader._parser = mock_parser

        actual_hostname = ReceiverConfigLoader.get_hostname(mock_loader)

        self.assertEqual('actual.hostname', actual_hostname)
        self.assertEqual(call(), mock_socket.gethostname)
        self.assertEqual(
            call(SECTION_RECEIVER, 'hostname', 'localhost'), mock_parser.get_option.call_args)

    def test_should_return_log_filename(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = 'filename.log'
        mock_loader._parser = mock_parser

        actual_log_filename = ReceiverConfigLoader.get_log_filename(
            mock_loader)

        self.assertEqual('filename.log', actual_log_filename)
        self.assertEqual(
            call(SECTION_RECEIVER, 'log_filename', DEFAULT_LOG_FILENAME), mock_parser.get_option.call_args)

    def test_should_return_python_command(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = '/spam/eggs/python'
        mock_loader._parser = mock_parser

        actual_python_command = ReceiverConfigLoader.get_python_command(
            mock_loader)

        self.assertEqual('/spam/eggs/python', actual_python_command)
        self.assertEqual(
            call(SECTION_RECEIVER, 'python_command', DEFAULT_PYTHON_COMMAND), mock_parser.get_option.call_args)

    def test_should_return_script_to_execute(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = '/script/to/execute'
        mock_loader._parser = mock_parser

        actual_script_to_execute = ReceiverConfigLoader.get_script_to_execute(
            mock_loader)

        self.assertEqual('/script/to/execute', actual_script_to_execute)
        self.assertEqual(
            call(SECTION_RECEIVER, 'script_to_execute', DEFAULT_SCRIPT_TO_EXECUTE), mock_parser.get_option.call_args)

    def test_should_return_targets(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option_as_set.return_value = set(['abc', 'def'])
        mock_loader._parser = mock_parser

        actual_targets = ReceiverConfigLoader.get_targets(mock_loader)

        self.assertEqual(set(['abc', 'def']), actual_targets)
        self.assertEqual(
            call(SECTION_RECEIVER, 'targets', DEFAULT_TARGETS), mock_parser.get_option_as_set.call_args)

    def test_should_return_targets_directory(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = '/directory/with/targets'
        mock_loader._parser = mock_parser

        actual_targets_directory = ReceiverConfigLoader.get_targets_directory(
            mock_loader)

        self.assertEqual('/directory/with/targets', actual_targets_directory)
        self.assertEqual(
            call(SECTION_RECEIVER, 'targets_directory', DEFAULT_TARGETS_DIRECTORY), mock_parser.get_option.call_args)

    def test_should_delegate_read_configuration_file(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.read_configuration_file.return_value = {'spam': 'eggs'}
        mock_loader._parser = mock_parser

        actual_configuration = ReceiverConfigLoader.read_configuration_file(
            mock_loader, 'filename.cfg')

        self.assertEqual({'spam': 'eggs'}, actual_configuration)
        self.assertEqual(
            call('filename.cfg'), mock_parser.read_configuration_file.call_args)

    def test_should_return_metrics_directory(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = '/tmp/metrics'
        mock_loader._parser = mock_parser

        actual_metrics_directory = ReceiverConfigLoader.get_metrics_directory(
            mock_loader)

        self.assertEqual('/tmp/metrics', actual_metrics_directory)
        self.assertEqual(
            call(SECTION_RECEIVER, 'metrics_directory', None), mock_parser.get_option.call_args)

    def test_should_return_metrics_file(self):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = '/tmp/metrics'
        mock_loader._parser = mock_parser

        actual_metrics_file = ReceiverConfigLoader.get_metrics_file(
            mock_loader)

        self.assertEqual('/tmp/metrics/ybr.metrics', actual_metrics_file)
        self.assertEqual(
            call(SECTION_RECEIVER, 'metrics_directory', None), mock_parser.get_option.call_args)


class LoadTest (unittest.TestCase):

    @patch('yadtreceiver.configuration.ReceiverConfig.compute_allowed_targets')
    @patch('yadtreceiver.configuration.ReceiverConfigLoader')
    def test_should_load_configuration_from_file(self, mock_loader_class, _):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_loader_class.return_value = mock_loader

        load('abc')

        self.assertEqual(
            call('abc'), mock_loader.read_configuration_file.call_args)

    @patch('yadtreceiver.configuration.ReceiverConfig.compute_allowed_targets')
    @patch('yadtreceiver.configuration.ReceiverConfigLoader')
    def test_should_get_broadcaster_properties_from_parser(self, mock_loader_class, _):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_loader.get_broadcaster_host.return_value = 'broadcaster host'
        mock_loader.get_broadcaster_port.return_value = 12345
        mock_loader_class.return_value = mock_loader

        actual_configuration = load('abc')

        self.assertEqual(call(), mock_loader.get_broadcaster_host.call_args)
        self.assertEqual(
            'broadcaster host', actual_configuration['broadcaster_host'])

        self.assertEqual(call(), mock_loader.get_broadcaster_port.call_args)
        self.assertEqual(12345, actual_configuration['broadcaster_port'])

    @patch('yadtreceiver.configuration.ReceiverConfigLoader')
    def test_should_get_receiver_properties_from_parser(self, mock_loader_class):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_loader.get_hostname.return_value = 'this is a name'
        mock_loader.get_log_filename.return_value = '/var/log/somewhere/rec.log'
        mock_loader.get_python_command.return_value = '/usr/bin/python'
        mock_loader.get_script_to_execute.return_value = '/usr/bin/yadtshell'
        mock_loader.get_log_filename.return_value = '/var/log/somewhere/rec.log'
        mock_loader.get_targets.return_value = set(['dev123'])
        mock_loader.get_targets_directory.return_value = '/etc/yadtshell/targets'
        mock_loader.get_metrics_directory.return_value = '/tmp/metrics'
        mock_loader_class.return_value = mock_loader

        actual_configuration = load('abc')

        self.assertEqual(call(), mock_loader.get_hostname.call_args)
        self.assertEqual('this is a name', actual_configuration['hostname'])

        self.assertEqual(call(), mock_loader.get_log_filename.call_args)
        self.assertEqual(
            '/var/log/somewhere/rec.log', actual_configuration['log_filename'])

        self.assertEqual(call(), mock_loader.get_python_command.call_args)
        self.assertEqual(
            '/usr/bin/python', actual_configuration['python_command'])

        self.assertEqual(call(), mock_loader.get_script_to_execute.call_args)
        self.assertEqual(
            '/usr/bin/yadtshell', actual_configuration['script_to_execute'])

        self.assertEqual(call(), mock_loader.get_targets.call_args)
        self.assertEqual(set(['dev123']), actual_configuration['targets'])

        self.assertEqual(call(), mock_loader.get_targets_directory.call_args)
        self.assertEqual('/etc/yadtshell/targets',
                         actual_configuration['targets_directory'])

        self.assertEqual(call(), mock_loader.get_targets_directory.call_args)
        self.assertEqual('/tmp/metrics',
                         actual_configuration['metrics_directory'])


class ReceiverConfigTests(unittest.TestCase):

    @patch('yadtreceiver.configuration.ReceiverConfigLoader')
    @patch('yadtreceiver.configuration.glob')
    def test_should_compute_allowed_targets(self, mock_glob, mock_loader_class):
        mock_glob.return_value = ['/foo/dev', '/foo/dev01', '/foo/dev02']
        config = ReceiverConfig('blah')
        config.configuration['targets'] = ['foo']
        config.compute_allowed_targets()

        self.assertEqual(config['allowed_targets'], ['dev', 'dev01', 'dev02'])

    @patch('yadtreceiver.configuration.ReceiverConfig.compute_allowed_targets')
    @patch('yadtreceiver.configuration.ReceiverConfigLoader')
    def test_should_reload_targets(self, mock_loader_class, _):
        mock_loader = Mock(ReceiverConfigLoader)
        mock_loader.get_targets.return_value = ['foo']
        mock_loader_class.return_value = mock_loader
        config = ReceiverConfig('/dev/foo')
        config.configuration['targets'] = ['bar']
        config.reload_targets()

        self.assertEqual(config['targets'], ['foo'])
