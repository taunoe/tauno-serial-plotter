# Build snap

## Install

    $ pip install --upgrade setuptools
    $ python3 -m pip install --user --upgrade setuptools wheel
    $ sudo apt install snapcraft

This command creates a snap folder in the current directory. The snap folder has a single file called **snapcraft.yaml**.

    $ snapcraft init

## Build

    $ snapcraft
    sudo snap install --devmode snap-file-name

## Publishing

    snapcraft login
    snapcraft register snap-name

After that we need to set the grade to stable and confinement to strict in **snapcraft.yaml**. Next we need to rebuild the snap. Release can be edge, candidate or stable.

    snapcraft
    snapcraft upload snap-file-name --release=candidate

    sudo snap install snap-name --channel=candidate

## Links

 - https://gist.github.com/ForgottenUmbrella/ce6ecd8983e76f6d8ef47e07240eb4ac#snappy
 - https://pakjiddat.netlify.app/posts/creating-snaps-for-pyqt5-applications
 - https://ubuntu.com/tutorials/create-your-first-snap#7-push-to-the-store
 - https://medium.com/oli-systems/the-joy-of-building-snaps-for-python-applications-4fa35c36b1a3