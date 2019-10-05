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
from gi.repository import Gdk
from gi.repository import Gtk

import model.model_cell as model_cell
import viewgtk.viewgtk_result as viewgtk_result


class CellController(object):

    def __init__(self, cell, cell_view, worksheet_controller, main_controller):

        self.cell = cell
        self.cell_view = cell_view

        self.worksheet_controller = worksheet_controller
        self.main_controller = main_controller

        # observe cell
        result = cell.get_result()
        if result != None:
            self.add_result_view(result)
        self.cell.register_observer(self)

        self.cell.connect('mark-set', self.on_cursor_movement)
        self.cell.connect('paste-done', self.on_paste)

        # observe cell view
        self.cell_view.connect('focus-in-event', self.on_focus_in)
        self.cell_view.text_entry.connect('focus-in-event', self.on_source_view_focus_in)
        self.cell_view.get_source_view().connect('size-allocate', self.on_size_allocate)
        self.cell_view.text_widget_sw.connect('scroll-event', self.on_scroll)
        
        self.cell_view.text_entry.connect('key-press-event', self.observe_keyboard_keypress_events)

        self.cell_view.result_view_revealer.connect('button-press-event', self.revealer_on_mouse_click)
        self.cell_view.result_view_revealer.connect('size-allocate', self.revealer_on_size_allocate)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_result':
            self.add_result_view(parameter['result'], show_animation=parameter['show_animation'])

        if change_code == 'cell_state_change':
            try: worksheet_view = self.main_controller.main_window.worksheet_views[self.cell.get_worksheet()]
            except KeyError: return
            child_position = self.cell.get_worksheet_position()
            cell_view = worksheet_view.get_child_by_position(child_position)

            if cell_view != None:
                if parameter == 'idle': cell_view.state_display.show_nothing()
                elif parameter == 'edit': cell_view.state_display.show_nothing()
                elif parameter == 'display': cell_view.state_display.show_nothing()
                elif parameter == 'queued_for_evaluation': cell_view.state_display.show_spinner()
                elif parameter == 'ready_for_evaluation': cell_view.state_display.show_spinner()
                elif parameter == 'evaluation_in_progress': cell_view.state_display.show_spinner()

    '''
    *** signal handlers: cells
    '''
    
    def on_scroll(self, scrolled_window, event):

        if(abs(event.delta_y) > 0):
            adjustment = self.worksheet_controller.worksheet_view.get_vadjustment()

            page_size = adjustment.get_page_size()
            scroll_unit = pow (page_size, 2.0 / 3.0)

            adjustment.set_value(adjustment.get_value() + event.delta_y*scroll_unit)

        return True

    def revealer_on_mouse_click(self, result_view_revealer, click_event):
        if click_event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            cell_view = result_view_revealer.cell_view
            cell = cell_view.get_cell()
            worksheet = cell.get_worksheet()
            cell.remove_result()
            worksheet.set_active_cell(cell)
        elif click_event.type == Gdk.EventType.BUTTON_PRESS:
            cell_view = result_view_revealer.cell_view
            cell = cell_view.get_cell()
            worksheet = cell.get_worksheet()
            worksheet.set_active_cell(cell)
        return False

    def revealer_on_size_allocate(self, result_view_revealer, allocation):
        cell = self.main_controller.notebook.active_worksheet.get_active_cell()
        if cell != None and result_view_revealer.autoscroll_on_reveal == True:
            worksheet_view = self.main_controller.main_window.active_worksheet_view
            cell_view_position = cell.get_worksheet_position()
            cell_view = worksheet_view.get_child_by_position(cell_view_position)
            x, cell_position = cell_view.translate_coordinates(worksheet_view.box, 0, 0)
            x, result_position = result_view_revealer.translate_coordinates(worksheet_view.box, 0, 0)
            
            last_allocation = result_view_revealer.allocation
            result_view_revealer.allocation = allocation
            if cell_position > result_position:
                worksheet_view.scroll(allocation.height - last_allocation.height)

    def observe_keyboard_keypress_events(self, widget, event):

        # switch cells with arrow keys: upward
        if event.keyval == Gdk.keyval_from_name('Up') and event.state == 0:
            worksheet = self.cell.get_worksheet()
            cell = self.cell
            if isinstance(cell, model_cell.MarkdownCell) and cell.get_result() != None:
                prev_cell = worksheet.get_prev_cell(cell)
                if not prev_cell == None:
                    worksheet.set_active_cell(prev_cell)
                    self.worksheet_controller.cell_controllers[prev_cell].place_cursor_on_last_line()
                    return True

            if cell.get_worksheet_position() > 0:
                if cell.get_iter_at_mark(cell.get_insert()).get_offset() == 0:
                    prev_cell = worksheet.get_prev_cell(cell)
                    if not prev_cell == None:
                        worksheet.set_active_cell(prev_cell)
                        self.worksheet_controller.cell_controllers[prev_cell].place_cursor_on_last_line()
                        return True
        
        # switch cells with arrow keys: downward
        if event.keyval == Gdk.keyval_from_name('Down') and event.state == 0:
            worksheet = self.cell.get_worksheet()
            cell = self.cell
            
            if isinstance(cell, model_cell.MarkdownCell) and cell.get_result() != None:
                next_cell = worksheet.get_next_cell(cell)
                if not next_cell == None:
                    worksheet.set_active_cell(next_cell)
                    next_cell.place_cursor(next_cell.get_start_iter())
                    return True
                
            if cell.get_worksheet_position() < worksheet.get_cell_count() - 1:
                if cell.get_char_count() == (cell.get_iter_at_mark(cell.get_insert()).get_offset()):
                    next_cell = worksheet.get_next_cell(cell)
                    if not next_cell == None:
                        worksheet.set_active_cell(next_cell)
                        next_cell.place_cursor(next_cell.get_start_iter())
                        return True

        if event.keyval == Gdk.keyval_from_name('BackSpace') and event.state == 0:
            worksheet = self.cell.get_worksheet()
            cell = self.cell

            if isinstance(cell, model_cell.CodeCell) and cell.get_char_count() == 0:
                prev_cell = worksheet.get_prev_cell(cell)
                if not prev_cell == None:
                    worksheet.set_active_cell(prev_cell)
                    self.worksheet_controller.cell_controllers[prev_cell].place_cursor_on_last_line()
                    cell.remove_result()
                    worksheet.remove_cell(cell)
                    return True

            if isinstance(cell, model_cell.MarkdownCell):
                if cell.get_result() != None or cell.get_char_count() == 0:
                    prev_cell = worksheet.get_prev_cell(cell)
                    next_cell = worksheet.get_next_cell(cell)
                    if not prev_cell == None: 
                        worksheet.set_active_cell(prev_cell)
                        self.worksheet_controller.cell_controllers[prev_cell].place_cursor_on_last_line()
                    elif not next_cell == None:
                        worksheet.set_active_cell(next_cell)
                        next_cell.place_cursor(next_cell.get_start_iter())
                    else:
                        worksheet.create_cell('last', '', activate=True)
                    cell.remove_result()
                    worksheet.remove_cell(cell)
                    return True
        
        return False
    
    def on_cursor_movement(self, cell=None, mark=None, user_data=None):
        self.main_controller.scroll_to_cursor(self.cell, check_if_position_changed=True)

    def on_paste(self, cell=None, clipboard=None, user_data=None):
        ''' hack to prevent some gtk weirdness. '''
            
        prev_insert = self.cell.create_mark('name', self.cell.get_iter_at_mark(self.cell.get_insert()), True)
        self.cell.insert_at_cursor('\n')
        GLib.idle_add(lambda: self.cell.delete(self.cell.get_iter_at_mark(self.cell.get_insert()), self.cell.get_iter_at_mark(prev_insert)))

    def on_focus_in(self, cell_view, event=None):
        ''' activate cell on click '''

        if self.cell.is_active_cell() == False:
            self.cell.get_worksheet().set_active_cell(self.cell)
        if self.cell_view.text_widget.get_reveal_child():
            self.cell_view.text_entry.grab_focus()
            self.main_controller.scroll_to_cursor(cell_view.text_entry.get_buffer(), check_if_position_changed=True)
        return False
    
    def on_source_view_focus_in(self, source_view, event=None):
        ''' activate cell on click '''

        if self.cell.is_active_cell() == False:
            self.cell.get_worksheet().set_active_cell(self.cell)
            return True
        return False
    
    def on_size_allocate(self, text_field, allocation=None):
        self.main_controller.scroll_to_cursor(text_field.get_buffer(), check_if_position_changed=True)
        
    '''
    *** helpers: cell
    '''
    
    def place_cursor_on_last_line(self):
        target_iter = self.cell_view.text_entry.get_iter_at_position(0, self.cell_view.text_entry.get_allocated_height() - 30)
        self.cell.place_cursor(target_iter[1])


class CodeCellController(CellController):

    def __init__(self, cell, cell_view, worksheet_controller, main_controller):
        CellController.__init__(self, cell, cell_view, worksheet_controller, main_controller)

        self.cell.register_observer(self.main_controller.backend_controller_code)

    def add_result_view(self, result, show_animation=False):
        cell_view_position = self.cell.get_worksheet_position()
                
        # check if cell view is still present
        if cell_view_position >= 0:

            # remove previous results
            revealer = self.cell_view.result_view_revealer
                
            # add result
            if result == None:
                revealer.unreveal()
                self.cell_view.text_widget.set_reveal_child(True)
                self.cell_view.text_entry.set_editable(True)
            else:
                revealer.set_result(result)
                revealer.show_all()
                GLib.idle_add(lambda: revealer.reveal(show_animation))
                result.scrolled_window.connect('scroll-event', self.result_on_scroll)

            # enable auto-scrolling for this cell (not enabled on startup)
            GLib.idle_add(lambda: revealer.set_autoscroll_on_reveal(True))

    def result_on_scroll(self, scrolled_window, event):
        if(abs(event.delta_y) > 0):
            adjustment = self.worksheet_controller.worksheet_view.get_vadjustment()

            page_size = adjustment.get_page_size()
            scroll_unit = pow (page_size, 2.0 / 3.0)

            adjustment.set_value(adjustment.get_value() + event.delta_y*scroll_unit)
        return True


class MarkdownCellController(CellController):

    def __init__(self, cell, cell_view, toolbar, worksheet_controller, main_controller):
        CellController.__init__(self, cell, cell_view, worksheet_controller, main_controller)
    
        self.toolbar = toolbar

        self.cell.register_observer(self.main_controller.backend_controller_markdown)
        
    def add_result_view(self, result, show_animation=False):
        cell_view_position = self.cell.get_worksheet_position()
                
        # check if cell view is still present
        if cell_view_position >= 0:

            # remove previous results
            revealer = self.cell_view.result_view_revealer

            # add result
            if result == None:
                revealer.unreveal()
                self.cell_view.text_widget.set_reveal_child(True)
                self.cell_view.text_entry.set_editable(True)
            else:
                self.cell_view.unreveal(show_animation)
                self.cell_view.text_entry.set_editable(False)
                revealer.set_result(result)
                revealer.show_all()
                if show_animation == False:
                    revealer.reveal(show_animation)
                else:
                    GLib.idle_add(lambda: revealer.reveal(show_animation))
                result.content.connect('button-press-event', self.result_on_button_press)

            # enable auto-scrolling for this cell (not enabled on startup)
            GLib.idle_add(lambda: revealer.set_autoscroll_on_reveal(True))

    def result_on_button_press(self, widget, event, user_data=None):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            cell_view = self.cell_view
            cell = cell_view.get_cell()
            worksheet = cell.get_worksheet()
            cell.remove_result()
            worksheet.set_active_cell(cell)
            return True
        elif event.type == Gdk.EventType.BUTTON_PRESS:
            cell_view = self.cell_view
            cell = cell_view.get_cell()
            worksheet = cell.get_worksheet()
            worksheet.set_active_cell(cell)
            return False


