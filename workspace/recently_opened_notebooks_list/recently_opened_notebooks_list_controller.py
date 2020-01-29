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

import notebook.notebook as model_notebook
from app.service_locator import ServiceLocator


class RecentlyOpenedNotebooksListController(object):

    def __init__(self, workspace, recently_opened_notebooks):
        self.sidebar = ServiceLocator.get_main_window().sidebar
        self.hbchooser = ServiceLocator.get_main_window().headerbar.hb_right.notebook_chooser
        self.workspace = workspace
        self.recently_opened_notebooks = recently_opened_notebooks

        for widget in [self.sidebar, self.hbchooser]:
            widget.recent_notebooks_list_view.set_sort_func(self.sort_func)
            widget.recent_notebooks_list_view.connect('row-activated', self.on_recent_notebooks_list_click)

        self.recently_opened_notebooks.populate_from_disk()

    def on_recent_notebooks_list_click(self, wslist_view, wslist_item_view):
        if wslist_item_view != None:
            pathname = wslist_item_view.pathname
            self.workspace.controller.open_ws_action(None, pathname)
            self.hbchooser.popdown()

    def select_row_by_notebook(self, notebook):
        for widget in [self.sidebar, self.hbchooser]:
            row_index = widget.open_notebooks_list_view.get_row_index_by_notebook(notebook)
            row = widget.open_notebooks_list_view.get_row_at_index(row_index)
            widget.open_notebooks_list_view.select_row(row)
            self.scroll_row_on_screen(row)

    def scroll_row_on_screen(self, row):
        for widget in [self.sidebar, self.hbchooser]:
            sw = widget.open_notebooks_list_view_wrapper
            item_offset = 48 * (row.get_index() - 1)
            viewport_offset = sw.get_vadjustment().get_value()
            viewport_height = sw.get_allocated_height()
            if item_offset < viewport_offset:
                sw.get_vadjustment().set_value(item_offset)
            elif item_offset > (viewport_offset + viewport_height - 48):
                sw.get_vadjustment().set_value(item_offset + viewport_height - 48)

    def sort_func(self, row1, row2):
        if row1.last_saved > row2.last_saved: return -1
        elif row1.last_saved < row2.last_saved: return 1
        else: return 0


