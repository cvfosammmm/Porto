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

import cell.cell as model_cell
import cell.cell_controller as cellcontroller


class NotebookController(object):

    def __init__(self, notebook, notebook_view):
        self.notebook = notebook
        self.notebook_view = notebook_view

        # to watch for cursor movements
        self.cursor_position = {'cell': None, 'cell_position': None, 'cell_size': None, 'position': None}

        self.notebook_view.viewport.connect('scroll-event', self.on_scroll)

    def change_notification(self, change_code, notifying_object, parameter):
        pass

    '''
    *** signal handlers: notebooks
    '''
    
    def on_scroll(self, scrolled_window, event):
        if(abs(event.delta_y) > 0):
            adjustment = self.notebook_view.get_vadjustment()

            page_size = adjustment.get_page_size()
            scroll_unit = pow (page_size, 2.0 / 3.0)

            adjustment.set_value(adjustment.get_value() + event.delta_y*scroll_unit)
        return True

    def scroll_to_cursor(self, cell, check_if_position_changed=True):
        notebook = self.notebook
        if notebook == None: return
        if not notebook.active_cell == cell: return
        current_cell = cell
        current_cell_position = cell.get_notebook_position()
        current_position = cell.get_property('cursor-position')
        notebook_view = notebook.view
        cell_view_position = cell.get_notebook_position()
        cell_view = notebook_view.get_child_by_position(cell_view_position)
        result_view = cell_view.result_view_revealer
        current_cell_size = cell_view.get_allocation().height
        current_cell_size = cell_view.get_allocation().height + result_view.get_allocation().height

        # check if cursor has changed
        position_changed = False
        if notebook.cursor_position['cell'] != current_cell: position_changed = True
        if notebook.cursor_position['cell_position'] != current_cell_position: position_changed = True
        if notebook.cursor_position['cell_size'] != current_cell_size and (self.cursor_position['position'] != 0 or cell.get_char_count() == 0): 
            position_changed = True
        if notebook.cursor_position['position'] != current_position: position_changed = True
        if check_if_position_changed == False:
            position_changed = True
            if cell_view.has_changed_size():
                cell_view.update_size()
        
        first_run = True
        if position_changed:
            if notebook.cursor_position['cell'] != None: first_run = False
            notebook.cursor_position['cell'] = current_cell
            notebook.cursor_position['cell_position'] = current_cell_position
            notebook.cursor_position['cell_size'] = current_cell_size
            notebook.cursor_position['position'] = current_position
            
        if first_run == False and position_changed:
            
            # scroll to markdown cell with result
            if isinstance(current_cell, model_cell.MarkdownCell) and current_cell.get_result() != None:

                # get line number, calculate offset
                scroll_position = notebook_view.get_vadjustment()
                x, cell_position = cell_view.translate_coordinates(notebook_view.box, 0, 0)
                line_position = cell_view.text_entry.get_iter_location(cell.get_iter_at_mark(cell.get_insert())).y
                last_line_position = cell_view.text_entry.get_iter_location(cell.get_end_iter()).y
                
                if cell_position >= 0:
                    new_position = cell_position
                else:
                    new_position = 0
                
                window_height = notebook_view.get_allocated_height()
                if current_cell_size < window_height:
                    if new_position >= scroll_position.get_value():
                        if new_position + current_cell_size >= scroll_position.get_value() + window_height:
                            new_position += current_cell_size - window_height
                            scroll_position.set_value(new_position)
                    else:
                        scroll_position.set_value(new_position)
                else:    
                    scroll_position.set_value(new_position)

            # scroll to codecell or md cell without result
            if not isinstance(current_cell, model_cell.MarkdownCell) or current_cell.get_result() == None:

                # get line number, calculate offset
                scroll_position = notebook_view.get_vadjustment()
                x, cell_position = cell_view.translate_coordinates(notebook_view.box, 0, 0)
                it = cell.get_iter_at_mark(cell.get_insert())
                line_position = cell_view.text_entry.get_iter_location(it).y
                last_line_position = cell_view.text_entry.get_iter_location(cell.get_end_iter()).y
                
                if cell_position >= 0:
                    offset = -scroll_position.get_value() + cell_position + line_position + 15
                else:
                    offset = 0

                if line_position == 0 and scroll_position.get_value() >= cell_position:
                    offset -= 15
                elif line_position >= last_line_position and scroll_position.get_value() <= (cell_position + 15 + line_position + 0):
                    offset += 15
                    
                # calculate movement
                window_height = notebook_view.get_allocated_height()
                if offset > window_height - cell_view.line_height:
                    movement = offset - window_height + cell_view.line_height
                elif offset < 0:
                    movement = offset
                else:
                    movement = 0
                if movement > 0 and line_position == 0:
                    if current_cell_size < round(window_height / 3.5):
                        movement += current_cell_size
                        if current_cell.get_line_count() == 1:
                            movement -= 50
                        else:
                            movement -= 35
                    else:
                        movement += min(60, current_cell_size - 35)
                    if isinstance(current_cell, model_cell.MarkdownCell):
                        movement -= 1

                if movement < 0 and line_position >= last_line_position:
                    if current_cell_size < round(window_height / 3.5):
                        movement -= current_cell_size
                        if current_cell.get_line_count() == 1:
                            movement += 50
                        else:
                            movement += 35
                    else:
                        movement -= min(60, current_cell_size - 35)
                    if isinstance(current_cell, model_cell.MarkdownCell):
                        movement -= 1
                        
                scroll_position.set_value(scroll_position.get_value() + movement)


