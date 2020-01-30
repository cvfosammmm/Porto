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

from helpers.observable import Observable
import workspace.open_notebooks_list.open_notebooks_list_viewgtk as onb_view
import workspace.open_notebooks_list.open_notebooks_list_presenter as onb_presenter
import workspace.open_notebooks_list.open_notebooks_list_controller as onb_controller


class OpenNotebooksList(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace

        self.sb_items = dict()
        self.hb_items = dict()

        self.sb_view = onb_view.OpenNotebooksListView()
        self.hb_view = onb_view.OpenNotebooksListView()
        self.presenter = onb_presenter.OpenNotebooksListPresenter(workspace, self, self.sb_view, self.hb_view)
        self.controller = onb_controller.OpenNotebooksListController(workspace, self.sb_view, self.hb_view)

    def add_item_by_notebook(self, notebook, notify=True):
        sb_item = notebook.list_item.sb_view
        hb_item = notebook.list_item.hb_view
        self.sb_items[notebook] = sb_item
        self.hb_items[notebook] = hb_item
        if notify:
            self.add_change_code('new_open_notebook_item', (sb_item, hb_item))

    def remove_item_by_notebook(self, notebook, notify=True):
        sb_item = self.sb_items[notebook]
        hb_item = self.hb_items[notebook]
        del(self.sb_items[notebook])
        del(self.hb_items[notebook])
        self.add_change_code('removed_open_notebook_item', (sb_item, hb_item))

    def activate_item_by_notebook(self, notebook, notify=True):
        sb_item = self.sb_items[notebook]
        hb_item = self.hb_items[notebook]
        self.add_change_code('new_active_open_notebook_item', (sb_item, hb_item))


