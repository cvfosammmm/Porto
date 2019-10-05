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


class CloseConfirmation(Gtk.MessageDialog):
    ''' This dialog is asking users to save unsaved worksheets or discard their changes. '''

    def __init__(self, main_window, worksheets):
        Gtk.MessageDialog.__init__(self, main_window, 0, Gtk.MessageType.QUESTION)
        
        if len(worksheets) == 1:
            self.set_property('text', 'Worksheet »' + worksheets[0].get_name() + '« has unsaved changes.')
            self.format_secondary_markup('If you close Porto without saving, these changes will be lost.')

        if len(worksheets) >= 2:
            self.set_property('text', 'There are ' + str(len(worksheets)) + ' worksheets with unsaved changes.\nSave changes before closing Porto?')
            self.format_secondary_markup('Select the worksheets you want to save:')
            label = self.get_message_area().get_children()[1]
            label.set_xalign(0)
            label.set_halign(Gtk.Align.START)
            
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
            scrolled_window.set_size_request(446, 112)
            self.chooser = Gtk.ListBox()
            self.chooser.set_selection_mode(Gtk.SelectionMode.NONE)
            self.worksheets = list()
            for worksheet in worksheets:
                button = Gtk.CheckButton(worksheet.get_name())
                self.worksheets.append(worksheet)
                button.set_name('worksheet_to_save_checkbutton_' + str(len(self.worksheets) - 1))
                button.set_active(True)
                button.set_can_focus(False)
                self.chooser.add(button)
            for listboxrow in self.chooser.get_children():
                listboxrow.set_can_focus(False)
            scrolled_window.add(self.chooser)
                
            secondary_text_label = Gtk.Label('If you close Porto without saving, all changes will be lost.')
            self.message_area = self.get_message_area()
            self.message_area.pack_start(scrolled_window, False, False, 0)
            self.message_area.pack_start(secondary_text_label, False, False, 0)
            self.message_area.show_all()

        self.add_buttons('Close _without Saving', Gtk.ResponseType.NO, '_Cancel', Gtk.ResponseType.CANCEL, '_Save', Gtk.ResponseType.YES)
        self.set_default_response(Gtk.ResponseType.YES)


