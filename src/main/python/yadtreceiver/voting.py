#   yadtreceiver
#   Copyright (C) 2013 Immobilien Scout GmbH
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
    Provides a state machine to trade votes with other receivers in order to
    determine which receiver handles a specific request.
"""

from fysom import Fysom


def create_voting_fsm(tracking_id,
                      vote,
                      broadcast_vote,
                      spawn_yadtshell,
                      cleanup_fsm):
    fsm = Fysom({
        'initial': 'negotiating',
        'events': [
            {'name': 'call', 'src':
                'negotiating', 'dst': 'negotiating'},
            {'name': 'fold', 'src': 'negotiating', 'dst': 'finish'},
            {'name': 'showdown', 'src':
                'negotiating', 'dst': 'spawning'},
            {'name': 'spawned', 'src': 'spawning', 'dst': 'finish'},
            {'name': 'showdown', 'src': 'finish', 'dst': 'finish'}
        ],
        'callbacks': {
            'onnegotiating': broadcast_vote,
            'onspawning': spawn_yadtshell,
            'onfinish': cleanup_fsm
        }
    })
    fsm.tracking_id = tracking_id
    fsm.vote = vote
    return fsm
