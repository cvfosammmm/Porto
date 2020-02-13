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

import cell.cell as model_cell
from app.service_locator import ServiceLocator


class ResultRevealerController(object):

    def __init__(self, result_revealer, view):

        self.result_revealer = result_revealer
        self.view = view

        self.view.connect('button-press-event', self.revealer_on_mouse_click)
        #self.view.connect('size-allocate', self.revealer_on_size_allocate)

    def revealer_on_mouse_click(self, result_view_revealer, click_event):
        if click_event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            cell = self.result_revealer.cell
            notebook = cell.get_notebook()
            self.result_revealer.remove_result()
            self.result_revealer.reset_streams()
            notebook.set_active_cell(cell)
        elif click_event.type == Gdk.EventType.BUTTON_PRESS:
            cell = self.result_revealer.cell
            notebook = cell.get_notebook()
            notebook.set_active_cell(cell)
        return False

    def revealer_on_size_allocate(self, result_view_revealer, allocation):
        cell = self.result_revealer.cell
        if cell != None and result_view_revealer.autoscroll_on_reveal == True:
            notebook_view = self.notebook.view
            cell_view_position = cell.get_notebook_position()
            cell_view = notebook_view.get_child_by_position(cell_view_position)
            x, cell_position = cell_view.translate_coordinates(notebook_view.box, 0, 0)
            x, result_position = result_view_revealer.translate_coordinates(notebook_view.box, 0, 0)
            
            last_allocation = result_view_revealer.allocation
            result_view_revealer.allocation = allocation
            if cell_position > result_position:
                notebook_view.scroll(allocation.height - last_allocation.height)


class CodeResultRevealerController(ResultRevealerController):

    def __init__(self, result_revealer, view):
        ResultRevealerController.__init__(self, result_revealer, view)


class MarkdownResultRevealerController(ResultRevealerController):

    def __init__(self, result_revealer, view):
        ResultRevealerController.__init__(self, result_revealer, view)


