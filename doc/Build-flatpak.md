# Flatpak

Official Flatpak repository is [github.com/flathub/art.taunoerik.tauno-serial-plotter](https://github.com/flathub/art.taunoerik.tauno-serial-plotter).

The Flatpak app [maintenance guide](https://github.com/flathub/flathub/wiki/App-Maintenance).

The manifest must install both Python modules next to the launcher:

```yaml
build-commands:
  - install -D src/tauno-serial-plotter.py /app/bin/tauno-serial-plotter.py
  - install -D src/theme.py /app/bin/theme.py
```

`tauno-serial-plotter.py` imports `theme` at runtime. If the Flatpak
manifest installs only the launcher, the application will fail with
`ModuleNotFoundError: No module named 'theme'`.

## Some commands

Build localy:

```Bash
flatpak-builder --user --install --force-clean build-dir art.taunoerik.tauno-serial-plotter.yml
```

Run:

```Bash
flatpak run art.taunoerik.tauno-serial-plotter
```

List flatpak apps:

```Bash
flatpak list --app
```

Install from flathub:

```Bash
flatpak install flathub art.taunoerik.tauno-serial-plotter
```

Uninstall:

```Bash
flatpak uninstall art.taunoerik.tauno-serial-plotter
```

 ___

Copyright 2021-2022 Tauno Erik https://taunoerik.art
