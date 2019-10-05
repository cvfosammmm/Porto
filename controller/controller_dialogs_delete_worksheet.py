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
from gi.repository import GLib
from gi.repository import Gtk


class ControllerDialogDeleteWorksheet(object):

    def __init__(self, notebook, main_window, main_controller):
        self.notebook = notebook
        self.main_window = main_window
        self.main_controller = main_controller

    def show(self, worksheet):
        self.delete_ws_dialog = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)
        self.delete_ws_dialog.set_property('text', 'Are you sure you want to delete »' + worksheet.get_name() + '«?')
        self.delete_ws_dialog.format_secondary_text('When a worksheet is deleted it\'s permanently gone and can\'t easily be restored.')
        self.delete_ws_dialog.add_button('Cancel', Gtk.ResponseType.NO)
        delete_button = self.delete_ws_dialog.add_button('Delete', Gtk.ResponseType.YES)
        delete_button.get_style_context().add_class(Gtk.STYLE_CLASS_DESTRUCTIVE_ACTION)
        
        response = self.delete_ws_dialog.run()
        if response == Gtk.ResponseType.YES:
            self.delete_ws_dialog.destroy()
            return True
        elif response == Gtk.ResponseType.NO:
            self.delete_ws_dialog.destroy()
            return False


