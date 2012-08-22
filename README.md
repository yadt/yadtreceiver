# yadtreceiver

Using yadtreceiver should make it easy to integrate yadt into your build
infrastructure.

# Installation

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
