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

* Python3
* Qt5
* pyserial
* pyqtgraph

## Run
    $ chmod +x Tauno-Serial-Plotter.py

    $ ./Tauno-Serial-Plotter.py

or 

    $ python3 ./Tauno-Serial-Plotter.py


