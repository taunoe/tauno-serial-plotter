# Flatpak

Official Flatpak repository is [github.com/flathub/art.taunoerik.tauno-serial-plotter](https://github.com/flathub/art.taunoerik.tauno-serial-plotter).

The Flatpak app [maintenance guide](https://github.com/flathub/flathub/wiki/App-Maintenance).

The manifest must install all Python modules next to the launcher:

```yaml
build-commands:
  - install -D src/tauno-serial-plotter.py /app/bin/tauno-serial-plotter.py
  - install -D src/parser.py /app/bin/parser.py
  - install -D src/serial_workers.py /app/bin/serial_workers.py
  - install -D src/theme.py /app/bin/theme.py
  - install -D src/widgets.py /app/bin/widgets.py
```

`tauno-serial-plotter.py` imports `parser`, `serial_workers`, `theme`, and `widgets` at runtime. If the
Flatpak manifest installs only the launcher, the application will fail with
`ModuleNotFoundError`.

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
