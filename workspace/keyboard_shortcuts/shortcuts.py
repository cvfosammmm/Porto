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
        self.accel_group.connect(Gdk.keyval_from_name('Up'), c_mask, flags, self.shortcut_move_cell_up)
        self.accel_group.connect(Gdk.keyval_from_name('Down'), c_mask, flags, self.shortcut_move_cell_down)
        self.accel_group.connect(Gdk.keyval_from_name('Page_Up'), 0, flags, self.shortcut_page_up)
        self.accel_group.connect(Gdk.keyval_from_name('Page_Down'), 0, flags, self.shortcut_page_down)
        self.accel_group.connect(Gdk.keyval_from_name('s'), c_mask, flags, self.shortcut_save)

        self.main_window.app.set_accels_for_action('win.quit', ['<Control>q'])
        self.main_window.app.set_accels_for_action('win.open', ['<Control>o'])
        self.main_window.app.set_accels_for_action('win.create', ['<Control>n'])
        self.main_window.app.set_accels_for_action('win.save_as', ['<Control><Shift>s'])
        self.main_window.app.set_accels_for_action('win.restart_kernel', ['<Control>r'])

        self.main_window.notebook_view_wrapper.connect('key-press-event', self.on_notebook_key_pressed)

    def on_notebook_key_pressed(self, notebook_wrapper, event, user_data=None):
        if event.keyval == Gdk.keyval_from_name('Return') and ((event.state & Gtk.accelerator_get_default_mod_mask()) == 0):
            self.shortcut_edit_markdown()

    def shortcut_edit_markdown(self, accel_group=None, window=None, key=None, mask=None):
        notebook = self.workspace.active_notebook
        if notebook != None:
            cell = notebook.get_active_cell()
            if isinstance(cell, model_cell.MarkdownCell) and cell.get_result() != None:
                cell.remove_result()
                notebook.set_active_cell(cell)
                cell.place_cursor(cell.get_start_iter())
                return True
        return False

    def shortcut_eval(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.evaluate_active_cell()
        return True

    def shortcut_eval_go_next(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.evaluate_active_cell_and_go_to_next()
        return True

    def shortcut_add_codecell_below(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.add_codecell_below_active_cell()
        return True

    def shortcut_eval_add(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.evaluate_active_cell()
            self.workspace.active_notebook.add_codecell_below_active_cell()
        return True

    def shortcut_add_markdown_cell(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.add_markdowncell_below_active_cell()
        return True

    def shortcut_stop_computation(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.stop_evaluation()
        return True

    def shortcut_move_cell_up(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.move_cell_up()
        return True

    def shortcut_move_cell_down(self, accel_group=None, window=None, key=None, mask=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.move_cell_down()
        return True

    def shortcut_page_up(self, accel_group=None, window=None, key=None, mask=None):
        try: notebook_view = self.main_window.active_notebook_view
        except AttributeError: pass
        else:
            scroll_position = notebook_view.get_vadjustment()
            window_height = notebook_view.get_allocated_height()
            scroll_position.set_value(scroll_position.get_value() - window_height)
        return True
        
    def shortcut_page_down(self, accel_group=None, window=None, key=None, mask=None):
        try: notebook_view = self.main_window.active_notebook_view
        except AttributeError: pass
        else:
            scroll_position = notebook_view.get_vadjustment()
            window_height = notebook_view.get_allocated_height()
            scroll_position.set_value(scroll_position.get_value() + window_height)
        return True

    def shortcut_save(self, accel_group=None, window=None, key=None, mask=None):
        notebook = self.workspace.get_active_notebook()
        if notebook != None:
            notebook.save_to_disk()


