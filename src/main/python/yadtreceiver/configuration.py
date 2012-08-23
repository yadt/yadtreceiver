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

"""
    Use the function Configuration.load to read a Configuration from a file.

    example configuration file receiver.cfg:

        [DEFAULT]
        targets = devyadt, proyadt
        targets_directory = /etc/yadtshell/targets
        script_to_execute = /usr/bin/yadtshell

        [broadcaster]
        host = broadcaster.domain.tld
        port = 8081

        [graphite]
        active = yes
        host = graphite.domain.tld
        port = 2003
"""

__author__ = 'Michael Gruber'

import os
import socket
import sys

from ConfigParser import SafeConfigParser

DEFAULT_BROADCASTER_HOST = 'localhost'
DEFAULT_BROADCASTER_PORT = 8081
DEFAULT_GRAPHITE_HOST = 'localhost'
DEFAULT_GRAPHITE_PORT = 2003
DEFAULT_GRAPHITE_ACTIVE = False
DEFAULT_LOG_FILENAME = '/var/log/yadtreceiver.log'
DEFAULT_PYTHON_COMMAND = '/usr/bin/python'
DEFAULT_SCRIPT_TO_EXECUTE = '/usr/bin/yadtshell'
DEFAULT_TARGETS = {}
DEFAULT_TARGETS_DIRECTORY = '/etc/yadtshell/targets/'

SECTION_BROADCASTER = 'broadcaster'
SECTION_RECEIVER = 'receiver'
SECTION_GRAPHITE = 'graphite'


class ConfigurationException (Exception):
    """
        to be raised when an configuration error occurs.
    """

class ReceiverConfigParser (object):
    """
        uses a SafeConfigParser to offer some convenience methods.
    """


    def __init__(self):
        """
            Creates instance of SafeConfigParser which will be used to parse
            the configuration file.
        """

        self.parser = SafeConfigParser()


    def get_broadcaster_host(self):
        """
            @return: the broadcaster host from the configuration file,
                     otherwise DEFAULT_BROADCASTER_HOST.
        """

        return self._get_option(SECTION_BROADCASTER, 'host', DEFAULT_BROADCASTER_HOST)


    def get_broadcaster_port(self):
        """
            @return: the broadcaster port from the configuration file as int,
                     otherwise DEFAULT_BROADCASTER_PORT.
        """

        return self._get_option_as_int(SECTION_BROADCASTER, 'port', DEFAULT_BROADCASTER_PORT)


    def get_graphite_active(self):
        """
            @return: the graphite active porperty from the configuration file
                     as bool, otherwise DEFAULT_GRAPHITE_ACTIVE.
        """

        return self._get_option_as_yes_or_no_boolean(SECTION_GRAPHITE, 'active', DEFAULT_GRAPHITE_ACTIVE)


    def get_graphite_host(self):
        """
            @return: the graphite host from the configuration file,
                     otherwise DEFAULT_GRAPHITE_HOST.
        """

        return self._get_option(SECTION_GRAPHITE, 'host', DEFAULT_GRAPHITE_HOST)


    def get_graphite_port(self):
        """
            @return: the graphite port from the configuration file as int,
                     otherwise DEFAULT_GRAPHITE_PORT.
        """

        return self._get_option_as_int(SECTION_GRAPHITE, 'port', DEFAULT_GRAPHITE_PORT)


    def get_hostname(self):
        """
            @return: if a hostname is given in the configration file it will
                     return it, otherwise it will return the host name as
                     given by socket.gethostname
        """

        if self.parser.has_section(SECTION_RECEIVER):
            if self.parser.has_option(SECTION_RECEIVER, 'hostname'):
                return self.parser.get(SECTION_RECEIVER, 'hostname')

        return socket.gethostname()


    def get_log_filename(self):
        """
            @return: the log filename from the configuration file if given,
                     otherwise DEFAULT_LOG_FILENAME
        """

        return self._get_option(SECTION_RECEIVER, 'log_filename', DEFAULT_LOG_FILENAME)


    def get_python_command(self):
        """
            @return: the python command from the configuration file if given,
                     otherwise DEFAULT_PYTHON_COMMAND
        """

        return self._get_option(SECTION_RECEIVER, 'python_command', DEFAULT_PYTHON_COMMAND)


    def get_script_to_execute(self):
        """
            @return: if the configuration file provides a script to execute,
                     otherwise DEFAULT_SCRIPT_TO_EXECUTE.
        """

        return self._get_option(SECTION_RECEIVER, 'script_to_execute', DEFAULT_SCRIPT_TO_EXECUTE)


    def get_targets(self):
        """
            @return: the set of targets given in the configuration file,
                     otherwise DEFAULT_TARGETS.
        """

        return self._get_option_as_set(SECTION_RECEIVER, 'targets', DEFAULT_TARGETS)


    def get_targets_directory(self):
        """
            @return: the targets directory from the configuration file,
                     otherwise DEFAULT_TARGETS_DIRECTORY.
        """

        return self._get_option(SECTION_RECEIVER, 'targets_directory', DEFAULT_TARGETS_DIRECTORY)


    def read_configuration_file(self, filename):
        """
            reads the file into the parser. Will exit with error code 1 if
            the configuration file does not exist.
        """

        if not os.path.exists(filename):
            sys.stderr.write('Configuration file "%s" does not exist.\n' % filename)
            exit(1)
            return

        sys.stdout.write('Loading configuration file "%s"' % filename)
        self.parser.read([filename])


    def _get_option(self, section, option, default_value):
        """
            @return: the option from the section if it exists,
                     otherwise the given default value.
        """

        if self.parser.has_section(section):
            if self.parser.has_option(section, option):
                return self.parser.get(section, option)

        return default_value


    def _get_option_as_yes_or_no_boolean(self, section, option, default_value):
        """
            @return: the boolean option from the section if it exists,
                     otherwise the given default value.
        """

        option_value = self._get_option(section, option, default_value)

        if option_value != 'yes' and option_value != 'no':
            raise ConfigurationException('Option %s in section %s expected "yes" or "no", but got %s'
                                         % (option, section, option_value))

        return option_value == 'yes'


    def _get_option_as_int(self, section, option, default_value):
        """
            @return: the integer option from the section if it exists,
                     otherwise the given default value.
        """

        option_value = self._get_option(section, option, default_value)

        if not option_value.isdigit():
            raise ConfigurationException('Option %s in section %s expected a integer value, but got %s'
                                         % (option, section, option_value))
        return int(option_value)


    def _get_option_as_list(self, section, option, default_value):
        """
            @return: the option (list of strings) from the section if it exists
                     otherwise the given default value.
        """

        option_value = self._get_option(section, option, '')

        if option_value == '':
            return default_value

        list_of_unstripped_options = option_value.split(',')

        result = []
        for unstripped_option in list_of_unstripped_options:
            result.append(unstripped_option.strip())

        return result


    def _get_option_as_set(self, section, option, default_value):
        """
            @return: the option (set of strings) from the section if it exists,
                     otherwise the given default value.
        """

        option_values = self._get_option_as_list(section, option, default_value)
        return set(option_values)


class Configuration(object):
    """
        represents the configuration data for a yadtreceiver.
    """

    broadcaster_host = DEFAULT_BROADCASTER_HOST
    broadcaster_port = DEFAULT_BROADCASTER_PORT

    graphite_active = DEFAULT_GRAPHITE_ACTIVE
    graphite_host = DEFAULT_GRAPHITE_HOST
    graphite_port = DEFAULT_GRAPHITE_PORT

    hostname = 'localhost'
    log_filename = DEFAULT_LOG_FILENAME
    python_command = DEFAULT_PYTHON_COMMAND
    script_to_execute = DEFAULT_SCRIPT_TO_EXECUTE
    targets = DEFAULT_TARGETS
    targets_directory = DEFAULT_TARGETS_DIRECTORY

    def __init__(self):
        """
            initializes a instance with default values and hostname is
            'localhost'.
        """

    @staticmethod
    def load(filename):
        """
            loads configuration from a file.

            @return: Configuration object containing the data from the file.
        """

        parser = ReceiverConfigParser()
        parser.read_configuration_file(filename)

        configuration = Configuration()
        configuration.broadcaster_host = parser.get_broadcaster_host()
        configuration.broadcaster_port = parser.get_broadcaster_port()
        configuration.graphite_active = parser.get_graphite_active()
        configuration.graphite_host = parser.get_graphite_host()
        configuration.graphite_port = parser.get_graphite_port()
        configuration.hostname = parser.get_hostname()
        configuration.log_filename = parser.get_log_filename()
        configuration.python_command = parser.get_python_command()
        configuration.script_to_execute = parser.get_script_to_execute()
        configuration.targets = parser.get_targets()
        configuration.targets_directory = parser.get_targets_directory()

        return configuration
