# Build for Windows

## PyInstaller

PyInstaller freezes (packages) Python applications into stand-alone executables, under Windows, GNU/Linux, Mac OS X, FreeBSD, Solaris and AIX.

Install PyInstaller:

    $ pip3 install pyinstaller

Go to your program’s directory and run (Before delete: build/, dist/ and __pycache__/ folders?):

    $ pyinstaller.exe tauno-serial-plotter.spec --noconsole

This will generate the bundle in a subdirectory called dist.

## Inno Setup

## Links

* [realpython.com/pyinstaller-python/](https://realpython.com/pyinstaller-python/)
* [pyinstaller.readthedocs.io/en/stable/spec-files.html](https://pyinstaller.readthedocs.io/en/stable/spec-files.html)
* Inno Setup [jrsoftware.org/isdl.php#stable](https://jrsoftware.org/isdl.php#stable)

 ___

Copyright 2021-2022 Tauno Erik https://taunoerik.art
