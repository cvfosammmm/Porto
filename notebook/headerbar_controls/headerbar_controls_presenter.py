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


class HeaderbarControlsPresenter(object):

    def __init__(self, notebook, button_box, save_button, title):
        self.notebook = notebook
        self.button_box = button_box
        self.save_button = save_button
        self.title = title
        self.update_title()
        self.update_subtitle()
        self.update_save_button()
        self.update_up_down_buttons()
        self.update_stop_button()
        self.notebook.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'deleted_cell':
            self.update_up_down_buttons()
        
        if change_code == 'new_active_cell':
            self.update_up_down_buttons()

        if change_code == 'cell_moved':
            self.update_up_down_buttons()

        if change_code == 'kernel_state_changed':
            self.update_subtitle()

        if change_code == 'busy_cell_count_changed':
            self.update_stop_button()
            self.update_subtitle()

        if change_code == 'save_state_change':
            self.update_save_button()
            self.update_title()

        if change_code == 'pathname_changed':
            self.update_title()
            
    def update_title(self):
        save_state = '*' if self.notebook.get_save_state() == 'modified' else ''
        self.title.title_label.set_text(save_state + self.notebook.get_name())

    def update_subtitle(self):
        busy_cell_count = self.notebook.get_busy_cell_count()
        if busy_cell_count > 0:
            plural = 's' if busy_cell_count > 1 else ''
            subtitle = 'evaluating ' + str(busy_cell_count) + ' cell' + plural + '.'
        elif self.notebook.get_kernel_state() == 'starting':
            subtitle = 'starting kernel.'
        else:
            subtitle = 'idle.'
        self.title.subtitle_label.set_text(subtitle)
            
    def update_stop_button(self):
        if self.notebook.get_busy_cell_count() > 0:
            self.activate_stop_button()
        else:
            self.deactivate_stop_button()
            
    def update_up_down_buttons(self):
        if self.notebook != None:
            active_cell = self.notebook.get_active_cell()
            if active_cell != None:
                cell_position = active_cell.get_notebook_position()
                cell_count = self.notebook.get_cell_count()
                if cell_position == cell_count - 1:
                    self.deactivate_down_button()
                else:
                    self.activate_down_button()
                if cell_position == 0:
                    self.deactivate_up_button()
                else:
                    self.activate_up_button()

    def update_save_button(self):
        if self.notebook.get_save_state() == 'modified':
            self.activate_save_button()
        else:
            self.deactivate_save_button()

    def activate_stop_button(self):
        self.button_box.stop_button.set_sensitive(True)

    def deactivate_stop_button(self):
        self.button_box.stop_button.set_sensitive(False)

    def activate_up_button(self):
        self.button_box.up_button.set_sensitive(True)

    def deactivate_up_button(self):
        self.button_box.up_button.set_sensitive(False)

    def activate_down_button(self):
        self.button_box.down_button.set_sensitive(True)

    def deactivate_down_button(self):
        self.button_box.down_button.set_sensitive(False)

    def activate_save_button(self):
        self.save_button.set_sensitive(True)

    def deactivate_save_button(self):
        self.save_button.set_sensitive(False)


