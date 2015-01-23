Slick
=====

Slick is a reference implementation for using the `SoftLayer Python Bindings <https://github.com/softlayer/softlayer-api-python-client>`_. It implements a small web portal using a variety of open source projects to show the type of application you can build with the bindings.

.. WARNING::
   This software is currently in active development. Some expertise is required for initial installation and setup.

Installation
------------
**Prerequirements**
Starting with a fresh install of Ubuntu 14.04-64
```bash
apt-get install libpq-dev sqlite3 python-pip git python-dev
pip install WTForms  wtforms-html5 WTForms-Components
pip install flask
pip install six --upgrade
```

**Get everything running**

If you don't want to have everything in /usr/local/slick make sure to change alembic.ini and config.py

```bash
cd /usr/local/
git clone https://github.com/softlayer/slick.git
cd slick
python setup.py install
```
If setup.py failed to install, make sure you install any missing packages and try again before continuing. Usually the setup will complain about a missing package, so just use pip to install or upgrade it, and you should be ok.


This will setup the database
```bash
alembic upgrade head   
```

Then you need to setup the config file. Just copy it to config.py, end edit the 2 secret strings. You can switch DB providers, but I would recommend sticking with sqlite for now.
```bash
cp config.py.sample slick/config.py
```


This will start the web server on port 5000
```bash
python run.py
```
Then just head over to http://hostname:5000 and you should be able to login with your SoftLayer portal username and password.
To run the server as a daemon just add the & symbol to the end of that command. There is currently no init script or anything fancy like that.

I'll leave seting up nginx as an excersize for the reader.


System Requirements
-------------------
* This library has been tested on Python 2.7 only. It may work on other versions.
* A valid SoftLayer API username and key are required to call SoftLayer's API

Copyright
---------
This software is Copyright (c) 2013 SoftLayer Technologies, Inc.
See the bundled LICENSE file for more information.
