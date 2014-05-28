from unittest import TestCase
from mock import Mock, ANY

from yadtreceiver.voting import create_voting_fsm


class VotingFsmTests(TestCase):

    def setUp(self):
        self.fsm = create_voting_fsm('tracking-id',
                                     'vote',
                                     lambda _: 'broadcasted vote',
                                     lambda _: 'spawned program',
                                     lambda _: 'folded',
                                     lambda _: 'cleaned up',
                                     )

    def test_should_start_in_negotiating_state(self):
        self.assertEqual(self.fsm.current, 'negotiating')

    def test_should_give_up_when_folding(self):
        self.fsm.fold()

        self.assertEqual(self.fsm.current, 'finish')

    def test_should_continue_negotiating_when_calling(self):
        self.fsm.call()

        self.assertEqual(self.fsm.current, 'negotiating')

    def test_should_spawn_program_when_winning(self):
        self.fsm.showdown()

        self.assertEqual(self.fsm.current, 'spawning')

    def test_should_finish_when_spawning_complete(self):
        self.fsm.showdown()
        self.fsm.spawned()

        self.assertEqual(self.fsm.current, 'finish')

    def test_should_invoke_callbacks_on_win(self):
        broadcast_vote = Mock()
        spawn = Mock()
        cleanup = Mock()
        fold = Mock()
        fsm = create_voting_fsm('tracking-id',
                                'vote',
                                broadcast_vote,
                                spawn,
                                fold,
                                cleanup)

        broadcast_vote.assert_called_with(ANY)

        fsm.showdown()
        spawn.assert_called_with(ANY)

        fsm.spawned()
        cleanup.assert_called_with(ANY)

        self.assertEqual(fsm.current, 'finish')

    def test_should_invoke_callbacks_on_lose(self):
        broadcast_vote = Mock()
        spawn = Mock()
        cleanup = Mock()
        fold = Mock()
        fsm = create_voting_fsm('tracking-id',
                                'vote',
                                broadcast_vote,
                                spawn,
                                fold,
                                cleanup)

        broadcast_vote.assert_called_with(ANY)

        fsm.fold()
        fold.assert_called_with(ANY)

        self.assertEqual(fsm.current, 'finish')
