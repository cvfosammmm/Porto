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


class OpenNotebooksListPresenter(object):

    def __init__(self, workspace, open_notebooks_list, sb_view, hb_view):
        self.workspace = workspace
        self.open_notebooks_list = open_notebooks_list
        self.main_window = ServiceLocator.get_main_window()

        self.sidebar = ServiceLocator.get_main_window().sidebar
        self.sb_view = sb_view
        self.sb_view.set_can_focus(False)
        self.sb_view.set_sort_func(self.sort_func)
        self.sidebar.open_notebooks_list_view_wrapper.add(self.sb_view)

        self.hbchooser = ServiceLocator.get_main_window().headerbar.hb_right.notebook_chooser
        self.hb_view = hb_view
        self.hb_view.set_can_focus(False)
        self.hb_view.set_sort_func(self.sort_func)
        self.hbchooser.open_notebooks_list_view_wrapper.add(self.hb_view)

        self.hbchooser.open_notebooks_list_view_wrapper.hide()
        self.workspace.register_observer(self)
        self.open_notebooks_list.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_open_notebook_item':
            sb_item, hb_item = parameter

            self.sb_view.add_item(sb_item)
            sb_item.close_button.connect('clicked', self.on_close_button_clicked, sb_item.notebook)
            self.sidebar.open_notebooks_label_revealer.set_reveal_child(True)
            self.sidebar.open_notebooks_list_view_wrapper.show_all()

            self.hb_view.add_item(hb_item)
            hb_item.close_button.connect('clicked', self.on_close_button_clicked, hb_item.notebook)
            self.hbchooser.open_notebooks_label_revealer.set_reveal_child(True)
            self.hbchooser.open_notebooks_list_view_wrapper.show_all()

            self.main_window.headerbar.hb_right.increment_notebooks_number()

        if change_code == 'removed_open_notebook_item':
            sb_item, hb_item = parameter

            self.sb_view.remove_item(sb_item)
            if self.sb_view.visible_items_count < 1:
                self.sidebar.open_notebooks_list_view_wrapper.hide()
                self.sidebar.open_notebooks_label_revealer.set_reveal_child(False)

            self.hb_view.remove_item(hb_item)
            if self.hb_view.visible_items_count < 1:
                self.hbchooser.open_notebooks_list_view_wrapper.hide()
                self.hbchooser.open_notebooks_label_revealer.set_reveal_child(False)

            self.main_window.headerbar.hb_right.decrement_notebooks_number()

        if change_code == 'new_active_open_notebook_item':
            sb_item, hb_item = parameter

            self.sb_view.select_row(sb_item)
            if self.sb_view.selected_row != None:
                self.sb_view.selected_row.set_icon_type('normal')
            self.sb_view.selected_row = sb_item
            self.sb_view.selected_row.set_icon_type('active')

            self.hb_view.select_row(hb_item)
            if self.sb_view.selected_row != None:
                self.sb_view.selected_row.set_icon_type('normal')
            self.sb_view.selected_row = hb_item
            self.sb_view.selected_row.set_icon_type('active')

    def on_close_button_clicked(self, button, notebook):
        self.workspace.controller.close_notebook_after_modified_check(notebook)

    def sort_func(self, row1, row2):
        if row1.last_saved > row2.last_saved: return -1
        elif row1.last_saved < row2.last_saved: return 1
        else: return 0


