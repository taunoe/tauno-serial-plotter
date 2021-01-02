# Building Flatpak

**I managed to get flatpak work, but it does not show any GUI icons!** 

1. Install a runtime and the matching SDK

    $ flatpak install flathub org.kde.Platform org.kde.Sdk

2. Add a manifest file


3. Build & Test

    $ flatpak-builder --user --install build-dir org.flatpak.Tauno-serial-plotter.yml --force-clean
    $ flatpak run org.flatpak.Tauno-serial-plotter