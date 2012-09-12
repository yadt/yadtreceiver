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
    Provides a function to send graphite a update notification.
    
    For more information about graphite please visit:
    http://graphite.wikidot.com/
"""

__author__ = 'Michael Gruber'

from socket import socket
from time import time
from twisted.python import log


def send_update_notification_to_graphite(target, host, port):
    """
        Sends a update notification to the graphite server at host:port.
    """
    try:
        graphite_socket  = socket()
        graphite_address = (host, port)
        graphite_socket.connect(graphite_address)

        timestamp = int(time())
        log.msg('sending update of target %s notification to graphite on %s:%s' % (target, host, port))
        graphite_socket.send('yadt.%s.update 1 %d\n' % (target, timestamp))

    except Exception as e:
        log.err(e)

    finally:
        if graphite_socket:
            graphite_socket.close()
