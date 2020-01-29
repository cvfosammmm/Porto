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
from gi.repository import Pango


class OpenNotebookListViewItem(Gtk.ListBoxRow):

    def __init__(self, notebook, last_saved):
        Gtk.ListBoxRow.__init__(self)
        self.get_style_context().add_class('wslist_item')

        self.icon_stack = Gtk.Stack()
        self.icon_normal = None
        self.icon_active = None
        self.icon_type = None
        
        self.notebook_name = notebook.get_pathname()
        self.last_saved = last_saved
        
        self.name = Gtk.Label()
        self.name.set_justify(Gtk.Justification.LEFT)
        self.name.set_xalign(0)
        self.name.set_hexpand(False)
        self.name.set_single_line_mode(True)
        self.name.set_max_width_chars(-1)
        self.name.set_ellipsize(Pango.EllipsizeMode.END)
        self.name.get_style_context().add_class('wslist_name')

        self.box = Gtk.HBox()
        self.box.pack_start(self.icon_stack, False, False, 0)

        self.notebook = notebook

        self.statebox = Gtk.HBox()
        self.state = Gtk.Label()
        self.state.set_justify(Gtk.Justification.LEFT)
        self.state.set_xalign(0)
        self.state.set_hexpand(False)
        self.state.get_style_context().add_class('wslist_state')
        self.statebox.pack_start(self.state, True, True, 0)

        self.topbox = Gtk.HBox()
        self.close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.close_button.get_style_context().add_class('wslist_close_button')
        self.close_button.set_can_focus(False)
        self.close_button.set_tooltip_text('Close Notebook')
        
        self.textbox = Gtk.VBox()
        self.textbox.pack_start(self.name, False, False, 0)
        self.textbox.pack_start(self.statebox, True, True, 0)
        
        self.topbox.pack_start(self.textbox, False, False, 0)
        self.topbox.pack_end(self.close_button, False, False, 0)

        self.box.pack_end(self.topbox, True, True, 0)
        self.box.get_style_context().add_class('wslist_wrapper')
        self.add(self.box)
        
        self.set_name(self.notebook_name)

    def set_icon_type(self, icon_type='normal'):
        self.icon_type = icon_type
        self.icon_stack.set_visible_child_name(icon_type)
        
    def set_name(self, new_name):
        self.notebook_name = new_name
        self.name.set_text(self.notebook_name)
        
    def get_notebook(self):
        return self.notebook

    def set_last_saved(self, new_date):
        self.last_saved = new_date
        self.changed()
        

