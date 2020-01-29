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
from gi.repository import Gio

from app.service_locator import ServiceLocator
import notebook.notebook as model_notebook


class HeaderbarPresenter(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.headerbar = ServiceLocator.get_main_window().headerbar
        self.kernelspecs = ServiceLocator.get_kernelspecs()

        self.window_mode = None
        self.activate_welcome_page_mode()
        self.setup_kernel_changer()

        if self.workspace.show_sidebar:
            self.on_show_sidebar()
        else:
            self.on_hide_sidebar()

        self.workspace.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_notebook':
            self.activate_notebook_mode()

        if change_code == 'notebook_removed':
            if self.workspace.get_active_notebook() == None:
                headerbar = self.headerbar.hb_right
                if headerbar.current_save_button != None:
                    headerbar.remove(headerbar.current_save_button)
                    headerbar.current_save_button = None
                if headerbar.current_controls != None:
                    headerbar.remove(headerbar.current_controls)
                    headerbar.current_controls = None
                if headerbar.current_add_cell_box != None:
                    headerbar.remove(headerbar.current_add_cell_box)
                    headerbar.current_add_cell_box = None
                if headerbar.current_move_cell_box != None:
                    headerbar.remove(headerbar.current_move_cell_box)
                    headerbar.current_move_cell_box = None
                if headerbar.current_eval_box != None:
                    headerbar.remove(headerbar.current_eval_box)
                    headerbar.current_eval_box = None
                self.activate_welcome_page_mode()

        if change_code == 'changed_active_notebook':
            notebook = parameter
            if notebook != None:
                self.activate_notebook_mode()
                self.update_title(notebook)
                self.update_save_button(notebook)
                self.update_controls(notebook)

        if change_code == 'sidebar_state':
            if parameter == True:
                self.on_show_sidebar()
            else:
                self.on_hide_sidebar()

    def setup_kernel_changer(self):
        menu = self.headerbar.hb_right.change_kernel_menu
        for name in self.kernelspecs.get_list_of_names():
            item = Gio.MenuItem.new(self.kernelspecs.get_displayname(name), 'win.change_kernel::' + name)
            menu.append_item(item)

    def update_title(self, notebook):
        headerbar = self.headerbar.hb_right
        headerbar.set_custom_title(notebook.headerbar_controls.title)
        
    def update_controls(self, notebook):
        headerbar = self.headerbar.hb_right

        if headerbar.current_add_cell_box != None:
            headerbar.remove(headerbar.current_add_cell_box)
        headerbar.current_add_cell_box = notebook.headerbar_controls.button_box.add_cell_box
        headerbar.pack_start(notebook.headerbar_controls.button_box.add_cell_box)

        if headerbar.current_move_cell_box != None:
            headerbar.remove(headerbar.current_move_cell_box)
        headerbar.current_move_cell_box = notebook.headerbar_controls.button_box.move_cell_box
        headerbar.pack_start(notebook.headerbar_controls.button_box.move_cell_box)

        if headerbar.current_eval_box != None:
            headerbar.remove(headerbar.current_eval_box)
        headerbar.current_eval_box = notebook.headerbar_controls.button_box.eval_box
        headerbar.pack_start(notebook.headerbar_controls.button_box.eval_box)

    def update_save_button(self, notebook):
        headerbar = self.headerbar.hb_right
        if headerbar.current_save_button != None:
            headerbar.remove(headerbar.current_save_button)
        headerbar.current_save_button = notebook.headerbar_controls.save_button
        headerbar.pack_end(notebook.headerbar_controls.save_button)

    def activate_welcome_page_mode(self):
        if self.window_mode != 'welcome_page':
            self.window_mode = 'welcome_page'
            hb_right = self.headerbar.hb_right
            hb_right.hide_buttons()
            hb_right.set_custom_title(hb_right.welcome_title)

    def activate_notebook_mode(self):
        if self.window_mode != 'notebook':
            self.window_mode = 'notebook'
            hb_right = self.headerbar.hb_right
            hb_right.show_buttons()

    def on_show_sidebar(self):
        self.headerbar.hb_left.show_all()
        self.headerbar.hb_right.open_notebooks_button.hide()

    def on_hide_sidebar(self):
        self.headerbar.hb_left.hide()
        self.headerbar.hb_right.open_notebooks_button.show_all()


