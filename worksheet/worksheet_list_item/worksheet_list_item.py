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

import worksheet.worksheet_list_item.worksheet_list_item_controller as wsli_controller
import worksheet.worksheet_list_item.worksheet_list_item_presenter as wsli_presenter
import worksheet.worksheet_list_item.worksheet_list_item_viewgtk as wsli_view
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class WorksheetListItem(Observable):

    def __init__(self, worksheet):
        Observable.__init__(self)
        self.worksheet = worksheet
        self.kernelspecs = ServiceLocator.get_kernelspecs()

        self.sb_view = wsli_view.OpenWorksheetListViewItem(worksheet, worksheet.get_last_saved())
        self.hb_view = wsli_view.OpenWorksheetListViewItem(worksheet, worksheet.get_last_saved())
        self.presenter = wsli_presenter.WorksheetListItemPresenter(worksheet, self, self.sb_view, self.hb_view)
        self.controller = wsli_controller.WorksheetListItemController(worksheet, self, self.sb_view, self.hb_view)

        self.set_kernel(worksheet.get_kernelname())

    def set_kernel(self, kernelname):
        self.sb_icon_normal = self.kernelspecs.get_normal_sidebar_icon(kernelname)
        self.sb_icon_active = self.kernelspecs.get_active_sidebar_icon(kernelname)
        self.hb_icon_normal = self.kernelspecs.get_normal_sidebar_icon(kernelname)
        self.hb_icon_active = self.kernelspecs.get_active_sidebar_icon(kernelname)
        self.add_change_code('icon_changed')


