# Porto

Run and edit Jupyter notebooks on the desktop, written in Python with Gtk.

Website: <a href="https://www.cvfosammmm.org/porto/">https://www.cvfosammmm.org/porto/</a>

<a href="https://flathub.org/apps/details/org.cvfosammmm.Porto"><img src="https://www.cvfosammmm.org/porto/images/flathub-badge-en.svg" width="150" height="50"></a>

![Screenshot](https://github.com/cvfosammmm/Porto/raw/master/resources/images/screenshots/2017-12-25.png)

Porto runs Jupyter notebooks on the desktop and is written in Python and Gtk. Report any issues you encounter here on Github. I'm really happy about any feedback I get, be it about code architecture, design, bugs, feature suggestion, ...

## Installation on Debian (Ubuntu?)

I'm developing Porto on Debian and that's what I exclusively tested it with. Installing on Ubuntu should probably work exactly the same.

[ansifilter](https://gitlab.com/saalen/ansifilter) is an optional dependency that allows colored error messages.

1. Run the following command to install prerequisite Debian packages:
apt-get install sagemath python3-bleach python3-markdown python3-pypandoc jupyter-client python3-ipykernel python3-nbformat libgtk-3-dev libgtksourceview-3.0-dev

2. Download und Unpack Porto from GitHub

3. cd to Porto folder

4. Running the following command should start Porto:
python3 __main__.py

## Installation on other Linux Distributions

Installation on distributions different from Debian or Ubuntu should work more or less the same. If you have any trouble please get in touch by opening an issue on GitHub.

## Getting in touch

Porto development / discussion takes place on GitHub at [https://github.com/cvfosammmm/porto](https://github.com/cvfosammmm/porto "project url").

## License

Porto is licensed under GPL version 3 or later. See the COPYING file for details.
