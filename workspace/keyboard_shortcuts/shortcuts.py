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
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Gtk

import cell.cell as model_cell
from app.service_locator import ServiceLocator


class Shortcuts(object):
    ''' Handle Keyboard shortcuts. '''
    
    def __init__(self, workspace):
        self.main_window = ServiceLocator.get_main_window()
        self.workspace = workspace
        
        self.setup_shortcuts()

    def setup_shortcuts(self):
    
        self.accel_group = Gtk.AccelGroup()
        self.main_window.add_accel_group(self.accel_group)
        
        c_mask = Gdk.ModifierType.CONTROL_MASK
        s_mask = Gdk.ModifierType.SHIFT_MASK
        m1_mask = Gdk.ModifierType.MOD1_MASK
        m_mask = Gdk.ModifierType.META_MASK
        flags = Gtk.AccelFlags.MASK
        
        #self.accel_group.connect(Gdk.keyval_from_name('BackSpace'), 0, flags, self.shortcut_backspace)
        self.accel_group.connect(Gdk.keyval_from_name('Return'), s_mask, flags, self.shortcut_eval)
        self.accel_group.connect(Gdk.keyval_from_name('Return'), c_mask, flags, self.shortcut_eval_go_next)
        self.accel_group.connect(Gdk.keyval_from_name('Return'), m1_mask, flags, self.shortcut_add_codecell_below)
        self.accel_group.connect(Gdk.keyval_from_name('Return'), m1_mask | s_mask, flags, self.shortcut_eval_add)
        self.accel_group.connect(Gdk.keyval_from_name('m'), c_mask, flags, self.shortcut_add_markdown_cell)
        self.accel_group.connect(Gdk.keyval_from_name('h'), c_mask, flags, self.shortcut_stop_computation)
        self.accel_group.connect(Gdk.keyval_from_name('BackSpace'), c_mask, flags, self.shortcut_delete_cell)
        self.accel_group.connect(Gdk.keyval_from_name('Up'), c_mask, flags, self.shortcut_move_cell_up)
        self.accel_group.connect(Gdk.keyval_from_name('Down'), c_mask, flags, self.shortcut_move_cell_down)
        self.accel_group.connect(Gdk.keyval_from_name('r'), c_mask, flags, self.shortcut_restart_kernel)
        self.accel_group.connect(Gdk.keyval_from_name('Page_Up'), 0, flags, self.shortcut_page_up)
        self.accel_group.connect(Gdk.keyval_from_name('Page_Down'), 0, flags, self.shortcut_page_down)
        self.accel_group.connect(Gdk.keyval_from_name('n'), c_mask, flags, self.shortcut_create_worksheet)
        self.accel_group.connect(Gdk.keyval_from_name('o'), c_mask, flags, self.shortcut_open_worksheet)
        self.accel_group.connect(Gdk.keyval_from_name('s'), c_mask, flags, self.shortcut_save)
        self.accel_group.connect(Gdk.keyval_from_name('s'), c_mask | s_mask, flags, self.shortcut_save_as)

        self.main_window.worksheet_view_wrapper.connect('key-press-event', self.on_worksheet_key_pressed)

    def on_worksheet_key_pressed(self, worksheet_wrapper, event, user_data=None):
        if event.keyval == Gdk.keyval_from_name('Return') and ((event.state & Gtk.accelerator_get_default_mod_mask()) == 0):
            self.shortcut_edit_markdown()

    def shortcut_edit_markdown(self, accel_group=None, window=None, key=None, mask=None):
        worksheet = self.workspace.active_worksheet
        if worksheet != None:
            cell = worksheet.get_active_cell()
            if isinstance(cell, model_cell.MarkdownCell) and cell.get_result() != None:
                cell.remove_result()
                worksheet.set_active_cell(cell)
                cell.place_cursor(cell.get_start_iter())
                return True
        return False

    def shortcut_eval(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.evaluate_active_cell()
        return True

    def shortcut_eval_go_next(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.evaluate_active_cell_and_go_to_next()
        return True

    def shortcut_add_codecell_below(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.add_codecell_below_active_cell()
        return True

    def shortcut_eval_add(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.evaluate_active_cell()
            self.workspace.active_worksheet.add_codecell_below_active_cell()
        return True

    def shortcut_add_markdown_cell(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.add_markdowncell_below_active_cell()
        return True

    def shortcut_stop_computation(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.stop_evaluation()
        return True

    def shortcut_delete_cell(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.delete_active_cell()
        return True

    def shortcut_move_cell_up(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.move_cell_up()
        return True

    def shortcut_move_cell_down(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.move_cell_down()
        return True

    def shortcut_restart_kernel(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.controller.on_wsmenu_restart_kernel()

    def shortcut_page_up(self, accel_group=None, window=None, key=None, mask=None):
        try: worksheet_view = self.main_window.active_worksheet_view
        except AttributeError: pass
        else:
            scroll_position = worksheet_view.get_vadjustment()
            window_height = worksheet_view.get_allocated_height()
            scroll_position.set_value(scroll_position.get_value() - window_height)
        return True
        
    def shortcut_page_down(self, accel_group=None, window=None, key=None, mask=None):
        try: worksheet_view = self.main_window.active_worksheet_view
        except AttributeError: pass
        else:
            scroll_position = worksheet_view.get_vadjustment()
            window_height = worksheet_view.get_allocated_height()
            scroll_position.set_value(scroll_position.get_value() + window_height)
        return True

    def shortcut_create_worksheet(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.controller.on_create_ws_button_click()

    def shortcut_open_worksheet(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.controller.on_open_ws_button_click()

    def shortcut_save(self, accel_group=None, window=None, key=None, mask=None):
        worksheet = self.workspace.get_active_worksheet()
        if worksheet != None:
            worksheet.save_to_disk()

    def shortcut_save_as(self, accel_group=None, window=None, key=None, mask=None):
        self.workspace.controller.on_wsmenu_save_as()


