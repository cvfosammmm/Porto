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
        self.items = dict()

        self.presenter = ro_presenter.RecentlyOpenedNotebooksListPresenter(workspace, self)
        self.controller = ro_controller.RecentlyOpenedNotebooksListController(workspace, self)

    def get_by_pathname(self, pathname):
        try:
            return self.items[pathname]
        except KeyError:
            return None

    def add_item(self, item, notify=True, save=True):
        if item['pathname'] == None: return
        try:
            self.update_item(item, notify, save)
        except KeyError:
            self.items[item['pathname']] = item
            if notify:
                self.add_change_code('add_recently_opened_notebook', item)
            if save:
                self.save_to_disk()

    def update_item(self, item, notify=True, save=True):
        self.items[item['pathname']] = item
        if notify:
            self.add_change_code('add_recently_opened_notebook', item)
        if save:
            self.save_to_disk()

    def remove_notebook_by_pathname(self, pathname):
        try:
            item = self.items[pathname]
        except KeyError:
            pass
        else:
            self.remove_item(item)

    def remove_item(self, item):
        del(self.items[item['pathname']])
        self.add_change_code('remove_recently_opened_notebook', item)
        self.save_to_disk()

    def populate_from_disk(self):
        try: filehandle = open(self.pathname + '/recently_openened.pickle', 'rb')
        except IOError: pass
        else:
            try: data = pickle.load(filehandle)
            except EOFError: pass
            else:
                for item in data.values():
                    if os.path.isfile(item['pathname']):
                        self.add_item(item, notify=True, save=False)

    def save_to_disk(self):
        try: filehandle = open(self.pathname + '/recently_openened.pickle', 'wb')
        except IOError: pass
        else:
            pickle.dump(self.items, filehandle)


