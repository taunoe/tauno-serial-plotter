# Tauno Serial Plotter
Serial Plotter for Arduino and other embedded devices.

Incoming data should be string. Ending with new line character. Number can be separated with almost any character.
Like:

    label2la15be17el28/31/42/54 78

or

    a2b1.5c1.7d2.8/3.1/4.2/5.4 7.8

But not with **-** unless it is a negative number:

    5-10-22-33-40-55-62-75

Script will extracts all numbers and generate graph.

Tested on Ubuntu 19.10.


![Screenshot on ubuntu](https://github.com/taunoe/tauno-serial-plotter/blob/master/img/screenshot.png)

## Requirements

Python 3.7, PyQt5, pyserial, pyqtgraph

    $ sudo apt install python3-pip python3-pyqt5

    $ pip3 install pyserial pyqtgraph



## udev.rules

Linux users have to install 99-platformio-udev.rules to accesse serial devices.

    $ curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/master/scripts/99-platformio-udev.rules | sudo tee /etc/udev/rules.d/99-platformio-udev.rules

Restart “udev” management tool:

    $ sudo service udev restart

More info: https://docs.platformio.org/en/latest/faq.html#faq-udev-rules

## Run
    $ chmod +x Tauno-Serial-Plotter.py

    $ ./Tauno-Serial-Plotter.py

or 

    $ python3 ./Tauno-Serial-Plotter.py


## Build with fbs

    pip3 install fbs

    fbs startproject

But sourcecode in ./src/main/python/main.py file. (And also 'img' folder https://github.com/taunoe/tauno-serial-plotter/issues/5)

    fbs run

Turn it into a standalone executable:

    fbs freeze

This places a self-contained binary in the target/MyApp/ folder of your current directory.

### Create installer:

On Ubuntu first install fbm: https://fpm.readthedocs.io/en/latest/installing.html

    sudo apt install ruby ruby-dev rubygems build-essential

    gem install --no-document fpm

Now create installer (deb filne on Ubuntu):

    fbs installer

If you are on Windows, you first need to install NSIS and place it on your PATH.
https://github.com/mherrmann/fbs-tutorial


