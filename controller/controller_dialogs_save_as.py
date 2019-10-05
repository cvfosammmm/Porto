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

import os.path

import model.model_worksheet as model_worksheet
import viewgtk.viewgtk_dialogs_save_as as viewgtk_dialogs_save_as
import viewgtk.viewgtk_dialogs_overwrite_confirmation as viewgtk_dialogs_overwrite_confirmation
import viewgtk.viewgtk_dialogs_select_folder as viewgtk_dialogs_select_folder
import helpers.helpers as helpers


class ControllerDialogSaveAs(object):

    def __init__(self, notebook, main_window, main_controller):
        self.notebook = notebook
        self.main_window = main_window
        self.main_controller = main_controller

    def show(self, worksheet):
        self.worksheet = worksheet
        self.setup()
        self.update_save_button()
        self.set_current_folder(self.worksheet.get_folder())
        self.save_as_dialog.name_entry.set_text(self.worksheet.get_name())
        self.save_as_dialog.run()

    def setup(self):
        self.save_as_dialog = viewgtk_dialogs_save_as.SaveAs(self.main_window)
        self.save_as_dialog.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.save_as_dialog.save_button.connect('clicked', self.on_save_button_clicked)
        self.save_as_dialog.name_entry_buffer.connect('inserted-text', self.on_name_entry)
        self.save_as_dialog.name_entry_buffer.connect('deleted-text', self.on_name_entry)
        self.save_as_dialog.name_entry.connect('activate', self.on_entry_activate)
        self.save_as_dialog.folder_entry.connect('clicked', self.on_folder_button_click)
        self.save_as_dialog.topbox.show_all()
        self.save_as_dialog.save_as_dialog.connect('close', self.on_close)

    def update_save_button(self):
        if len(self.save_as_dialog.name_entry.get_text()) > 0:
            self.save_as_dialog.save_button.set_sensitive(True)
        else:
            self.save_as_dialog.save_button.set_sensitive(False)

    def on_name_entry(self, buffer, position, chars, n_chars=None):
        self.update_save_button()
        self.set_current_filename(''.join(self.save_as_dialog.name_entry.get_text().title().split()) + '.ipynb')

    def on_cancel_button_clicked(self, cancel_button):
        del(self.save_as_dialog)

    def on_close(self, dialog, user_data=False):
        del(self.save_as_dialog)

    def on_save_button_clicked(self, save_button):
        self.current_name = self.save_as_dialog.name_entry.get_text().strip()
        if len(self.current_name) > 0:
            if os.path.isfile(self.current_folder + '/' + self.current_filename):
                overwrite_confirmation_dialog = viewgtk_dialogs_overwrite_confirmation.OverwriteConfirmation(self.main_window, self.current_filename, self.current_folder)
                response = overwrite_confirmation_dialog.run()
                overwrite_confirmation_dialog.destroy()
                if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.CLOSE, Gtk.ResponseType.DELETE_EVENT]:
                    return
            del(self.save_as_dialog)
            self.save_worksheet()

    def on_entry_activate(self, entry, user_data=None):
        self.save_as_dialog.save_button.clicked()

    def set_current_folder(self, folder):
        self.current_folder = folder
        display_name = helpers.shorten_folder(self.current_folder, 35)
        self.save_as_dialog.folder_entry_widget_label.set_text(display_name)

    def set_current_filename(self, filename):
        self.current_filename = filename

    def on_folder_button_click(self, button):
        self.folder_dialog = viewgtk_dialogs_select_folder.SelectFolder(self.main_window)
        self.folder_dialog.set_current_folder(self.current_folder)

        response = self.folder_dialog.run()
        if response == Gtk.ResponseType.APPLY:
            self.set_current_folder(self.folder_dialog.get_current_folder())
        self.folder_dialog.destroy()

    def save_worksheet(self):
        new_path = self.current_folder + '/' + self.current_filename
        old_path = self.worksheet.get_pathname()

        overwrite = self.notebook.get_worksheet_by_pathname(new_path)
        if overwrite != None and old_path != new_path:
            self.main_controller.notebook_controller.close_worksheet(overwrite)

        self.worksheet.save_as(new_path)


