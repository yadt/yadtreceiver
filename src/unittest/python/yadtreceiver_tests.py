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

from yadtreceiver import __version__, Receiver, ReceiverException
from yadtreceiver.events import Event


class YadtReceiverTests (unittest.TestCase):
    def test_if_this_test_fails_maybe_you_have_yadtreceiver_installed_locally (self):
        self.assertEqual('${version}', __version__)


    def test_should_set_configuration (self):
        configuration = 'configuration'
        receiver = Receiver()

        receiver.set_configuration(configuration)

        self.assertEquals(configuration, receiver.configuration)

    @patch('yadtreceiver.WampBroadcaster')
    def test_should_initialize_broadcaster_when_starting_service (self, mock_wamb):
        configuration = Mock(Configuration)
        configuration.broadcaster_host = 'broadcaster-host'
        configuration.broadcaster_port = 1234
        receiver = Receiver()
        receiver.set_configuration(configuration)

        receiver._connect_broadcaster()

        self.assertEquals(call('broadcaster-host', 1234, 'yadtreceiver'), mock_wamb.call_args)


    @patch('yadtreceiver.WampBroadcaster')
    def test_should_add_session_handler_to_broadcaster_when_starting_service (self, mock_wamb):
        receiver      = Receiver()
        configuration = {'broadcaster_host' : 'broadcasterhost',
                         'broadcaster_port' : 1234}
        receiver.set_configuration(configuration)
        mock_broadcaster_client = Mock()
        mock_wamb.return_value = mock_broadcaster_client

        receiver._connect_broadcaster()

        self.assertEquals(call(receiver.onConnect), mock_broadcaster_client.addOnSessionOpenHandler.call_args)


    @patch('yadtreceiver.WampBroadcaster')
    def test_should_connect_broadcaster_when_starting_service (self, mock_wamb):
        receiver = Receiver()
        configuration = {'broadcaster_host' : 'broadcaster-host',
                         'broadcaster_port' : 1234}
        receiver.set_configuration(configuration)
        mock_broadcaster_client = Mock()
        mock_wamb.return_value = mock_broadcaster_client

        receiver._connect_broadcaster()

        self.assertEquals(call(), mock_broadcaster_client.connect.call_args)


    @patch('yadtreceiver.WampBroadcaster')
    def test_should_initialize_broadcaster_when_starting_service (self, mock_wamb):
        configuration = {'broadcaster_host' : 'broadcaster-host',
                         'broadcaster_port' : 1234}
        receiver = Receiver()
        receiver.set_configuration(configuration)

        receiver._connect_broadcaster()

        self.assertEquals(call('broadcaster-host', 1234, 'yadtreceiver'), mock_wamb.call_args)

    @patch('yadtreceiver.log')
    @patch('__builtin__.exit')
    def test_should_exit_when_no_target_configured (self, mock_exit, mock_log):
        receiver = Receiver()
        receiver.set_configuration({'targets' : set(),
                                    'broadcaster_host': 'broadcaster_host',
                                    'broadcaster_port': 1234})
        mock_broadcaster_client = Mock()
        receiver.broadcaster = mock_broadcaster_client

        receiver.onConnect()

        self.assertEquals(call(1), mock_exit.call_args)


    def test_should_initialize_watchdog_and_start_connection_when_service_starts (self):
        mock_receiver = Mock(Receiver)

        Receiver.startService(mock_receiver)

        self.assertEquals(call(), mock_receiver._client_watchdog.call_args)
        self.assertEquals(call(first_call=True), mock_receiver._refresh_connection.call_args)


    def test_should_subscribe_to_target_from_configuration_when_connected (self):
        receiver = Receiver()
        mock_broadcaster_client = Mock()
        receiver.broadcaster = mock_broadcaster_client
        receiver.set_configuration({'targets' : set(['devabc123']),
                                    'broadcaster_host': 'broadcaster_host',
                                    'broadcaster_port': 1234})
        receiver.onConnect()

        self.assertEquals(call('devabc123', receiver.onEvent), mock_broadcaster_client.client.subscribe.call_args)


    def test_should_subscribe_to_targets_from_configuration_in_alphabetical_order_when_connected (self):
        receiver = Receiver()
        mock_broadcaster_client = Mock()
        receiver.broadcaster = mock_broadcaster_client
        receiver.set_configuration({'targets': set(['dev01', 'dev02', 'dev03']),
                                    'broadcaster_host': 'broadcaster_host',
                                    'broadcaster_port': 1234})

        receiver.onConnect()

        self.assertEquals([call('dev01', receiver.onEvent),
                           call('dev02', receiver.onEvent),
                           call('dev03', receiver.onEvent)], mock_broadcaster_client.client.subscribe.call_args_list)


    @patch('os.path.exists')
    def test_should_raise_exception_when_target_directory_does_not_exist (self, mock_exists):
        mock_exists.return_value = False
        receiver = Receiver()
        configuration = {'hostname'          : 'hostname',
                         'targets_directory' : '/etc/yadtshell/targets/'} 
        receiver.set_configuration(configuration)

        self.assertRaises(ReceiverException, receiver.get_target_directory, 'spargel')


    @patch('os.path.exists')
    def test_should_append_target_name_to_targets_directory (self, mock_exists):
        mock_exists.return_value = True
        receiver = Receiver()
        configuration = {'hostname'          : 'hostname',
                         'targets_directory' : '/etc/yadtshell/targets/'} 
        receiver.set_configuration(configuration)

        actual_target_directory = receiver.get_target_directory('spargel')

        self.assertEquals('/etc/yadtshell/targets/spargel', actual_target_directory)


    @patch('os.path.exists')
    def test_should_join_target_name_with_targets_directory (self, mock_exists):
        mock_exists.return_value = True
        receiver = Receiver()
        configuration = {'hostname'          : 'hostname',
                         'targets_directory' : '/etc/yadtshell/targets/'} 
        receiver.set_configuration(configuration)

        actual_target_directory = receiver.get_target_directory('spargel')

        self.assertEquals('/etc/yadtshell/targets/spargel', actual_target_directory)


    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.send_update_notification_to_graphite')
    def test_should_publish_start_event (self, mock_reactor, mock_send):
        mock_receiver = Mock(Receiver)
        mock_receiver.broadcaster = Mock()
        mock_receiver.configuration = {'hostname' : 'hostname',
                                       'python_command' : '/usr/bin/python',
                                       'graphite_active': True,
                                       'script_to_execute' : '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.handle_request(mock_receiver, mock_event)

        self.assertEquals(call(mock_event), mock_receiver.publish_start.call_args)


    @patch('yadtreceiver.reactor')
    def test_should_notify_graphite (self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_receiver.broadcaster = Mock()
        mock_receiver.configuration = {'hostname'          : 'hostname',
                                       'graphite_active'   : True,
                                       'python_command'    : '/usr/bin/python',
                                       'script_to_execute' : '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.handle_request(mock_receiver, mock_event)

        self.assertEquals(call('devabc123', 'update'), mock_receiver.notify_graphite.call_args)

    @patch('yadtreceiver.reactor')
    def test_should_not_notify_graphite_if_deactivated (self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_receiver.broadcaster = Mock()
        mock_receiver.configuration = {'hostname'          : 'hostname',
                                       'graphite_active'   : False,
                                       'python_command'    : '/usr/bin/python',
                                       'script_to_execute' : '/usr/bin/yadtshell'}
        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.handle_request(mock_receiver, mock_event)

        self.assertEquals(None, mock_receiver.notify_graphite.call_args)


    @patch('yadtreceiver.reactor')
    def test_should_not_notify_graphite_when_no_action_given (self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_receiver.broadcaster = Mock()
        mock_receiver.configuration = {'hostname'          : 'hostname',
                                       'graphite_active'   : True,
                                       'python_command'    : '/usr/bin/python',
                                       'script_to_execute' : '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = []

        Receiver.handle_request(mock_receiver, mock_event)

        self.assertEquals(None, mock_receiver.notify_graphite.call_args)


    @patch('yadtreceiver.send_update_notification_to_graphite')
    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.ProcessProtocol')
    def test_should_spawn_new_process_on_reactor (self, mock_protocol, mock_reactor, mock_send):
        mock_protocol.return_value = 'mock-protocol'
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster
        mock_receiver.get_target_directory.return_value = '/etc/yadtshell/targets/devabc123'

        mock_receiver.configuration = {'hostname'          : 'hostname',
                                       'graphite_active'   : True,
                                       'python_command'    : '/usr/bin/python',
                                       'script_to_execute' : '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.handle_request(mock_receiver, mock_event)

        self.assertEquals(call('hostname', mock_broadcaster, 'devabc123', '/usr/bin/python /usr/bin/yadtshell update'), mock_protocol.call_args)
        self.assertEquals(call('mock-protocol', '/usr/bin/python', ['/usr/bin/python', '/usr/bin/yadtshell', 'update'], path='/etc/yadtshell/targets/devabc123', env={}), mock_reactor.spawnProcess.call_args)


    @patch('yadtreceiver.send_update_notification_to_graphite')
    def test_should_not_notify_graphite_on_update_if_command_is_status (self, mock_send):
        mock_receiver = Mock(Receiver)

        Receiver.notify_graphite(mock_receiver, 'devabc123', 'status')

        self.assertEquals(None, mock_send.call_args)


    @patch('yadtreceiver.send_update_notification_to_graphite')
    def test_should_notify_graphite_on_update (self, mock_send):
        mock_receiver = Mock(Receiver)
        mock_receiver.configuration = {'graphite_host' : 'host',
                                       'graphite_port' : 'port'}

        Receiver.notify_graphite(mock_receiver, 'devabc123', 'update')

        self.assertEquals(call('devabc123', 'host', 'port'), mock_send.call_args)


    @patch('yadtreceiver.log')
    def test_should_publish_event_about_failed_command_on_target (self, mock_log):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.publish_failed(mock_receiver, mock_event, 'It failed!')

        self.assertEquals(call('devabc123', 'yadtshell', 'failed', 'It failed!'), mock_broadcaster.publish_cmd_for_target.call_args)


    @patch('yadtreceiver.log')
    def test_should_publish_event_about_started_command_on_target (self, mock_log):
        mock_receiver = Mock(Receiver)
        mock_receiver.configuration = {'hostname' : 'hostname'}
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.publish_start(mock_receiver, mock_event)

        self.assertEquals(call('devabc123', 'yadtshell', 'started', '(hostname) target[devabc123] request: command="yadtshell", arguments=[\'update\']'), mock_broadcaster.publish_cmd_for_target.call_args)


    @patch('yadtreceiver.Event')
    def test_should_handle_request (self, mock_event_class):
        mock_receiver = Mock(Receiver)
        mock_event = Mock(Event)
        mock_event_class.return_value = mock_event

        Receiver.onEvent(mock_receiver, 'target', {'id': 'request', 'cmd': 'command', 'args': 'args'})

        self.assertEqual(call('target', {'id': 'request', 'cmd': 'command', 'args': 'args'}), mock_event_class.call_args)
        self.assertEqual(call(mock_event), mock_receiver.handle_request.call_args)


    @patch('yadtreceiver.Event')
    @patch('yadtreceiver.log')
    def test_should_publish_event_about_failed_request_when_handle_request_fails (self, mock_log, mock_event_class):
        mock_receiver = Mock(Receiver)
        mock_receiver.handle_request.side_effect = ReceiverException('It failed!')
        mock_event = Mock(Event)
        mock_event_class.return_value = mock_event

        Receiver.onEvent(mock_receiver, 'target', {'id': 'request', 'cmd': 'command', 'args': 'args'})

        self.assertEqual(call('target', {'id': 'request', 'cmd': 'command', 'args': 'args'}), mock_event_class.call_args)
        self.assertEqual(call(mock_event, 'It failed!'), mock_receiver.publish_failed.call_args)


    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_refresh_connection (self, mock_reactor):
        mock_receiver = Mock(Receiver)
        
        Receiver._refresh_connection(mock_receiver, 123)
    
        self.assertEquals(call(123, mock_receiver._refresh_connection), mock_reactor.callLater.call_args)


    @patch('yadtreceiver.reactor')
    def test_should_close_connection_to_broadcaster_when_not_first_call (self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        Receiver._refresh_connection(mock_receiver, 123)
        
        self.assertEquals(call(), mock_broadcaster.client.sendClose.call_args)


    @patch('yadtreceiver.reactor')
    def test_should_not_close_connection_to_broadcaster_when_first_call (self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        Receiver._refresh_connection(mock_receiver, 123, first_call=True)
        
        self.assertEquals(None, mock_broadcaster.client.sendClose.call_args)


    @patch('yadtreceiver.log')
    def test_should_set_the_client_to_none (self, mock_log):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_broadcaster.client = 'Test client'
        mock_receiver.broadcaster = mock_broadcaster
        
        Receiver.onConnectionLost(mock_receiver, 'Spam eggs.')
        
        self.assertEquals(None, mock_broadcaster.client)
        
        
    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_when_client_available (self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_broadcaster.client = 'Test client'
        mock_receiver.broadcaster = mock_broadcaster
        
        Receiver._client_watchdog(mock_receiver)
        
        self.assertEquals(call(1, mock_receiver._client_watchdog), mock_reactor.callLater.call_args)


    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available (self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        
        Receiver._client_watchdog(mock_receiver)
        
        self.assertEquals(call(1, mock_receiver._client_watchdog, 2), mock_reactor.callLater.call_args)


    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available_and_double_delay_when_delay_of_two_is_given (self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        
        Receiver._client_watchdog(mock_receiver, delay=2)
        
        self.assertEquals(call(2, mock_receiver._client_watchdog, 4), mock_reactor.callLater.call_args)


    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available_and_double_delay_when_delay_of_four_is_given (self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        
        Receiver._client_watchdog(mock_receiver, delay=4)
        
        self.assertEquals(call(4, mock_receiver._client_watchdog, 8), mock_reactor.callLater.call_args)


    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available_and_return_sixty_as_maximum_delay_when_delay_of_one_sixty_is_given (self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        
        Receiver._client_watchdog(mock_receiver, delay=60)
        
        self.assertEquals(call(60, mock_receiver._client_watchdog, 60), mock_reactor.callLater.call_args)


    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_return_result_of_connect_broadcaster (self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        mock_receiver._connect_broadcaster.return_value = 'spam eggs'
        
        actual_result = Receiver._client_watchdog(mock_receiver)
        
        self.assertEquals('spam eggs', actual_result)
        
    
    @patch('yadtreceiver.log')
    def test_should_log_shutting_down_of_service (self, mock_log):
        mock_receiver = Mock(Receiver)
    
        Receiver.stopService(mock_receiver)
        
        # Since all the method does is logging we are asserting it here.
        self.assertEquals(call('shutting down service'), mock_log.msg.call_args)
    