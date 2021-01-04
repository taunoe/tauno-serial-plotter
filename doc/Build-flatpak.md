# Building Flatpak

**I managed to get flatpak work, but it does not show any GUI icons!** 

Install a runtime and the matching SDK

    $ flatpak install flathub org.kde.Platform org.kde.Sdk

Add a manifest file: org.flatpak.Tauno-serial-plotter.yml


## Build & Test

    $ flatpak-builder --user --install build-dir org.flatpak.Tauno-serial-plotter.yml --force-clean

    $ flatpak run org.flatpak.Tauno-serial-plotter

## Put the app in a local repository

    $ flatpak-builder --repo=repo --force-clean build-dir org.flatpak.Tauno-serial-plotter.yml

## Install

## Links

- [Building your first Flatpak](https://docs.flatpak.org/en/latest/first-build.html)