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
import notebook.notebook as model_notebook

import os.path


class WorkspaceController(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.settings = ServiceLocator.get_settings()

        self.main_window.toggle_sidebar_action.connect('activate', self.toggle_sidebar)
        self.main_window.preferences_action.connect('activate', self.show_preferences_dialog)
        self.main_window.show_about_dialog_action.connect('activate', self.show_about_dialog)
        self.main_window.show_shortcuts_window_action.connect('activate', self.show_shortcuts_window)
        self.main_window.sidebar.connect('size-allocate', self.on_sidebar_size_allocate)

        self.main_window.restart_kernel_action.connect('activate', self.on_wsmenu_restart_kernel)
        self.main_window.change_kernel_action.connect('activate', self.on_wsmenu_change_kernel)
        self.main_window.save_all_action.connect('activate', self.on_wsmenu_save_all)
        self.main_window.save_as_action.connect('activate', self.on_wsmenu_save_as)
        self.main_window.delete_ws_action.connect('activate', self.on_wsmenu_delete)
        self.main_window.close_action.connect('activate', self.on_wsmenu_close)
        self.main_window.close_all_action.connect('activate', self.on_wsmenu_close_all)
        self.main_window.open_action.connect('activate', self.open_ws_action)
        self.main_window.create_action.connect('activate', self.create_ws_action)

        self.settings.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'pretty_print'):
                self.workspace.set_pretty_print(self.settings.get_value('preferences', 'pretty_print'))

    def on_sidebar_size_allocate(self, paned, paned_size):
        self.workspace.sidebar_position = self.main_window.paned.get_position()
            
    def open_ws_action(self, action=None, pathname=None):
        if pathname == None:
            pathname = ServiceLocator.get_dialog('open_notebook').run()
        if pathname != None:
            notebook = self.workspace.get_notebook_by_pathname(pathname)
            if notebook == None:
                if pathname.split('.')[-1] == 'ipynb':
                    notebook = model_notebook.Notebook(pathname)
                    try:
                        notebook.load_from_disk()
                    except FileNotFoundError:
                        notebook = None
                    except model_notebook.KernelMissing as e:
                        ServiceLocator.get_dialog('kernel_missing').run(str(e))
                    else:
                        self.workspace.add_notebook(notebook)
            if notebook != None:
                self.workspace.set_active_notebook(notebook)

    def create_ws_action(self, action=None, parameter=None):
        parameters = ServiceLocator.get_dialog('create_notebook').run()
        if parameters != None:
            pathname, kernelname = parameters
            self.workspace.recently_opened_notebooks.remove_notebook_by_pathname(pathname)
            self.workspace.remove_notebook_by_pathname(pathname)

            notebook = model_notebook.Notebook(pathname)
            notebook.set_kernelname(kernelname)
            notebook.create_cell(0, '', activate=True)
            notebook.save_to_disk()
            self.workspace.add_notebook(notebook)
            self.workspace.set_active_notebook(notebook)

    def on_wsmenu_restart_kernel(self, action=None, parameter=None):
        if self.workspace.active_notebook != None:
            self.workspace.active_notebook.restart_kernel()
        
    def on_wsmenu_change_kernel(self, action=None, parameter=None):
        if parameter != None:
            self.main_window.change_kernel_action.set_state(parameter)
            notebook = self.workspace.active_notebook
            if notebook.get_kernelname() != parameter.get_string():
                notebook.set_kernelname(parameter.get_string())
                notebook.restart_kernel()

    def on_wsmenu_save_as(self, action=None, parameter=None):
        notebook = self.workspace.get_active_notebook()
        if notebook != None:
            ServiceLocator.get_dialog('save_as').run(notebook)

    def on_wsmenu_save_all(self, action=None, parameter=None):
        for notebook in self.workspace.open_notebooks:
            notebook.save_to_disk()

    def on_wsmenu_delete(self, action, parameter=None):
        self.delete_notebook(self.workspace.get_active_notebook())

    def on_wsmenu_close(self, action=None, parameter=None):
        notebook = self.workspace.get_active_notebook()
        if notebook != None:
            self.close_notebook_after_modified_check(notebook)

    def on_wsmenu_close_all(self, action=None, parameter=None):
        self.close_all_notebooks_after_modified_check()

    def close_notebook(self, notebook, add_to_recently_opened=True):
        self.workspace.remove_notebook(notebook)
        self.workspace.recently_opened_notebooks.remove_notebook_by_pathname(notebook.pathname)
        if add_to_recently_opened:
            pathname = notebook.get_pathname()
            kernelname = notebook.get_kernelname()
            if os.path.isfile(pathname):
                item = {'pathname': pathname, 'kernelname': kernelname, 'date': notebook.get_last_saved()}
                self.workspace.recently_opened_notebooks.add_item(item, notify=True, save=True)        

    def close_notebook_after_modified_check(self, notebook):
        if notebook.get_save_state() != 'modified' or ServiceLocator.get_dialog('close_confirmation').run([notebook])['all_save_to_close']:
            self.close_notebook(notebook)

    def close_all_notebooks_after_modified_check(self):
        notebooks = self.workspace.get_unsaved_notebooks()
        active_notebook = self.workspace.get_active_notebook()

        if len(notebooks) == 0 or active_notebook == None or ServiceLocator.get_dialog('close_confirmation').run(notebooks)['all_save_to_close']: 
            for notebook in list(self.workspace.open_notebooks.values()):
                self.close_notebook(notebook)

    def toggle_sidebar(self, action, parameter=None):
        show_sidebar = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(show_sidebar))
        self.workspace.set_show_sidebar(show_sidebar)

    def show_shortcuts_window(self, action, parameter=''):
        ServiceLocator.get_dialog('keyboard_shortcuts').run()

    def show_preferences_dialog(self, action=None, parameter=''):
        ServiceLocator.get_dialog('preferences').run()

    def show_about_dialog(self, action, parameter=''):
        ServiceLocator.get_dialog('about').run()

    def delete_notebook(self, notebook):
        if ServiceLocator.get_dialog('delete_notebook').run(notebook):
            self.close_notebook(notebook, add_to_recently_opened=False)
            notebook.remove_from_disk()


