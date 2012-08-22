#   yadt receiver
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
from yadtreceiver.configuration import (ConfigurationException,
                                        ReceiverConfigParser)


__author__ = 'Michael Gruber'

import unittest

from mock import Mock, call, patch

from yadtreceiver.configuration import (DEFAULT_BROADCASTER_HOST,
                                        DEFAULT_BROADCASTER_PORT,
                                        DEFAULT_GRAPHITE_ACTIVE,
                                        DEFAULT_GRAPHITE_HOST,
                                        DEFAULT_GRAPHITE_PORT,
                                        DEFAULT_PYTHON_COMMAND,
                                        DEFAULT_SCRIPT_TO_EXECUTE,
                                        DEFAULT_TARGETS,
                                        DEFAULT_TARGETS_DIRECTORY,
                                        SECTION_BROADCASTER,
                                        SECTION_GRAPHITE,
                                        SECTION_DEFAULT,
                                        ReceiverConfigParser)

class ConfigurationTests (unittest.TestCase):
    def test_should_create_instance_of_SafeConfigParser (self):
        parser = ReceiverConfigParser()

        name_of_type = parser.parser.__class__.__name__
        self.assertEquals('SafeConfigParser', name_of_type)

    def test_should_return_broadcaster_host_option (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_broadcaster_host(mock_parser)

        self.assertEquals(call(SECTION_BROADCASTER, 'host', DEFAULT_BROADCASTER_HOST), mock_parser._get_option.call_args)

    def test_should_return_broadcaster_port_option (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_broadcaster_port(mock_parser)

        self.assertEquals(call(SECTION_BROADCASTER, 'port', DEFAULT_BROADCASTER_PORT), mock_parser._get_option_as_int.call_args)

    def test_should_return_graphite_active (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_graphite_active(mock_parser)

        self.assertEquals(call(SECTION_GRAPHITE, 'active', DEFAULT_GRAPHITE_ACTIVE), mock_parser._get_option_as_yes_or_no_boolean.call_args)

    def test_should_return_graphite_host (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_graphite_host(mock_parser)

        self.assertEquals(call(SECTION_GRAPHITE, 'host', DEFAULT_GRAPHITE_HOST), mock_parser._get_option.call_args)

    def test_should_return_graphite_port (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_graphite_port(mock_parser)

        self.assertEquals(call(SECTION_GRAPHITE, 'port', DEFAULT_GRAPHITE_PORT), mock_parser._get_option_as_int.call_args)

    def test_should_return_hostname_from_default_section (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = True
        mock_wrapped_parser.has_option.return_value = True
        mock_wrapped_parser.get.return_value = 'hostname'
        mock_parser.parser = mock_wrapped_parser

        actual_hostname = ReceiverConfigParser.get_hostname(mock_parser)

        self.assertEquals('hostname', actual_hostname)
        self.assertEquals(call(SECTION_DEFAULT), mock_wrapped_parser.has_section.call_args)
        self.assertEquals(call(SECTION_DEFAULT, 'hostname'), mock_wrapped_parser.has_option.call_args)
        self.assertEquals(call(SECTION_DEFAULT, 'hostname'), mock_wrapped_parser.get.call_args)

    @patch('yadtreceiver.configuration.socket')
    def test_should_return_hostname_from_socket_when_section_does_not_contain_option (self, mock_socket):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = True
        mock_wrapped_parser.has_option.return_value = False
        mock_socket.gethostname.return_value = 'hostname'
        mock_parser.parser = mock_wrapped_parser

        actual_hostname = ReceiverConfigParser.get_hostname(mock_parser)

        self.assertEquals('hostname', actual_hostname)
        self.assertEquals(call(SECTION_DEFAULT), mock_wrapped_parser.has_section.call_args)
        self.assertEquals(call(SECTION_DEFAULT, 'hostname'), mock_wrapped_parser.has_option.call_args)
        self.assertEquals(call(), mock_socket.gethostname.call_args)

    @patch('yadtreceiver.configuration.socket')
    def test_should_return_hostname_from_socket_when_no_default_section (self, mock_socket):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = False
        mock_socket.gethostname.return_value = 'hostname'
        mock_parser.parser = mock_wrapped_parser

        actual_hostname = ReceiverConfigParser.get_hostname(mock_parser)

        self.assertEquals('hostname', actual_hostname)
        self.assertEquals(call(SECTION_DEFAULT), mock_wrapped_parser.has_section.call_args)
        self.assertEquals(call(), mock_socket.gethostname.call_args)

    def test_should_return_python_command (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_python_command(mock_parser)

        self.assertEquals(call(SECTION_DEFAULT, 'python_command', DEFAULT_PYTHON_COMMAND), mock_parser._get_option.call_args)

    def test_should_return_script_to_execute (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_script_to_execute(mock_parser)

        self.assertEquals(call(SECTION_DEFAULT, 'script_to_execute', DEFAULT_SCRIPT_TO_EXECUTE), mock_parser._get_option.call_args)

    def test_should_return_targets (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_targets(mock_parser)

        self.assertEquals(call(SECTION_DEFAULT, 'targets', DEFAULT_TARGETS), mock_parser._get_option_as_set.call_args)

    def test_should_return_targets_directory (self):
        mock_parser = Mock(ReceiverConfigParser)

        ReceiverConfigParser.get_targets_directory(mock_parser)

        self.assertEquals(call(SECTION_DEFAULT, 'targets_directory', DEFAULT_TARGETS_DIRECTORY), mock_parser._get_option.call_args)

    @patch('yadtreceiver.configuration.log')
    @patch('yadtreceiver.configuration.os.path.exists')
    @patch('__builtin__.exit')
    def test_should_exit_when_configuration_file_does_not_exist (self, mock_exit, mock_exists, mock_log):
        mock_parser = Mock(ReceiverConfigParser)
        mock_exists.return_value = False

        ReceiverConfigParser.read_configuration_file(mock_parser, 'some.cfg')

        self.assertEquals(call('some.cfg'), mock_exists.call_args)
        self.assertEquals(call(1), mock_exit.call_args)

    @patch('yadtreceiver.configuration.log')
    @patch('yadtreceiver.configuration.os.path.exists')
    def test_should_read_configuration_file (self, mock_exists, mock_log):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_parser.parser = mock_wrapped_parser
        mock_exists.return_value = True

        ReceiverConfigParser.read_configuration_file(mock_parser, 'some.cfg')

        self.assertEquals(call(['some.cfg']), mock_wrapped_parser.read.call_args)

    def test_should_return_option_from_section (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = True
        mock_wrapped_parser.has_option.return_value = True
        mock_wrapped_parser.get.return_value = 'the option'
        mock_parser.parser = mock_wrapped_parser

        actual_option = ReceiverConfigParser._get_option(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals('the option', actual_option)
        self.assertEquals(call('section'), mock_wrapped_parser.has_section.call_args)
        self.assertEquals(call('section', 'option'), mock_wrapped_parser.has_option.call_args)
        self.assertEquals(call('section', 'option'), mock_wrapped_parser.get.call_args)

    def test_should_return_default_value_when_option_not_in_section (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = True
        mock_wrapped_parser.has_option.return_value = False
        mock_parser.parser = mock_wrapped_parser

        actual_option = ReceiverConfigParser._get_option(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals('default_value', actual_option)
        self.assertEquals(call('section'), mock_wrapped_parser.has_section.call_args)
        self.assertEquals(call('section', 'option'), mock_wrapped_parser.has_option.call_args)

    def test_should_return_default_value_when_section_does_not_exist (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = False
        mock_parser.parser = mock_wrapped_parser

        actual_option = ReceiverConfigParser._get_option(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals('default_value', actual_option)
        self.assertEquals(call('section'), mock_wrapped_parser.has_section.call_args)

    def test_should_return_yes_as_boolean_value_true (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = 'yes'

        actual_option = ReceiverConfigParser._get_option_as_yes_or_no_boolean(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals(True, actual_option)
        self.assertEquals(call('section', 'option', 'default_value'), mock_parser._get_option.call_args)

    def test_should_return_no_as_boolean_value_false (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = 'no'

        actual_option = ReceiverConfigParser._get_option_as_yes_or_no_boolean(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals(False, actual_option)
        self.assertEquals(call('section', 'option', 'default_value'), mock_parser._get_option.call_args)

    def test_should_raise_exception_when_given_value_is_not_yes_or_no (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = 'tralala'

        self.assertRaises(ConfigurationException, ReceiverConfigParser._get_option_as_yes_or_no_boolean, mock_parser, 'section', 'option', 'default_value')

    def test_should_return_option_as_int (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = '123456'

        actual_option = ReceiverConfigParser._get_option_as_int(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals(123456, actual_option)
        self.assertEquals(call('section', 'option', 'default_value'), mock_parser._get_option.call_args)

    def test_should_raise_exception_when_given_option_is_not_digit (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = 'abcdef'

        self.assertRaises(ConfigurationException, ReceiverConfigParser._get_option_as_int, mock_parser, 'section', 'option', 'default_value')

    def test_should_return_default_when_option_not_available (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = ''

        actual_option = ReceiverConfigParser._get_option_as_list(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals('default_value', actual_option)
        self.assertEquals(call('section', 'option', ''), mock_parser._get_option.call_args)

    def test_should_return_list_separated_by_comma (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option.return_value = ' abc, def,ghi,jkl   '

        actual_option = ReceiverConfigParser._get_option_as_list(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals(['abc', 'def', 'ghi', 'jkl'], actual_option)
        self.assertEquals(call('section', 'option', ''), mock_parser._get_option.call_args)

    def test_should_return_a_set (self):
        mock_parser = Mock(ReceiverConfigParser)
        mock_parser._get_option_as_list.return_value = ['abc', 'def', 'ghi', 'jkl']

        actual_option = ReceiverConfigParser._get_option_as_set(mock_parser, 'section', 'option', 'default_value')

        self.assertEquals(set(['abc', 'def', 'ghi', 'jkl']), actual_option)
        self.assertEquals(call('section', 'option', 'default_value'), mock_parser._get_option_as_list.call_args)
