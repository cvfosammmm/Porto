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

import notebook.notebook_list_item.notebook_list_item_controller as nbli_controller
import notebook.notebook_list_item.notebook_list_item_presenter as nbli_presenter
import notebook.notebook_list_item.notebook_list_item_viewgtk as nbli_view
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class NotebookListItem(Observable):

    def __init__(self, notebook):
        Observable.__init__(self)
        self.notebook = notebook
        self.kernelspecs = ServiceLocator.get_kernelspecs()

        self.sb_view = nbli_view.OpenNotebookListViewItem(notebook, notebook.get_last_saved())
        self.hb_view = nbli_view.OpenNotebookListViewItem(notebook, notebook.get_last_saved())
        self.presenter = nbli_presenter.NotebookListItemPresenter(notebook, self, self.sb_view, self.hb_view)
        self.controller = nbli_controller.NotebookListItemController(notebook, self, self.sb_view, self.hb_view)

        self.set_kernel(notebook.get_kernelname())

    def set_kernel(self, kernelname):
        self.sb_icon_normal = self.kernelspecs.get_normal_sidebar_icon(kernelname)
        self.sb_icon_active = self.kernelspecs.get_active_sidebar_icon(kernelname)
        self.hb_icon_normal = self.kernelspecs.get_normal_sidebar_icon(kernelname)
        self.hb_icon_active = self.kernelspecs.get_active_sidebar_icon(kernelname)
        self.add_change_code('icon_changed')


