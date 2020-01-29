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


class CloseConfirmationDialog(Dialog):
    ''' This dialog is asking users to save unsaved notebooks or discard their changes. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, notebooks):
        self.setup(notebooks)

        response = self.view.run()
        if response == Gtk.ResponseType.NO:
            all_save_to_close = True
        elif response == Gtk.ResponseType.YES:
            selected_notebooks = list()
            if len(notebooks) == 1:
                selected_notebooks.append(notebooks[0])
            else:
                for child in self.chooser.get_children():
                    if child.get_child().get_active():
                        number = int(child.get_child().get_name()[30:])
                        selected_notebooks.append(notebooks[number])
            for notebook in selected_notebooks:
                notebook.save_to_disk()
            all_save_to_close = True
        else:
            all_save_to_close = False

        self.close()
        return {'all_save_to_close': all_save_to_close}

    def setup(self, notebooks):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)

        if len(notebooks) == 1:
            self.view.set_property('text', 'Notebook »' + notebooks[0].get_name() + '« has unsaved changes.')
            self.view.format_secondary_markup('If you close Porto without saving, these changes will be lost.')

        if len(notebooks) >= 2:
            self.view.set_property('text', 'There are ' + str(len(notebooks)) + ' notebooks with unsaved changes.\nSave changes before closing Porto?')
            self.view.format_secondary_markup('Select the notebooks you want to save:')
            label = self.view.get_message_area().get_children()[1]
            label.set_xalign(0)
            label.set_halign(Gtk.Align.START)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
            scrolled_window.set_size_request(446, 112)
            self.chooser = Gtk.ListBox()
            self.chooser.set_selection_mode(Gtk.SelectionMode.NONE)

            counter = 0
            for notebook in notebooks:
                button = Gtk.CheckButton(notebook.get_name())
                button.set_name('notebook_to_save_checkbutton_' + str(counter))
                button.set_active(True)
                button.set_can_focus(False)
                self.chooser.add(button)
                counter += 1
            for listboxrow in self.chooser.get_children():
                listboxrow.set_can_focus(False)
            scrolled_window.add(self.chooser)
            
            secondary_text_label = Gtk.Label('If you close Porto without saving, all changes will be lost.')
            message_area = self.view.get_message_area()
            message_area.pack_start(scrolled_window, False, False, 0)
            message_area.pack_start(secondary_text_label, False, False, 0)
            message_area.show_all()

        self.view.add_buttons('Close _without Saving', Gtk.ResponseType.NO, '_Cancel', Gtk.ResponseType.CANCEL, '_Save', Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)


