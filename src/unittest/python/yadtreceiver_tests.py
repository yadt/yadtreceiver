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
import yadtreceiver


__author__ = 'Michael Gruber'

import unittest
from collections import defaultdict

from mock import Mock, call, patch, MagicMock
from twisted.python.logfile import LogFile

from yadtreceiver import (__version__,
                          Receiver,
                          ReceiverException,
                          FileSystemWatcher,
                          _write_metrics,
                          _reset_metrics,
                          )
from yadtreceiver.configuration import ReceiverConfig
from yadtreceiver.events import Event
from twisted.python import filepath


class YadtReceiverTests (unittest.TestCase):

    def test_if_this_test_fails_maybe_you_have_yadtreceiver_installed_locally(self):
        self.assertEqual('${version}', __version__)

    @patch('yadtreceiver.LogFile')
    @patch('yadtreceiver.log')
    def test_should_call_start_logging_when_initializing_twisted_logging(self, mock_log, mock_log_file_class):
        receiver = Receiver()
        receiver.set_configuration({'log_filename': 'log/file.log',
                                    'targets': set(['devabc123']),
                                    'broadcaster_host': 'broadcaster_host',
                                    'broadcaster_port': 1234})
        mock_log_file = Mock(LogFile)
        mock_log_file_class.fromFullPath.return_value = mock_log_file

        receiver.initialize_twisted_logging()

        self.assertEqual(
            call('log/file.log', rotateLength=20000000, maxRotatedFiles=10),
            mock_log_file_class.fromFullPath.call_args)
        self.assertEquals(call(mock_log_file), mock_log.startLogging.call_args)

    def test_should_set_configuration(self):
        configuration = 'configuration'
        receiver = Receiver()

        receiver.set_configuration(configuration)

        self.assertEquals(configuration, receiver.configuration)

    @patch('yadtreceiver.WampBroadcaster')
    def test_should_initialize_broadcaster_when_connecting_broadcaster(self, mock_wamb):
        configuration = {'broadcaster_host': 'broadcaster-host',
                         'broadcaster_port': 1234}
        receiver = Receiver()
        receiver.set_configuration(configuration)

        receiver._connect_broadcaster()

        self.assertEquals(
            call('broadcaster-host', 1234, 'yadtreceiver'), mock_wamb.call_args)

    @patch('yadtreceiver.WampBroadcaster')
    def test_should_add_session_handler_to_broadcaster_when_connecting_broadcaster(self, mock_wamb):
        receiver = Receiver()
        configuration = {'broadcaster_host': 'broadcasterhost',
                         'broadcaster_port': 1234}
        receiver.set_configuration(configuration)
        mock_broadcaster_client = Mock()
        mock_wamb.return_value = mock_broadcaster_client

        receiver._connect_broadcaster()

        self.assertEquals(
            call(receiver.onConnect), mock_broadcaster_client.addOnSessionOpenHandler.call_args)

    @patch('yadtreceiver.WampBroadcaster')
    def test_should_connect_broadcaster_when_connecting_broadcaster(self, mock_wamb):
        receiver = Receiver()
        configuration = {'broadcaster_host': 'broadcaster-host',
                         'broadcaster_port': 1234}
        receiver.set_configuration(configuration)
        mock_broadcaster_client = Mock()
        mock_wamb.return_value = mock_broadcaster_client

        receiver._connect_broadcaster()

        self.assertEquals(call(), mock_broadcaster_client.connect.call_args)

    @patch('yadtreceiver.log')
    @patch('__builtin__.exit')
    def test_should_exit_when_no_target_configured(self, mock_exit, mock_log):
        receiver = Receiver()
        receiver.set_configuration({'allowed_targets': set(),
                                    'broadcaster_host': 'broadcaster_host',
                                    'broadcaster_port': 1234})
        mock_broadcaster_client = Mock()
        receiver.broadcaster = mock_broadcaster_client

        receiver.onConnect()

        self.assertEquals(call(1), mock_exit.call_args)

    @patch('yadtreceiver.LogFile')
    @patch('yadtreceiver.log')
    def test_should_initialize_watchdog_and_start_connection_when_service_starts(self, mock_log, mock_log_file):
        mock_receiver = Mock(Receiver)
        mock_receiver.configuration = {'log_filename': 'log/file.log'}

        Receiver.startService(mock_receiver)

        self.assertEquals(call(), mock_receiver._client_watchdog.call_args)
        self.assertEquals(
            call(first_call=True), mock_receiver._refresh_connection.call_args)

    def test_should_initialize_logging_when_service_starts(self):
        mock_receiver = Mock(Receiver)

        Receiver.startService(mock_receiver)

        self.assertEquals(
            call(), mock_receiver.initialize_twisted_logging.call_args)

    def test_should_subscribe_to_target_from_configuration_when_connected(self):
        receiver = Receiver()
        mock_broadcaster_client = Mock()
        receiver.broadcaster = mock_broadcaster_client
        receiver.set_configuration({'allowed_targets': set(['devabc123']),
                                    'broadcaster_host': 'broadcaster_host',
                                    'broadcaster_port': 1234})
        receiver.onConnect()

        self.assertEquals(call('devabc123', receiver.onEvent),
                          mock_broadcaster_client.client.subscribe.call_args)

    def test_should_subscribe_to_targets_from_configuration_in_alphabetical_order_when_connected(self):
        receiver = Receiver()
        mock_broadcaster_client = Mock()
        receiver.broadcaster = mock_broadcaster_client
        receiver.set_configuration(
            {'allowed_targets': set(['dev01', 'dev02', 'dev03']),
             'broadcaster_host': 'broadcaster_host',
             'broadcaster_port': 1234})

        receiver.onConnect()

        self.assertEquals([call('dev01', receiver.onEvent),
                           call('dev02', receiver.onEvent),
                           call('dev03', receiver.onEvent)], mock_broadcaster_client.client.subscribe.call_args_list)

    @patch('os.path.exists')
    def test_should_raise_exception_when_target_directory_does_not_exist(self, mock_exists):
        mock_exists.return_value = False
        receiver = Receiver()
        configuration = {'hostname': 'hostname',
                         'targets_directory': '/etc/yadtshell/targets/'}
        receiver.set_configuration(configuration)

        self.assertRaises(
            ReceiverException, receiver.get_target_directory, 'spargel')

    @patch('os.path.exists')
    def test_should_append_target_name_to_targets_directory(self, mock_exists):
        mock_exists.return_value = True
        receiver = Receiver()
        configuration = {'hostname': 'hostname',
                         'targets_directory': '/etc/yadtshell/targets/'}
        receiver.set_configuration(configuration)

        actual_target_directory = receiver.get_target_directory('spargel')

        self.assertEquals(
            '/etc/yadtshell/targets/spargel', actual_target_directory)

    @patch('os.path.exists')
    def test_should_join_target_name_with_targets_directory(self, mock_exists):
        mock_exists.return_value = True
        receiver = Receiver()
        configuration = {'hostname': 'hostname',
                         'targets_directory': '/etc/yadtshell/targets/'}
        receiver.set_configuration(configuration)

        actual_target_directory = receiver.get_target_directory('spargel')

        self.assertEquals(
            '/etc/yadtshell/targets/spargel', actual_target_directory)

    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.ProcessProtocol')
    def test_should_spawn_new_process_on_reactor(self, mock_protocol, mock_reactor):
        mock_protocol.return_value = 'mock-protocol'
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster
        mock_receiver.get_target_directory.return_value = '/etc/yadtshell/targets/devabc123'
        mock_receiver.states = {None: Mock()}

        mock_receiver.configuration = {'hostname': 'hostname',
                                       'python_command': '/usr/bin/python',
                                       'script_to_execute': '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.perform_request(mock_receiver, mock_event, Mock())

        self.assertEquals(call('hostname', mock_broadcaster, 'devabc123',
                          '/usr/bin/python /usr/bin/yadtshell update', tracking_id=None), mock_protocol.call_args)
        self.assertEquals(call('mock-protocol', '/usr/bin/python', [
                          '/usr/bin/python', '/usr/bin/yadtshell', 'update'], path='/etc/yadtshell/targets/devabc123', env={}), mock_reactor.spawnProcess.call_args)

    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.ProcessProtocol')
    @patch('yadtreceiver.log')
    def test_should_spawn_new_process_on_reactor_even_when_not_registered(self, _, mock_protocol, mock_reactor):
        mock_protocol.return_value = 'mock-protocol'
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster
        mock_receiver.get_target_directory.return_value = '/etc/yadtshell/targets/devabc123'
        mock_receiver.states = {}

        mock_receiver.configuration = {'hostname': 'hostname',
                                       'python_command': '/usr/bin/python',
                                       'script_to_execute': '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.perform_request(mock_receiver, mock_event, Mock())

        self.assertEquals(call('hostname', mock_broadcaster, 'devabc123',
                          '/usr/bin/python /usr/bin/yadtshell update', tracking_id=None), mock_protocol.call_args)
        self.assertEquals(call('mock-protocol', '/usr/bin/python', [
                          '/usr/bin/python', '/usr/bin/yadtshell', 'update'], path='/etc/yadtshell/targets/devabc123', env={}), mock_reactor.spawnProcess.call_args)

    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.ProcessProtocol')
    def test_should_broadcast_error_when_spawning_fails(self, mock_protocol, mock_reactor):
        mock_protocol.side_effect = RuntimeError('Booom!')
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster
        mock_receiver.get_target_directory.return_value = '/etc/yadtshell/targets/devabc123'
        mock_receiver.states = {None: Mock()}

        mock_receiver.configuration = {'hostname': 'hostname',
                                       'python_command': '/usr/bin/python',
                                       'script_to_execute': '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.perform_request(mock_receiver, mock_event, Mock())

        mock_receiver.publish_failed.assert_called_with(mock_event, "<type 'exceptions.RuntimeError'> : Booom!")

    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.ProcessProtocol')
    def test_should_create_process_protocol_with_tracking_id_if_given(self, mock_protocol, mock_reactor):
        mock_protocol.return_value = 'mock-protocol'
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.states = {'foo': Mock()}
        mock_receiver.broadcaster = mock_broadcaster
        mock_receiver.get_target_directory.return_value = '/etc/yadtshell/targets/devabc123'

        mock_receiver.configuration = {'hostname': 'hostname',
                                       'python_command': '/usr/bin/python',
                                       'script_to_execute': '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update', '--tracking-id=foo']

        Receiver.perform_request(mock_receiver, mock_event, Mock())

        expected_command_with_arguments = '/usr/bin/python /usr/bin/yadtshell update --tracking-id=foo'

        self.assertEqual(
            call(
                'hostname', mock_broadcaster, 'devabc123', expected_command_with_arguments,
                tracking_id='foo'), mock_protocol.call_args)

    @patch('yadtreceiver.reactor')
    @patch('yadtreceiver.ProcessProtocol')
    def test_should_create_process_protocol_with_no_tracking_id_if_not_given(self, mock_protocol, mock_reactor):
        mock_protocol.return_value = 'mock-protocol'
        mock_receiver = Mock(Receiver)
        mock_receiver.states = {None: Mock()}
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster
        mock_receiver.get_target_directory.return_value = '/etc/yadtshell/targets/devabc123'

        mock_receiver.configuration = {'hostname': 'hostname',
                                       'python_command': '/usr/bin/python',
                                       'script_to_execute': '/usr/bin/yadtshell'}

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.perform_request(mock_receiver, mock_event, Mock())

        expected_command_with_arguments = '/usr/bin/python /usr/bin/yadtshell update'

        self.assertEqual(call('hostname', mock_broadcaster, 'devabc123',
                         expected_command_with_arguments, tracking_id=None), mock_protocol.call_args)

    @patch('yadtreceiver.log')
    def test_should_publish_event_about_failed_command_on_target(self, mock_log):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        mock_event = Mock(Event)
        mock_event.target = 'devabc123'
        mock_event.tracking_id = 'any-tracking-id'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.publish_failed(mock_receiver, mock_event, 'It failed!')

        mock_broadcaster.publish_cmd_for_target.assert_called_with(
            'devabc123',
            'yadtshell',
            'failed',
            'It failed!',
            tracking_id='any-tracking-id')

    @patch('yadtreceiver.log')
    def test_should_publish_event_about_started_command_on_target(self, mock_log):
        mock_receiver = Mock(Receiver)
        mock_receiver.configuration = {'hostname': 'hostname'}
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        mock_event = Mock(Event)
        mock_event.tracking_id = 'any-tracking-id'
        mock_event.target = 'devabc123'
        mock_event.command = 'yadtshell'
        mock_event.arguments = ['update']

        Receiver.publish_start(mock_receiver, mock_event)

        mock_broadcaster.publish_cmd_for_target.assert_called_with(
            'devabc123',
            'yadtshell',
            'started',
            '(hostname) target[devabc123] request: command="yadtshell", arguments=[\'update\']',
            tracking_id='any-tracking-id')

    @patch('yadtreceiver.events.Event')
    def test_should_handle_request(self, mock_event_class):
        mock_receiver = Mock(Receiver)
        mock_receiver.states = {None: Mock()}
        mock_event = Mock(Event)
        mock_event.is_a_vote = False
        mock_event_class.return_value = mock_event

        Receiver.onEvent(mock_receiver, 'target', {
                         'id': 'request', 'cmd': 'command', 'args': 'args'})

        self.assertEqual(
            call('target', {'id': 'request', 'cmd': 'command', 'args': 'args'}), mock_event_class.call_args)
        self.assertEqual(
            call(mock_event), mock_receiver.handle_request.call_args)

    @patch('yadtreceiver.events.Event')
    @patch('yadtreceiver.log')
    def test_should_publish_event_about_failed_request_when_handle_request_fails(self, mock_log, mock_event_class):
        mock_receiver = Mock(Receiver)
        mock_receiver.handle_request.side_effect = ReceiverException(
            'It failed!')
        mock_receiver.states = {'some-id': Mock()}
        mock_event = Mock(Event)
        mock_event.is_a_vote = False
        mock_event.tracking_id = 'some-id'
        mock_event_class.return_value = mock_event

        Receiver.onEvent(mock_receiver, 'target', {
                         'id': 'request', 'cmd': 'command', 'args': 'args'})

        self.assertEqual(
            call('target', {'id': 'request', 'cmd': 'command', 'args': 'args'}), mock_event_class.call_args)
        self.assertEqual(
            call(mock_event, 'It failed!'), mock_receiver.publish_failed.call_args)

    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_refresh_connection(self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_receiver.broadcaster = Mock()

        Receiver._refresh_connection(mock_receiver, 123)

        self.assertEquals(
            call(123, mock_receiver._refresh_connection), mock_reactor.callLater.call_args)

    @patch('yadtreceiver.reactor')
    def test_should_close_connection_to_broadcaster_when_not_first_call(self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        Receiver._refresh_connection(mock_receiver, 123)

        self.assertEquals(call(), mock_broadcaster.client.sendClose.call_args)

    @patch('yadtreceiver.reactor')
    def test_should_not_close_connection_to_broadcaster_when_first_call(self, mock_reactor):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_receiver.broadcaster = mock_broadcaster

        Receiver._refresh_connection(mock_receiver, 123, first_call=True)

        self.assertEquals(None, mock_broadcaster.client.sendClose.call_args)

    @patch('yadtreceiver.log')
    def test_should_set_the_client_to_none(self, mock_log):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_broadcaster.client = 'Test client'
        mock_receiver.broadcaster = mock_broadcaster

        Receiver.onConnectionLost(mock_receiver, 'Spam eggs.')

        self.assertEquals(None, mock_broadcaster.client)

    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_when_client_available(self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        mock_broadcaster = Mock()
        mock_broadcaster.client = 'Test client'
        mock_receiver.broadcaster = mock_broadcaster

        Receiver._client_watchdog(mock_receiver)

        self.assertEquals(
            call(1, mock_receiver._client_watchdog), mock_reactor.callLater.call_args)

    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available(self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)

        Receiver._client_watchdog(mock_receiver)

        self.assertEquals(
            call(1, mock_receiver._client_watchdog, 2), mock_reactor.callLater.call_args)

    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available_and_double_delay_when_delay_of_two_is_given(self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)

        Receiver._client_watchdog(mock_receiver, delay=2)

        self.assertEquals(
            call(2, mock_receiver._client_watchdog, 4), mock_reactor.callLater.call_args)

    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available_and_double_delay_when_delay_of_four_is_given(self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)

        Receiver._client_watchdog(mock_receiver, delay=4)

        self.assertEquals(
            call(4, mock_receiver._client_watchdog, 8), mock_reactor.callLater.call_args)

    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_queue_call_to_client_watchdog_no_client_available_and_return_sixty_as_maximum_delay_when_delay_of_one_sixty_is_given(self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)

        Receiver._client_watchdog(mock_receiver, delay=60)

        self.assertEquals(
            call(60, mock_receiver._client_watchdog, 60), mock_reactor.callLater.call_args)

    @patch('yadtreceiver.log')
    @patch('yadtreceiver.reactor')
    def test_should_return_result_of_connect_broadcaster(self, mock_reactor, mock_log):
        mock_receiver = Mock(Receiver)
        mock_receiver._connect_broadcaster.return_value = 'spam eggs'

        actual_result = Receiver._client_watchdog(mock_receiver)

        self.assertEquals('spam eggs', actual_result)

    @patch('yadtreceiver.log')
    def test_should_log_shutting_down_of_service(self, mock_log):
        mock_receiver = Mock(Receiver)

        Receiver.stopService(mock_receiver)

        # Since all the method does is logging we are asserting it here.
        self.assertEquals(
            call('shutting down service'), mock_log.msg.call_args)

    def test_determine_tracking_id_should_return_tracking_id_if_present(self):
        list_with_tracking_id = [
            'foo', 'bar', 'baz=fubar', '--tracking-id=test', 'foofoo']
        self.assertEqual(
            yadtreceiver._determine_tracking_id(list_with_tracking_id), 'test')

    def test_determine_tracking_id_should_return_none_if_no_tracking_id_present(self):
        list_with_tracking_id = [
            'foo', 'bar', 'baz=fubar', '--no-tracking-id=test', 'foofoo']
        self.assertEqual(
            yadtreceiver._determine_tracking_id(list_with_tracking_id), None)

    def test_subscribe_target_is_allowed(self):
        mock_receiver = Mock(Receiver)
        mock_config = Mock(ReceiverConfig)
        mock_config.configuration = {'allowed_targets': ['foo']}
        mock_config.__getitem__ = lambda _self, key: mock_config.configuration[
            key]
        mock_receiver.broadcaster = Mock()
        mock_receiver.broadcaster.client = Mock()
        mock_receiver.configuration = mock_config

        Receiver.subscribeTarget(mock_receiver, 'foo')

        mock_receiver.configuration.reload_targets.assert_called_with()
        mock_receiver.broadcaster.client.subscribe.assert_called_with(
            'foo', mock_receiver.onEvent)


class ConnectionRefreshTests(unittest.TestCase):

    @patch('yadtreceiver.datetime')
    def test_should_refresh_when_connected_and_hour_is_2_am(self, datetime):
        time = Mock()
        datetime.now.return_value = time
        time.hour = 2
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.broadcaster.client = Mock()

        self.assertTrue(Receiver._should_refresh_connection(receiver))

    @patch('yadtreceiver.datetime')
    def test_should_not_refresh_when_no_broadcaster_but_hour_is_2_am(self, datetime):
        time = Mock()
        datetime.now.return_value = time
        time.hour = 2
        receiver = Mock(Receiver)

        self.assertFalse(Receiver._should_refresh_connection(receiver))

    @patch('yadtreceiver.datetime')
    def test_should_not_refresh_when_no_broadcastclient_but_hour_is_2_am(self, datetime):
        time = Mock()
        datetime.now.return_value = time
        time.hour = 2
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.broadcaster.client = None

        self.assertFalse(Receiver._should_refresh_connection(receiver))

    @patch('yadtreceiver.datetime')
    def test_should_not_refresh_when_connected_but_hour_is_not_2_am(self, datetime):
        time = Mock()
        datetime.now.return_value = time
        time.hour = 8
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.broadcaster.client = Mock()

        self.assertFalse(Receiver._should_refresh_connection(receiver))


class YadtReceiverFilesytemWatcherTests(unittest.TestCase):

    def setUp(self):
        self.CREATE = 0x40000100
        self.DELETE = 0x40000200
        self.PATH = filepath.FilePath('/foo/bar')

    def test_for_missing_callbacks(self):
        fs = FileSystemWatcher('/foo/bar')
        self.assertRaises(
            AttributeError, fs.onChange, 'watch', self.PATH, self.CREATE)

    def test_for_mock_callback_create(self):
        mock_receiver = Mock(Receiver)
        fs = FileSystemWatcher('/foo/bar')
        fs.onChangeCallbacks = dict(create=mock_receiver.subscribeTarget,
                                    delete=mock_receiver.unsubscribeTarget)
        fs.onChange('watch', self.PATH, self.CREATE)
        self.assertTrue(mock_receiver.subscribeTarget.called)

    def test_for_mock_callback_delete(self):
        mock_receiver = Mock(Receiver)
        fs = FileSystemWatcher('/foo/bar')
        fs.onChangeCallbacks = dict(create=mock_receiver.subscribeTarget,
                                    delete=mock_receiver.unsubscribeTarget)
        fs.onChange('watch', self.PATH, self.DELETE)
        self.assertTrue(mock_receiver.unsubscribeTarget.called)

    @patch('yadtreceiver.inotify')
    def test_inotify_is_started(self, mock_inotify):
        fs = FileSystemWatcher('/foo/bar')
        fs.startService()
        self.assertTrue(mock_inotify.INotify().startReading.called)


class MetricsTests(unittest.TestCase):

    def test_should_not_write_anything_when_no_metrics_given(self):
        mock_file = Mock()
        metrics = {}

        _write_metrics(metrics, mock_file)

        self.assertFalse(mock_file.write.called)

    def test_should_write_metrics(self):
        mock_file = Mock()
        metrics = {
            "metric1": 21,
            "metric2": 42
        }

        _write_metrics(metrics, mock_file)

        self.assertEquals(mock_file.write.call_args_list,
                          [call('metric2=42\n'),
                           call('metric1=21\n')])

    @patch.dict('yadtreceiver.METRICS', {'foo': 42}, clear=True)
    @patch('yadtreceiver.open', create=True)
    def test_write_metrics_to_file(self, open_):
        # initialize a receiver with given configuration
        configuration = {'metrics_directory': '/tmp/metrics',
                         'metrics_file': '/tmp/metrics/yrc.metrics'
                         }

        yrc = Receiver()
        yrc.set_configuration(configuration)
        open_.return_value = MagicMock(spec=file)
        yrc.write_metrics_to_file()
        open_.assert_called_once_with('/tmp/metrics/yrc.metrics')
        file_handle = open_.return_value.__enter__.return_value
        file_handle.write.assert_called_once_with('foo=42\n')


class TestResetMetrics(unittest.TestCase):

    def test_should_remove_metrics_when_they_are_empty(self):
        metrics = {
            "empty": 0,
            "empty_long": 0L,
        }

        _reset_metrics(metrics)

        self.assertEquals(metrics,
                          {})

    def test_should_just_reset_metrics_when_they_are_not_empty(self):
        metrics = {
            "full": 42,
            "full_long": 42L,
        }

        _reset_metrics(metrics)

        self.assertEquals(metrics,
                          {"full": 0,
                           "full_long": 0,
                           })
