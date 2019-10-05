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
from gi.repository import GLib, Gtk

import os.path

import viewgtk.viewgtk_dialogs_create_worksheet as viewgtk_dialogs_create_worksheet
import viewgtk.viewgtk_dialogs_overwrite_confirmation as viewgtk_dialogs_overwrite_confirmation
import viewgtk.viewgtk_dialogs_select_folder as viewgtk_dialogs_select_folder
import helpers.helpers as helpers


class ControllerDialogCreateWorksheet(object):

    def __init__(self, notebook, main_window, main_controller):
        self.notebook = notebook
        self.main_window = main_window
        self.main_controller = main_controller
        self.current_kernelname = None

    def show(self):
        self.setup()
        self.update_create_button()
        self.set_current_folder(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS))
        self.create_dialog.name_entry.set_text('Untitled' + self.get_untitled_postfix())
        self.create_dialog.run()

    def get_untitled_postfix(self):
        if not os.path.isfile(self.current_folder + '/Untitled.ipynb'):
            return ''
            
        count = 2
        while os.path.isfile(self.current_folder + '/Untitled' + str(count) + '.ipynb'):
            count += 1
        return str(count)

    def setup(self):
        self.create_dialog = viewgtk_dialogs_create_worksheet.CreateWorksheet(self.main_window)
        self.create_dialog.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.create_dialog.create_button.connect('clicked', self.on_create_button_clicked)
        self.create_dialog.name_entry_buffer.connect('inserted-text', self.on_name_entry)
        self.create_dialog.name_entry_buffer.connect('deleted-text', self.on_name_entry)
        self.create_dialog.name_entry.connect('activate', self.on_entry_activate)
        self.create_dialog.folder_entry.connect('clicked', self.on_folder_button_click)

        first_button = None
        for language in self.main_controller.kernelspecs.get_list_of_names():
            name = self.main_controller.kernelspecs.get_displayname(language)
            self.create_dialog.language_buttons[name] = Gtk.RadioButton()
            if first_button == None: first_button = self.create_dialog.language_buttons[name]
            box = Gtk.HBox()
            icon = self.main_controller.kernelspecs.get_menu_icon(language)
            icon.set_margin_left(0)
            icon.set_margin_right(10)
            box.pack_start(icon, False, False, 0)
            box.pack_start(Gtk.Label(name), False, False, 0)
            box.set_margin_right(2)
            self.create_dialog.language_buttons[name].add(box)
            self.create_dialog.language_buttons[name].set_mode(False)
            if first_button != None:
                self.create_dialog.language_buttons[name].join_group(first_button)
            self.create_dialog.language_switcher.pack_start(self.create_dialog.language_buttons[name], False, False, 0)
            self.create_dialog.language_buttons[name].connect('toggled', self.on_language_button_toggled, language)
        self.create_dialog.topbox.show_all()

        first_button.set_active(True)
        first_button.toggled()
        self.create_dialog.create_dialog.connect('close', self.on_close)

    def update_create_button(self):
        if len(self.create_dialog.name_entry.get_text()) > 0:
            self.create_dialog.create_button.set_sensitive(True)
        else:
            self.create_dialog.create_button.set_sensitive(False)

    def on_name_entry(self, buffer, position, chars, n_chars=None):
        self.update_create_button()
        self.set_current_filename(''.join(self.create_dialog.name_entry.get_text().title().split()) + '.ipynb')

    def on_cancel_button_clicked(self, cancel_button):
        del(self.create_dialog)

    def on_close(self, dialog, user_data=False):
        del(self.create_dialog)

    def on_create_button_clicked(self, create_button):
        self.current_name = self.create_dialog.name_entry.get_text().strip()
        if len(self.current_name) > 0:
            if os.path.isfile(self.current_folder + '/' + self.current_filename):
                overwrite_confirmation_dialog = viewgtk_dialogs_overwrite_confirmation.OverwriteConfirmation(self.main_window, self.current_filename, self.current_folder)
                response = overwrite_confirmation_dialog.run()
                overwrite_confirmation_dialog.destroy()
                if response in [Gtk.ResponseType.CANCEL, Gtk.ResponseType.CLOSE, Gtk.ResponseType.DELETE_EVENT]:
                    return
            del(self.create_dialog)
            self.create_worksheet()

    def on_entry_activate(self, entry, user_data=None):
        self.create_dialog.create_button.clicked()

    def set_current_folder(self, folder):
        self.current_folder = folder
        display_name = helpers.shorten_folder(self.current_folder, 35)
        self.create_dialog.folder_entry_widget_label.set_text(display_name)

    def set_current_filename(self, filename):
        self.current_filename = filename

    def on_folder_button_click(self, button):
        self.folder_dialog = viewgtk_dialogs_select_folder.SelectFolder(self.main_window)
        self.folder_dialog.set_current_folder(self.current_folder)

        response = self.folder_dialog.run()
        if response == Gtk.ResponseType.APPLY:
            icon = self.main_controller.kernelspecs.get_menu_icon(language)
            self.set_current_folder(self.folder_dialog.get_current_folder())
        self.folder_dialog.destroy()

    def on_language_button_toggled(self, button, language):
        if button.get_active():
            self.create_dialog.css_provider.load_from_data(('dialog { background-image: url(\'' + self.main_controller.kernelspecs.get_background_path(language) + '\'); }').encode('utf-8'))
            self.current_kernelname = language

    def create_worksheet(self):
        pathname = self.current_folder + '/' + self.current_filename
        self.main_controller.notebook_controller.create_worksheet(pathname, self.current_kernelname)


