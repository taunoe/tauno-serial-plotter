# Tauno Serial Plotter
Serial Plotter for Arduino and other embedded devices.

Incoming data should be string. Ending with new line character.
Like:

    label2la15be17el28-31/42-54 78

or

    5-10-22-33-40-55-62-75

Script will extracts all numbers and generate graph.

Tested on Ubuntu.


![Screenshot on ubuntu](https://github.com/taunoe/tauno-serial-plotter/blob/master/img/screenshot.png)

## Requirements

    $ sudo apt install python3-pip

* Python3
* Qt5
* pyserial 3.4 ($ pip3 install pyserial)
* pyqtgraph 0.10.0 ($ pip3 install pyqtgraph)

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


