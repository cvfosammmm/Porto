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

import workspace.workspace_presenter as workspace_presenter
import workspace.workspace_controller as workspace_controller
import workspace.recently_opened_notebooks_list.recently_opened_notebooks_list as ro_notebooks_list
import workspace.open_notebooks_list.open_notebooks_list as open_notebooks_list
import notebook.notebook as model_notebook
import workspace.headerbar.headerbar as headerbar_model
import workspace.keyboard_shortcuts.shortcuts as shortcuts
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class Workspace(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.recently_opened_notebooks = ro_notebooks_list.RecentlyOpenedNotebooksList(self)
        self.open_notebooks_list = open_notebooks_list.OpenNotebooksList(self)
        self.open_notebooks = dict()
        self.active_notebook = None

        self.settings = ServiceLocator.get_settings()
        self.show_sidebar = self.settings.get_value('window_state', 'sidebar_visible')
        self.sidebar_position = self.settings.get_value('window_state', 'paned_position')
        self.presenter = workspace_presenter.WorkspacePresenter(self)
        self.controller = workspace_controller.WorkspaceController(self)
        self.headerbar = headerbar_model.Headerbar(self)
        self.shortcuts = shortcuts.Shortcuts(self)

        self.set_pretty_print(self.settings.get_value('preferences', 'pretty_print'))

    def add_notebook(self, notebook):
        if notebook in self.open_notebooks: return False
        self.open_notebooks[notebook] = notebook
        self.open_notebooks_list.add_item_by_notebook(notebook)
        item = {'pathname': notebook.pathname, 'kernelname': notebook.kernelname, 'date': notebook.get_last_saved()}
        self.recently_opened_notebooks.add_item(item)
        self.add_change_code('new_notebook', notebook)

    def get_notebook_by_pathname(self, pathname):
        for notebook in self.open_notebooks:
            if notebook.pathname == pathname:
                return notebook
        return None

    def set_active_notebook(self, notebook):
        if notebook != self.active_notebook:
            self.active_notebook = notebook
            self.add_change_code('changed_active_notebook', notebook)
            if notebook != None:
                self.open_notebooks_list.activate_item_by_notebook(notebook)
        
    def get_active_notebook(self):
        return self.active_notebook
        
    def get_unsaved_notebooks(self):
        ''' return notebooks with unsaved changes '''
        
        matching_notebooks = list()
        for notebook in self.open_notebooks.values():
            if notebook.get_save_state() == 'modified':
                matching_notebooks.append(notebook)
        return matching_notebooks

    def get_notebook_by_pathname(self, pathname):
        for notebook in self.open_notebooks.values():
            if notebook.pathname == pathname:
                return notebook
        return None

    def remove_notebook(self, notebook):
        try: notebook = self.open_notebooks[notebook]
        except KeyError: pass
        else:
            notebook.shutdown_kernel()
            self.open_notebooks_list.remove_item_by_notebook(notebook)
            del(self.open_notebooks[notebook])
            if len(self.open_notebooks) < 1:
                self.set_active_notebook(None)
            elif self.get_active_notebook() == notebook:
                new_active = False
                def sort_func(nb): return nb.last_saved
                for nb in sorted(self.open_notebooks, key=sort_func, reverse=True):
                    if nb.last_saved <= notebook.last_saved:
                        self.set_active_notebook(nb)
                        new_active = True
                        break
                if new_active == False:
                    for nb in sorted(self.open_notebooks, key=sort_func, reverse=False):
                        self.set_active_notebook(nb)
                        break
            self.add_change_code('notebook_removed', notebook)
        
    def remove_notebook_by_pathname(self, pathname):
        notebook = self.get_notebook_by_pathname(pathname)
        if notebook != None:
            self.remove_notebook(notebook)

    def set_show_sidebar(self, value):
        self.show_sidebar = value
        self.add_change_code('sidebar_state', value)

    def set_pretty_print(self, value):
        self.add_change_code('set_pretty_print', value)

    def shutdown_all_kernels(self):
        for notebook in self.open_notebooks:
            notebook.shutdown_kernel_now()


