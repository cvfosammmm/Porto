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
from gi.repository import Gtk, GLib

import notebook.notebook as model_notebook
from app.service_locator import ServiceLocator


class OpenNotebooksListController(object):

    def __init__(self, workspace, sb_view, hb_view):
        self.sb_view = sb_view
        self.hb_view = hb_view
        self.sidebar = ServiceLocator.get_main_window().sidebar
        self.hbchooser = ServiceLocator.get_main_window().headerbar.hb_right.notebook_chooser
        self.main_window = ServiceLocator.get_main_window()
        self.workspace = workspace
        self.open_notebook_should_scroll = False
        self.open_notebook_hb_should_scroll = False

        self.sidebar.connect('size-allocate', self.on_open_notebook_view_size_allocate)
        self.hbchooser.connect('size-allocate', self.on_open_notebook_hb_view_size_allocate)
        self.sb_view.connect('row-selected', self.on_open_notebooks_list_selected)
        self.hb_view.connect('row-selected', self.on_open_notebooks_list_selected)

    def on_open_notebooks_list_selected(self, list_view, list_item_view):
        if list_item_view != None:
            notebook = list_item_view.get_notebook()
            self.workspace.set_active_notebook(notebook)
            GLib.idle_add(self.scroll_row_on_screen, list_view, list_item_view)

    def scroll_row_on_screen(self, view, row):
        if view == self.sb_view: widget = self.sidebar
        if view == self.hb_view: widget = self.hbchooser
        sw = widget.open_notebooks_list_view_wrapper
        item_offset = 48 * row.get_index()
        viewport_offset = sw.get_vadjustment().get_value()
        viewport_height = sw.get_allocated_height()
        if item_offset < viewport_offset:
            sw.get_vadjustment().set_value(item_offset)
        elif item_offset > (viewport_offset + viewport_height - 48):
            sw.get_vadjustment().set_value(item_offset - viewport_height + 48)

    def on_open_notebook_view_size_allocate(self, widget=None, allocation=None):
        sw = self.sidebar.open_notebooks_list_view_wrapper
        open_notebook_height = 48 * self.sb_view.visible_items_count
        self_height = self.sidebar.get_allocated_height()
        open_notebook_should_scroll = open_notebook_height >= self_height / 2
        if open_notebook_should_scroll != self.open_notebook_should_scroll:
            self.open_notebook_should_scroll = open_notebook_should_scroll
        if self.open_notebook_should_scroll:
            sw.set_size_request(-1, self_height / 2)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        else:
            sw.set_size_request(-1, -1)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

    def on_open_notebook_hb_view_size_allocate(self, widget=None, allocation=None):
        sw = self.hbchooser.open_notebooks_list_view_wrapper
        open_notebook_height = 49 * self.hb_view.visible_items_count
        self_height = 500
        open_notebook_hb_should_scroll = (open_notebook_height >= 196)
        if open_notebook_hb_should_scroll != self.open_notebook_hb_should_scroll:
            self.open_notebook_hb_should_scroll = open_notebook_hb_should_scroll
        if self.open_notebook_hb_should_scroll:
            sw.set_size_request(-1, 174)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        else:
            sw.set_size_request(-1, -1)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)


