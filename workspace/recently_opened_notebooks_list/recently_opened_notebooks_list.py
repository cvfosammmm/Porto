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

import pickle
import os.path

import workspace.recently_opened_notebooks_list.recently_opened_notebooks_list_controller as ro_controller
import workspace.recently_opened_notebooks_list.recently_opened_notebooks_list_presenter as ro_presenter
from helpers.observable import Observable


class RecentlyOpenedNotebooksList(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)

        self.workspace = workspace
        self.pathname = os.path.expanduser('~') + '/.porto'
        self.items = list()

        self.presenter = ro_presenter.RecentlyOpenedNotebooksListPresenter(workspace, self)
        self.controller = ro_controller.RecentlyOpenedNotebooksListController(workspace, self)

    def get_by_pathname(self, pathname):
        for item in self.items:
            if item['pathname'] == pathname:
                return item
        return None

    def already_in_list(self, pathname):
        for item in self.items:
            if pathname == item['pathname']: return True
        return False

    def add_item(self, item, notify=True, save=True):
        if item['pathname'] == None: return
        if self.already_in_list(item['pathname']):
            pass
        else:
            self.items.append(item)
            if notify:
                self.add_change_code('add_recently_opened_notebook', item)
            if save:
                self.save_to_disk()

    def remove_notebook_by_pathname(self, pathname):
        item = self.get_by_pathname(pathname)
        if item != None:
            self.remove_item(item)

    def remove_item(self, item):
        self.items.remove(item)
        self.add_change_code('remove_recently_opened_notebook', item)
        self.save_to_disk()

    def populate_from_disk(self):
        try: filehandle = open(self.pathname + '/recently_openened.pickle', 'rb')
        except IOError: pass
        else:
            try: data = pickle.load(filehandle)
            except EOFError: pass
            else:
                for item in data:
                    if os.path.isfile(item['pathname']):
                        self.add_item(item, notify=True, save=False)

    def save_to_disk(self):
        try: filehandle = open(self.pathname + '/recently_openened.pickle', 'wb')
        except IOError: pass
        else:
            pickle.dump(self.items, filehandle)


