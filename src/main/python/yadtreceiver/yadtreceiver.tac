#!/usr/bin/env python
#
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
    Start-up and configuration of the yadtreceiver application.
"""

__author__ = 'Arne Hilmann, Michael Gruber'


from twisted.application import service
from twisted.internet.defer import setDebugging

from yadtreceiver import __version__, Receiver
from yadtreceiver.configuration import load

setDebugging(True)

configuration = load('/etc/yadtshell/receiver.cfg')
application = service.Application('yadtreceiver version %s' % __version__)

receiver = Receiver()
receiver.set_configuration(configuration)
receiver.setServiceParent(application)
