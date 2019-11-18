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

    def __init__(self, view, worksheet):
        self.view = view
        worksheet.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'deleted_cell':
            self.update_up_down_buttons()
        
        if change_code == 'new_active_cell':
            self.update_up_down_buttons()

        if change_code == 'cell_moved':
            self.update_up_down_buttons()

        if change_code == 'busy_cell_count_changed':
            self.update_stop_button()

    def update_stop_button(self):
        if self.worksheet.get_busy_cell_count() > 0:
            self.activate_stop_button()
        else:
            self.deactivate_stop_button()
            
    def update_up_down_buttons(self):
        if self.worksheet != None:
            active_cell = self.worksheet.get_active_cell()
            if active_cell != None:
                cell_position = active_cell.get_worksheet_position()
                cell_count = self.worksheet.get_cell_count()
                if cell_position == cell_count - 1:
                    self.main_window.headerbar.deactivate_down_button()
                else:
                    self.main_window.headerbar.activate_down_button()
                if cell_position == 0:
                    self.main_window.headerbar.deactivate_up_button()
                else:
                    self.main_window.headerbar.activate_up_button()

    def activate_stop_button(self):
        self.view.stop_button.set_sensitive(True)

    def deactivate_stop_button(self):
        self.view.stop_button.set_sensitive(False)

    def activate_up_button(self):
        self.view.up_button.set_sensitive(True)

    def deactivate_up_button(self):
        self.view.up_button.set_sensitive(False)

    def activate_down_button(self):
        self.view.down_button.set_sensitive(True)

    def deactivate_down_button(self):
        self.view.down_button.set_sensitive(False)


