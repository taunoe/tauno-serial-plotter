# Build snap

**Note:**
Serial port access is restricted in snaps. It is easier to install it with '--devmode'.

```Bash
sudo snap install --devmode tauno-serial-port --channel=beta
```

## Install

```Bash
pip install --upgrade setuptools
python3 -m pip install --user --upgrade setuptools wheel
sudo apt install snapcraft
```

This command creates a snap/ folder in the current directory. The snap folder has a single file called **snap/snapcraft.yaml**.

```Bash
snapcraft init
```

## Build

For local testing check those lines in file snap/snapcraft.yaml:

```Bash
grade: devel # 'devel', must be 'stable' to release into candidate/stable channels
confinement: devmode # 'devmode' or 'strict' to release into candidate/stable channels
```

Build:

```Bash
snapcraft clean
snapcraft
sudo snap install --devmode snap-file-name

snapcraft --debug
snapcraft prime --shell
```

Run:

```Bash
/snap/bin/tauno-serial-plotter
```

## Publishing

```Bash
snapcraft login
snapcraft register snap-name
```

After that we need to set the grade to stable and confinement to strict in **snapcraft.yaml**. Next we need to rebuild the snap. Release can be edge, candidate or stable.

```Bash
snapcraft clean

snapcraft
snapcraft upload snap-file-name --release=candidate

sudo snap install snap-name --channel=candidate
```

## Uninstall

```Bash
sudo snap remove snap-name
```

## Change channel after install

stabel, candidate, beta, edge

sudo snap refresh --channel=edge tauno-serial-plotter

## notes

sudo usermod -a -G dialout $USER

sudo snap connect tauno-serial-plotter:raw-usb

## Links

- [How to publish Python apps for human beings](https://gist.github.com/ForgottenUmbrella/ce6ecd8983e76f6d8ef47e07240eb4ac#snappy)
- [Creating Snaps for PyQt5 applications](https://pakjiddat.netlify.app/posts/creating-snaps-for-pyqt5-applications)
- [Create your first snap](https://ubuntu.com/tutorials/create-your-first-snap)
- [The Joy of Building Snaps for Python Applications](https://medium.com/oli-systems/the-joy-of-building-snaps-for-python-applications-4fa35c36b1a3)
