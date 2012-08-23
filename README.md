# yadtreceiver

Using yadtreceiver should make it easy to integrate yadt into your build
infrastructure.

## Installation

Since yadtreceiver is a python application you can install it using `pip`
 
```bash
sudo pip install https://github.com/downloads/yadt/yadtreceiver/yadtreceiver-0.1.3.tar.gz
```

or using `easy_install`

```bash
easy_install https://github.com/downloads/yadt/yadtreceiver/yadtreceiver-0.1.3.tar.gz
```

Unfortunately tar will not set the permissions as required:

```bash
sudo chmod 755 /etc/init.d/yadtreceiver 
```
## Configuration

Put a file called receiver.cfg into the directory /etc/yadtshell/

```
[receiver]
log_filename = /var/log/yadtreceiver.log
targets = devyadt
targets_directory = /etc/yadtshell/targets
script_to_execute = /usr/bin/yadtshell

[broadcaster]
host = broadcaster.domain.tld
port = 8081

[graphite]
active = yes
host = graphite.domain.tld
port = 2003
```

## Starting service

After installation you will find a minimal service script in `/etc/init.d`.
Maybe you want/need to modify the script to make it fit to your *nix
distribution.
 
```bash
sudo service yadtreceiver start
```