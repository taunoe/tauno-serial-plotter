## Build with fbs

    pip3 install fbs

    fbs startproject

But sourcecode in ./src/main/python/main.py file. (And also 'img' folder https://github.com/taunoe/tauno-serial-plotter/issues/5)

    fbs run

Turn it into a standalone executable:

    fbs freeze

This places a self-contained binary in the target/MyApp/ folder of your current directory.

### Create installer:

On Ubuntu first install fbm: https://fpm.readthedocs.io/en/latest/installing.html

    sudo apt install ruby ruby-dev rubygems build-essential

    gem install --no-document fpm

Now create installer (deb filne on Ubuntu):

    fbs installer

If you are on Windows, you first need to install NSIS and place it on your PATH.
https://github.com/mherrmann/fbs-tutorial