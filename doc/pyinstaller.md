# Build with PyInstaller

PyInstaller freezes (packages) Python applications into stand-alone executables, under Windows, GNU/Linux, Mac OS X, FreeBSD, Solaris and AIX.

Install PyInstaller:

    $ pip3 install pyinstaller

Go to your program’s directory and run (Before delete: build/, dist/ and __pycache__/ folders?):

    $ pyinstaller tauno-serial-plotter.spec

This will generate the bundle in a subdirectory called dist. In first time, latter it generates empty directory!?

## Links
 - [PyInstaller Quickstart](https://www.pyinstaller.org/)