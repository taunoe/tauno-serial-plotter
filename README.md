# Tauno Serial Plotter

[![tauno-serial-plotter](https://snapcraft.io/tauno-serial-plotter/badge.svg)](https://snapcraft.io/tauno-serial-plotter)

Serial Plotter for Arduino and other embedded devices.

## Features

- Simple user interface
- Plotting of multiple variables, with different colors for each
- Can plot both integers and floats
- Can plot negative values
- Auto-scrolls the Time scale (X axis)
- Auto-resizes the Data scale (Y axis)
- Labels

## Example Arduino code

Do not add new line between multiple data items. Only in the end.

Label names cannot contain numbers.

If all data is not labelled. Then the labels will not be displayed.

```C++
Serial.print("Label");
Serial.print(data1);
Serial.print("Label");
Serial.print(data2);
Serial.println();
```

To stop the plotter from auto-scaling add a 'min' and 'max' line.

```C++
Serial.print("Label1");
Serial.print(data1);
Serial.print("Label2");
Serial.print(data2);
Serial.println("Min:0,Max:1023");
```

## Install

### Snap

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-white.svg)](https://snapcraft.io/tauno-serial-plotter)

Install Snap:

```Bash
sudo snap install tauno-serial-plotter
```

Run Snap:

```Bash
snap run tauno-serial-plotter
```

If no ports show up. Then close the app and run these commands. And open the app again:

```Bash
sudo usermod -a -G dialout $USER

sudo snap connect tauno-serial-plotter:raw-usb
```

Uninstall Snap:

```Bash
sudo snap remove tauno-serial-plotter
```

### Flatpak

[<img src="https://flathub.org/assets/badges/flathub-badge-en.png" width="25%" height="25%">](https://flathub.org/apps/details/art.taunoerik.tauno-serial-plotter)

Install Flatpak:

```Bash
flatpak install flathub art.taunoerik.tauno-serial-plotter
```

Run Flatpak:

```Bash
flatpak run art.taunoerik.tauno-serial-plotter
```

Uninstall Flatpak:

```Bash
flatpak uninstall art.taunoerik.tauno-serial-plotter
```

### Windows

Windows version can be found under [Releases](https://github.com/taunoe/tauno-serial-plotter/releases). (TODO: Update it!)

## Plot settings

Once the plot (graph) is created it is possible to change the additional plot settings. Like to disable auto-resize on x or-axis y-axis. Or to export data.

**Right-click** on the plot area.

![Graph settings](img/graph-settings.png)

## Screenshots

Tested on Ubuntu 20.10.

![Screenshot on ubuntu](./img/screenshot.png)

And on Windows 10

![Screenshot on ubuntu](./img/screenshot_win10.png)

## Dialout group

In order to access USB devices on Linux, you need to add your user to the dialout group. Open a terminal window, run the following command and reboot your computer.

```Bash
sudo usermod -a -G dialout $USER
```

## udev.rules

Linux users have to install 99-platformio-udev.rules to accesse serial devices.

```Bash
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core/master/scripts/99-platformio-udev.rules | sudo tee /etc/udev/rules.d/99-platformio-udev.rules
```

Restart “udev” management tool:

```Bash
sudo service udev restart
```

More info: https://docs.platformio.org/en/latest/faq.html#faq-udev-rules

## Run Python script

### Requirements

Requirements if you use python script to run it.

Python 3.7, PyQt5, pyserial, pyqtgraph

```Bash
sudo apt install python3-pip

pip install PyQt5

pip install pyserial pyqtgraph
```

### Run

```Bash
cd src/

chmod +x tauno-serial-plotter.py

./tauno-serial-plotter.py
```

or

```Bash
python3 ./tauno-serial-plotter.py
```

 ___

Copyright 2021-2024 Tauno Erik https://taunoerik.art
