smsMyCabin
==========

This is a small tool to control the power outlets at our cabin using text messages.

The purpose of this tool is not to be an generic tool, but to suit my personal goals.

The tool makes use of 

* USB modem to send and receive text messages via smstools
* 433mhz RF transmitter to communicate with 433mhz power outlets
* USB thermostat to tell the current temperature

Requirements
------------

The tool is heavily dependent on smstools package, and that it's properly configured and setup to call
the smsMyCabin using eventhandler, eg. ```eventhandler = /usr/bin/python /home/pi/smsMyCabin/main.py```

Note: I've included an example config of smstools (smsd.conf) which you're free to base yours on.

Usage
-----

Once you've setup smstools, modem and RF sender:
    $ cd ~
    $ git clone git://git.drogon.net/wiringPi
    $ cd wiringPi
    $ ./build
    $ cd ~
    $ git clone https://github.com/jkaberg/smsMyCabin.git
    $ cd smsMyCabin/
    $ pip install -r requirements.txt
    .....
    $ chmod +x main.py

Make sure you've whitelisted your number in main.py. After that you should be able to send text's to your smsMyCabin :-)