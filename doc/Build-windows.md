# Build for Windows

## Requirments

Install PyInstaller:

```Bash
pip install pyinstaller
```

Download and install [Inno Setup](https://jrsoftware.org/isdl.php#stable).


## Build

PyInstaller freezes (packages) Python applications into stand-alone executables, under Windows, GNU/Linux, Mac OS X, FreeBSD, Solaris and AIX.

Go to tauno-serial-plotter/ directory and run:

```Bash
pyinstaller.exe tauno-serial-plotter.spec --noconsole
```

This will generate the bundle in a subdirectory **dist/**.

```Bash
dist/tauno-serial-plotter/
```

## Inno Setup

Select: inno-setup-script.iss

Run.

Folder tauno-serial-plotter/Output/ contains setup file.

## Links

* [realpython.com/pyinstaller-python/](https://realpython.com/pyinstaller-python/)
* [pyinstaller.readthedocs.io/en/stable/spec-files.html](https://pyinstaller.readthedocs.io/en/stable/spec-files.html)
* Inno Setup [jrsoftware.org/isdl.php#stable](https://jrsoftware.org/isdl.php#stable)

 ___

Copyright 2021-2022 Tauno Erik https://taunoerik.art
