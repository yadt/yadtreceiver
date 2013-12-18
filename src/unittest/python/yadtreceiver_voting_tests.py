from unittest import TestCase
from mock import Mock, patch
from yadtreceiver import Receiver


class YadtreceiverVotingTests(TestCase):

    def test_should_fold_when_higher_vote_received(self):
        receiver = Mock(Receiver)
        fsm = Mock()
        fsm.vote = 5
        receiver.states = {'id123': fsm}
        higher_vote_event = {'id': 'vote',
                             'tracking_id': 'id123',
                             'payload': 42
                             }

        Receiver.onEvent(receiver, 'target', higher_vote_event)

        fsm.fold.assert_called_with()

    def test_should_call_when_lower_vote_received(self):
        receiver = Mock(Receiver)
        fsm = Mock()
        fsm.vote = 42
        receiver.states = {'id123': fsm}
        lower_vote_event = {'id': 'vote',
                            'tracking_id': 'id123',
                            'payload': 5
                            }

        Receiver.onEvent(receiver, 'target', lower_vote_event)

        fsm.call.assert_called_with()

    @patch('yadtreceiver.random_uuid')
    def test_should_vote_when_handling_request(self, uuid_fun):
        uuid_fun.return_value = "1234-5678"
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.states = {'foo': None}
        event = Mock()
        event.arguments = ['--tracking-id=foo']
        event.target = 'target'
        Receiver.handle_request(receiver, event)

        receiver.broadcaster._sendEvent.assert_called_with(
            'vote', data='1234-5678', tracking_id='foo', target='target')

    @patch('yadtreceiver.random_uuid')
    def test_should_initialize_fsm_when_handling_request(self, uuid_fun):
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.states = {'foo': None}
        event = Mock()
        event.arguments = ['--tracking-id=foo']
        Receiver.handle_request(receiver, event)

        request_fsm = receiver.states['foo']
        self.assertEqual(request_fsm.current, 'negotiating')

    @patch('yadtreceiver.reactor.callLater')
    def test_should_announce_showdown(self, call_later):
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.states = {'foo': None}
        event = Mock()
        event.arguments = ['--tracking-id=foo']

        Receiver.handle_request(receiver, event)

        call_later.assert_called_with(10, receiver.states['foo'].showdown)

    def test_should_cleanup_fsm_after_finishing(self):
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.states = {'foo': None}
        receiver = Mock(Receiver)
        receiver.broadcaster = Mock()
        receiver.states = {'foo': None}
        event = Mock()
        event.arguments = ['--tracking-id=foo']
        Receiver.handle_request(receiver, event)

        receiver.states['foo'].showdown()
        receiver.states['foo'].spawned()

        self.assertEqual(receiver.states, {})
