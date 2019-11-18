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

import model.model_cell as model_cell
import viewgtk.viewgtk_cell as viewgtk_cell
import controller.controller_cell as cellcontroller


class WorksheetController(object):

    def __init__(self, worksheet, worksheet_view, main_controller):

        self.worksheet = worksheet
        self.worksheet_view = worksheet_view

        self.main_controller = main_controller
        self.cell_controllers = dict()

        # build it from current cells
        for cell in worksheet.cells:
            self.add_cell_view(cell)

        # observe worksheet
        worksheet.register_observer(self)
        worksheet.register_observer(self.main_controller.backend_controller_code)

        self.worksheet_view.viewport.connect('scroll-event', self.on_scroll)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'pathname_changed':
            worksheet = notifying_object
            old_path = parameter
            new_path = self.worksheet.get_pathname()
            row = self.main_controller.notebook.recently_opened_worksheets

            for path in [old_path, new_path]:
                row.remove_worksheet_by_pathname(path)
                item = {'pathname': path, 'kernelname': worksheet.kernelname, 'date': worksheet.get_last_saved()}
                row.add_item(item)
            self.main_controller.update_title(self.worksheet)
            
        if change_code == 'kernel_state_changed':
            self.main_controller.update_subtitle(self.worksheet)
            
        if change_code == 'new_cell':
            cell = parameter
            self.add_cell_view(cell)

        if change_code == 'deleted_cell':
            cell = parameter

            self.worksheet_view.remove_child_by_position(cell.get_worksheet_position())
        
        if change_code == 'new_active_cell':
            cell = parameter

            child_position = cell.get_worksheet_position()
            cell_view = self.worksheet_view.get_child_by_position(child_position)
            cell_view.set_active()
            cell_view.grab_focus()
            
        if change_code == 'new_inactive_cell':
            cell = parameter
            child_position = cell.get_worksheet_position()
            cell_view = self.worksheet_view.get_child_by_position(child_position)
            cell_view.set_inactive()
            
            # unselect text
            insert_mark = cell.get_iter_at_mark(cell.get_insert())
            selection_bound = cell.get_selection_bound()
            cell.move_mark(selection_bound, insert_mark)

        if change_code == 'cell_moved':
            cell_view1_position = parameter['position']
            cell_view2_position = parameter['new_position']
            
            # move cells
            cell_view1 = self.worksheet_view.get_child_by_position(cell_view1_position)
            cell_view2 = self.worksheet_view.get_child_by_position(cell_view2_position)
            self.worksheet_view.move_child(cell_view1, cell_view2_position)
            self.worksheet_view.move_child(cell_view2, cell_view1_position)
            
            cell_view1.grab_focus()
            GLib.idle_add(lambda: cell_view1.get_source_view().grab_focus())

        if change_code == 'busy_cell_count_changed':
            self.main_controller.update_subtitle(self.worksheet)

        if change_code == 'save_state_change':
            save_state = parameter
            self.main_controller.update_title(self.worksheet)
            self.main_controller.wslists_controller.update_save_date(self.worksheet)
            if self.worksheet == self.main_controller.notebook.active_worksheet:
                self.main_controller.update_save_button()
            if save_state == 'saved':
                path = self.worksheet.get_pathname()
                row = self.main_controller.notebook.recently_opened_worksheets
                row.remove_worksheet_by_pathname(path)
                item = {'pathname': path, 'kernelname': self.worksheet.kernelname, 'date': self.worksheet.get_last_saved()}
                row.add_item(item)


    def add_cell_view(self, cell):
        worksheet_position = cell.get_worksheet_position()
        if isinstance(cell, model_cell.MarkdownCell):
            cell_view = viewgtk_cell.CellViewMarkdown(cell)
            self.cell_controllers[cell] = cellcontroller.MarkdownCellController(cell, cell_view, None, self, self.main_controller)
        elif isinstance(cell, model_cell.CodeCell):
            cell_view = viewgtk_cell.CellViewCode(cell)
            self.cell_controllers[cell] = cellcontroller.CodeCellController(cell, cell_view, self, self.main_controller)

        self.worksheet_view.add_child_at_position(cell_view, worksheet_position)
        self.worksheet_view.show_all()

    '''
    *** signal handlers: worksheets
    '''
    
    def on_scroll(self, scrolled_window, event):
        if(abs(event.delta_y) > 0):
            adjustment = self.worksheet_view.get_vadjustment()

            page_size = adjustment.get_page_size()
            scroll_unit = pow (page_size, 2.0 / 3.0)

            adjustment.set_value(adjustment.get_value() + event.delta_y*scroll_unit)

        return True
        

    def destruct(self):
        self.worksheet.remove_observer(self)
        self.worksheet.remove_observer(self.main_controller.backend_controller_code)

        #self.worksheet_view.viewport.disconnect('scroll-event')
        
        '''for cell in self.cell_controllers:
            self.cell_controllers[cell].destruct()
            del(self.cell_controllers[cell])'''


