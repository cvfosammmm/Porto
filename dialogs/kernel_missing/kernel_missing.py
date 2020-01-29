#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from dialogs.dialog import Dialog


class KernelMissingDialog(Dialog):
    ''' This dialog is asking users to save unsaved worksheets or discard their changes. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, kernelname):
        self.setup(kernelname)

        response = self.view.run()
        self.close()

    def setup(self, kernelname):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.ERROR)

        self.view.set_property('text', 'Kernel »' + kernelname + '« is missing.')
        self.view.format_secondary_markup('The worksheet you want to open uses the »' + kernelname + '« kernel, which does not seem to be installed on this system.')
        self.view.add_buttons('_Close', Gtk.ResponseType.OK)


