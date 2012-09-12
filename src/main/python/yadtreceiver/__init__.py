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
    Provides the Receiver class which implements a twisted service
    application. The receiver allows to start processes triggered by
    broadcast events. It is configured using a dictionary. You can load
    configuration files using the load method from the configuration
    module. When activated in the configuration the receiver will send
    update notifications to a graphite server.
"""

__author__ = 'Arne Hilmann, Michael Gruber'

import os
import traceback

from twisted.application import service
from twisted.internet import reactor
from twisted.python import log

from yadtbroadcastclient import WampBroadcaster

from yadtreceiver.graphite import send_update_notification_to_graphite
from yadtreceiver.protocols import ProcessProtocol
from yadtreceiver.events import Event


VERSION = '${version}'


class ReceiverException(Exception):
    """
        To be raised when an exception occurs within the receiver.
    """


class Receiver(service.Service):
    """
        The receiver connects to the broadcaster and receives events
        for the targets that it subscribed to.
    """


    def get_target_directory(self, target):
        """
            Appends the given target name to the targets_directory.

            @raise ReceiverException: if the target directory does not exist.
        """

        hostname          = self.configuration['hostname']
        targets_directory = self.configuration['targets_directory']

        target_directory  = os.path.join(targets_directory, target)

        if not os.path.exists(target_directory):
            raise ReceiverException('(%s) target[%s] request failed: target directory "%s" does not exist.'
                                    % (hostname, target, target_directory))

        return target_directory


    def handle_request(self, target, command, arguments):
        """
            Handles a request for the given target by executing the given
            command (using the python_command and script_to_execute from
            the configuration).
        """

        self.publish_start(target, command, arguments)
        
        if arguments:
            action = arguments[0]
            self.notify_graphite(target, action)

        hostname          = self.configuration['hostname']
        python_command    = self.configuration['python_command']
        script_to_execute = self.configuration['script_to_execute']

        command_and_arguments_list = [python_command, script_to_execute] + arguments
        command_with_arguments = ' '.join(command_and_arguments_list)

        process_protocol = ProcessProtocol(hostname, self.broadcaster, target, command_with_arguments)

        target_dir = self.get_target_directory(target)
        reactor.spawnProcess(process_protocol, python_command, command_and_arguments_list, env={}, path=target_dir)


    def notify_graphite(self, target, action):
        """
            Notifies the configured graphite server about events (update events).
        """

        if action == 'update':
            host = self.configuration['graphite_host']
            port = self.configuration['graphite_port']

            send_update_notification_to_graphite(target, host, port)


    def publish_failed(self, target, command, message):
        """
            Publishes a event to signal that the command on the target failed.
        """

        log.err(_stuff=Exception(message), _why=message)
        self.broadcaster.publish_cmd_for_target(target, command, Event.FAILED, message)


    def publish_start(self, target, command, arguments):
        """
            Publishes a event to signal that the command on the target started.
        """

        hostname = self.configuration['hostname']
        message  = '(%s) target[%s] request: command="%s", arguments=%s' % (hostname, target, command, arguments)
        log.msg(message)
        self.broadcaster.publish_cmd_for_target(target, command, Event.STARTED, message)


    def onConnect(self):
        """
            Subscribes to the targets from the configuration. The receiver
            is useless when no targets are configured, therefore it will exit
            with error code 1 when no targets are configured.
        """

        self.broadcaster.client.connectionLost = self.onConnectionLost

        host = self.configuration['broadcaster_host']
        port = self.configuration['broadcaster_port']

        log.msg('Successfully connected to broadcaster on %s:%s' % (host, port))

        targets = sorted(self.configuration['targets'])

        if not targets:
            log.err('No targets configured.')
            exit(1)

        for target in targets:
            log.msg('subscribing to target "%s".' % target)
            self.broadcaster.client.subscribe(target, self.onEvent)



    def _refresh_connection(self, delay=60 * 60, first_call=False):
        """
            When connected, closes connection to force a clean reconnect,
            except on first_call
        """
        reactor.callLater(delay, self._refresh_connection)
        if hasattr(self, 'broadcaster') and self.broadcaster.client:
            if not first_call:
                log.msg('Closing connection to broadcaster. This should force a connection-refresh.')
                self.broadcaster.client.sendClose()


    def onConnectionLost(self, reason):
        """
            Allows for clean reconnect behaviour, because it 'none'ifies 
            the client explicitly
        """
        log.err('connection lost: %s' % reason)
        self.broadcaster.client = None
        # TODO: superclass method should be called here?


    def _client_watchdog(self, delay=1):
        """
            Checks periodically if broadcaster.client is set
            (see also onConnectionLost), tries to reconnect after a 
            delay (delay after failed connect: 1, 2, 4, 8, 16, 32, 60, 60, ... 
            seconds)
        """
        if hasattr(self, 'broadcaster') and self.broadcaster.client:
            reactor.callLater(1, self._client_watchdog)
        else:
            reactor.callLater(delay, self._client_watchdog, min(60, 2 * delay))
            log.err('broadcast.client not set, trying to connect')
            if delay > 1:
                log.msg('(scheduling next try in %s seconds)' % delay)
            return self._connect_broadcaster()


    def onEvent(self, target, event):
        """
            Will be called when receiving an event from the broadcaster.
            See onConnect which subscribes to the targets.
        """

        log.msg(event)
        if event.get('id') == 'request':
            command   = event['cmd']
            arguments = event['args']

            try:
                self.handle_request(target, command, arguments)
            except Exception as e:
                log.err(e.message)
                log.err('-' * 40)
                for line in traceback.format_exc().splitlines():
                    log.err(line)
                log.err('-' * 40)
                self.publish_failed(target, command, e.message)

        log.msg('onEvent finished')

    def set_configuration(self, configuration):
        """
            Assigns a configuration to this receiver instance.
        """

        self.configuration = configuration


    def startService(self):
        """
            Initializes logging and establishes connection to broadcaster.
        """

        self._initialize_logging()
        #self._connect_broadcaster()
        self._client_watchdog()
        self._refresh_connection(first_call=True)


    def stopService(self):
        """
            Writes 'shutting down service' to the log.
        """
        
        log.msg('shutting down service')


    def _initialize_logging(self):
        """
            Starts logging as configured.
        """

        log_file = open(self.configuration['log_filename'], 'a+')
        os.chmod(self.configuration['log_filename'], 0o660)
        log.startLogging(log_file)
        log.msg('yadtreceiver version %s' % VERSION)


    def _connect_broadcaster(self):
        """
            Establishes a connection to the broadcaster as found in the
            configuration.
        """

        host = self.configuration['broadcaster_host']
        port = self.configuration['broadcaster_port']

        log.msg('Connecting to broadcaster on %s:%s' % (host, port))

        self.broadcaster = WampBroadcaster(host, port, 'yadtreceiver')
        self.broadcaster.addOnSessionOpenHandler(self.onConnect)
        self.broadcaster.connect()
