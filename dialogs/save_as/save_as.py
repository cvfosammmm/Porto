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

import dialogs.save_as.save_as_viewgtk as save_as_viewgtk
from dialogs.dialog import Dialog
import helpers.helpers as helpers

import os.path


class SaveAsDialog(Dialog):

    def __init__(self, workspace, main_window, overwrite_confirmation_dialog, select_folder_dialog):
        self.workspace = workspace
        self.main_window = main_window
        self.overwrite_confirmation_dialog = overwrite_confirmation_dialog
        self.select_folder_dialog = select_folder_dialog

    def run(self, worksheet):
        self.current_name = None
        self.current_folder = None
        self.current_filename = None

        self.worksheet = worksheet
        self.setup()
        self.update_save_button()
        self.set_current_folder(self.worksheet.get_folder())
        self.view.name_entry.set_text(self.worksheet.get_name())

        response = self.view.run()
        while response == Gtk.ResponseType.APPLY:
            if not self.check_overwrite():
                response = self.view.run()
            else:
                break
        if response == Gtk.ResponseType.APPLY:
            self.current_name = self.view.name_entry.get_text().strip()
            if len(self.current_name) > 0:
                new_path = self.current_folder + '/' + self.current_filename
                old_path = self.worksheet.get_pathname()

                overwrite = self.workspace.get_worksheet_by_pathname(new_path)
                if overwrite != None and old_path != new_path:
                    self.workspace.controller.close_worksheet(overwrite)

                self.worksheet.save_as(new_path)
                return_value = True
        else:
            return_value = False
        self.view.save_as_dialog.hide()
        del(self.view)
        return return_value

    def check_overwrite(self):
        if self.current_folder == None or self.current_filename == None: return False
        if os.path.isfile(self.current_folder + '/' + self.current_filename):
            return self.overwrite_confirmation_dialog.run(self.current_filename, self.current_folder)
        return True

    def setup(self):
        self.view = save_as_viewgtk.SaveAs(self.main_window)
        self.view.name_entry_buffer.connect('inserted-text', self.on_name_entry)
        self.view.name_entry_buffer.connect('deleted-text', self.on_name_entry)
        self.view.name_entry.connect('activate', self.on_entry_activate)
        self.view.folder_entry.connect('clicked', self.on_folder_button_click)
        self.view.topbox.show_all()

    def update_save_button(self):
        if len(self.view.name_entry.get_text()) > 0:
            self.view.save_button.set_sensitive(True)
        else:
            self.view.save_button.set_sensitive(False)

    def on_name_entry(self, buffer, position, chars, n_chars=None):
        self.update_save_button()
        self.set_current_filename(''.join(self.view.name_entry.get_text().title().split()) + '.ipynb')

    def on_entry_activate(self, entry, user_data=None):
        self.view.save_button.clicked()

    def set_current_folder(self, folder):
        self.current_folder = folder
        display_name = helpers.shorten_folder(self.current_folder, 35)
        self.view.folder_entry_widget_label.set_text(display_name)

    def set_current_filename(self, filename):
        self.current_filename = filename

    def on_folder_button_click(self, button):
        folder = self.select_folder_dialog.run(self.current_folder)
        if folder != None:
            self.set_current_folder(folder)


