#!/bin/bash
PYTHONPATH=src/main/python twistd -n -l - -y src/main/python/yadtreceiver/yadtreceiver.tac
