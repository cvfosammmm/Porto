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

from app.service_locator import ServiceLocator


class NotebookPresenter(object):

    def __init__(self, notebook, notebook_view):
        self.notebook = notebook
        self.notebook_view = notebook_view

        # build it from current cells
        for cell in notebook.cells:
            self.add_cell_view(cell)

        # observe notebook
        notebook.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_cell':
            cell = parameter
            self.add_cell_view(cell)

        if change_code == 'deleted_cell':
            cell = parameter

            self.notebook_view.remove_child_by_position(cell.get_notebook_position())
        
        if change_code == 'new_active_cell':
            cell = parameter

            child_position = cell.get_notebook_position()
            cell_view = self.notebook_view.get_child_by_position(child_position)
            cell_view.set_active()
            cell_view.grab_focus()
            
        if change_code == 'new_inactive_cell':
            cell = parameter
            child_position = cell.get_notebook_position()
            cell_view = self.notebook_view.get_child_by_position(child_position)
            cell_view.set_inactive()
            
            # unselect text
            insert_mark = cell.get_iter_at_mark(cell.get_insert())
            selection_bound = cell.get_selection_bound()
            cell.move_mark(selection_bound, insert_mark)

        if change_code == 'cell_moved':
            cell_view1_position = parameter['position']
            cell_view2_position = parameter['new_position']
            
            # move cells
            cell_view1 = self.notebook_view.get_child_by_position(cell_view1_position)
            cell_view2 = self.notebook_view.get_child_by_position(cell_view2_position)
            self.notebook_view.move_child(cell_view1, cell_view2_position)
            self.notebook_view.move_child(cell_view2, cell_view1_position)
            
            cell_view1.grab_focus()
            GLib.idle_add(lambda: cell_view1.get_source_view().grab_focus())

    def add_cell_view(self, cell):
        notebook_position = cell.get_notebook_position()
        self.notebook_view.add_child_at_position(cell.view, notebook_position)


