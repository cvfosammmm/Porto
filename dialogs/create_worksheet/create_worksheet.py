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

from dialogs.dialog import Dialog
import helpers.helpers as helpers
import dialogs.create_worksheet.create_worksheet_viewgtk as create_worksheet_viewgtk
import app.service_locator as service_locator

import os.path


class CreateWorksheetDialog(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window
        self.kernelspecs = service_locator.ServiceLocator.get_kernelspecs()

    def run(self):
        self.current_kernelname = None
        self.current_folder = None
        self.current_filename = None

        self.setup()

        self.update_create_button()
        self.set_current_folder(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS))
        self.view.name_entry.set_text('Untitled' + self.get_untitled_postfix())

        response = self.view.run()
        while response == Gtk.ResponseType.APPLY:
            if not self.check_overwrite():
                response = self.view.run()
            else:
                break
        if response == Gtk.ResponseType.APPLY:
            self.current_name = self.view.name_entry.get_text().strip()
            pathname = self.current_folder + '/' + self.current_filename
            kernelname = self.current_kernelname
            return_value = (pathname, kernelname)
        else:
            return_value = None

        self.view.create_dialog.hide()
        del(self.view)
        return return_value

    def check_overwrite(self):
        if self.current_folder == None or self.current_filename == None: return False
        if os.path.isfile(self.current_folder + '/' + self.current_filename):
            return service_locator.ServiceLocator.get_dialog('overwrite_confirmation').run(self.current_filename, self.current_folder)
        return True

    def setup(self):
        self.view = create_worksheet_viewgtk.CreateWorksheet(self.main_window)
        self.view.name_entry_buffer.connect('inserted-text', self.on_name_entry)
        self.view.name_entry_buffer.connect('deleted-text', self.on_name_entry)
        self.view.name_entry.connect('activate', self.on_entry_activate)
        self.view.folder_entry.connect('clicked', self.on_folder_button_click)

        first_button = None
        for language in self.kernelspecs.get_list_of_names():
            name = self.kernelspecs.get_displayname(language)
            self.view.language_buttons[name] = Gtk.RadioButton()
            if first_button == None: first_button = self.view.language_buttons[name]
            box = Gtk.HBox()
            icon = self.kernelspecs.get_menu_icon(language)
            icon.set_margin_left(0)
            icon.set_margin_right(10)
            box.pack_start(icon, False, False, 0)
            box.pack_start(Gtk.Label(name), False, False, 0)
            box.set_margin_right(2)
            self.view.language_buttons[name].add(box)
            self.view.language_buttons[name].set_mode(False)
            if first_button != None:
                self.view.language_buttons[name].join_group(first_button)
            self.view.language_switcher.pack_start(self.view.language_buttons[name], False, False, 0)
            self.view.language_buttons[name].connect('toggled', self.on_language_button_toggled, language)
        self.view.topbox.show_all()

        first_button.set_active(True)
        first_button.toggled()

    def update_create_button(self):
        if len(self.view.name_entry.get_text()) > 0:
            self.view.create_button.set_sensitive(True)
        else:
            self.view.create_button.set_sensitive(False)

    def get_untitled_postfix(self):
        if not os.path.isfile(self.current_folder + '/Untitled.ipynb'):
            return ''
            
        count = 2
        while os.path.isfile(self.current_folder + '/Untitled' + str(count) + '.ipynb'):
            count += 1
        return str(count)

    def on_name_entry(self, buffer, position, chars, n_chars=None):
        self.update_create_button()
        self.set_current_filename(''.join(self.view.name_entry.get_text().title().split()) + '.ipynb')

    def on_entry_activate(self, entry, user_data=None):
        self.view.create_button.clicked()

    def set_current_folder(self, folder):
        self.current_folder = folder
        display_name = helpers.shorten_folder(self.current_folder, 35)
        self.view.folder_entry_widget_label.set_text(display_name)

    def set_current_filename(self, filename):
        self.current_filename = filename

    def on_folder_button_click(self, button):
        folder = service_locator.ServiceLocator.get_dialog('select_folder').run(self.current_folder)
        if folder != None:
            self.set_current_folder(folder)

    def on_language_button_toggled(self, button, language):
        if button.get_active():
            self.view.css_provider.load_from_data(('dialog { background-image: url(\'' + self.kernelspecs.get_background_path(language) + '\'); }').encode('utf-8'))
            self.current_kernelname = language


