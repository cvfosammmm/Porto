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
import workspace.open_worksheets_list.open_worksheets_list_viewgtk as ows_view
import workspace.open_worksheets_list.open_worksheets_list_presenter as ows_presenter
import workspace.open_worksheets_list.open_worksheets_list_controller as ows_controller


class OpenWorksheetsList(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace

        self.sb_items = dict()
        self.hb_items = dict()

        self.sb_view = ows_view.OpenWorksheetsListView()
        self.hb_view = ows_view.OpenWorksheetsListView()
        self.presenter = ows_presenter.OpenWorksheetsListPresenter(workspace, self, self.sb_view, self.hb_view)
        self.controller = ows_controller.OpenWorksheetsListController(workspace, self.sb_view, self.hb_view)

    def add_item_by_worksheet(self, worksheet, notify=True):
        sb_item = worksheet.list_item.sb_view
        hb_item = worksheet.list_item.hb_view
        self.sb_items[worksheet] = sb_item
        self.hb_items[worksheet] = hb_item
        if notify:
            self.add_change_code('new_open_worksheet_item', (sb_item, hb_item))

    def remove_item_by_worksheet(self, worksheet, notify=True):
        sb_item = self.sb_items[worksheet]
        hb_item = self.hb_items[worksheet]
        del(self.sb_items[worksheet])
        del(self.hb_items[worksheet])
        self.add_change_code('removed_open_worksheet_item', (sb_item, hb_item))

    def activate_item_by_worksheet(self, worksheet, notify=True):
        sb_item = self.sb_items[worksheet]
        hb_item = self.hb_items[worksheet]
        self.add_change_code('new_active_open_worksheet_item', (sb_item, hb_item))


