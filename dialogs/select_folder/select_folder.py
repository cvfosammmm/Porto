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

import os.path


class SelectFolderDialog(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, current_folder):
        self.setup()
        self.view.set_current_folder(current_folder)
        response = self.view.run()
        return_value = None
        if response == Gtk.ResponseType.APPLY:
            return_value = self.view.get_current_folder()
        self.view.hide()
        del(self.view)
        return return_value

    def setup(self):
        action = Gtk.FileChooserAction.SELECT_FOLDER
        buttons = ('_Cancel', Gtk.ResponseType.CANCEL, '_Select', Gtk.ResponseType.APPLY)
        self.view = Gtk.FileChooserDialog('Select Folder', self.main_window, action, buttons)

        self.view.set_do_overwrite_confirmation(True)

        for widget in self.view.get_header_bar().get_children():
            if isinstance(widget, Gtk.Button) and widget.get_label() == '_Select':
                widget.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
                widget.set_can_default(True)
                widget.grab_default()
        

