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
import workspace.recently_opened_worksheets_list.recently_opened_worksheets_list as ro_worksheets_list
import workspace.open_worksheets_list.open_worksheets_list as open_worksheets_list
import worksheet.worksheet as model_worksheet
import workspace.headerbar.headerbar as headerbar_model
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class Workspace(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.recently_opened_worksheets = ro_worksheets_list.RecentlyOpenedWorksheetsList(self)
        self.open_worksheets_list = open_worksheets_list.OpenWorksheetsList(self)
        self.open_worksheets = dict()
        self.active_worksheet = None

        self.settings = ServiceLocator.get_settings()
        self.show_sidebar = self.settings.get_value('window_state', 'sidebar_visible')
        self.sidebar_position = self.settings.get_value('window_state', 'paned_position')
        self.presenter = workspace_presenter.WorkspacePresenter(self)
        self.controller = workspace_controller.WorkspaceController(self)
        self.headerbar = headerbar_model.Headerbar(self)
        self.set_pretty_print(self.settings.get_value('preferences', 'pretty_print'))

    def add_worksheet(self, worksheet):
        if worksheet in self.open_worksheets: return False
        self.open_worksheets[worksheet] = worksheet
        self.open_worksheets_list.add_item_by_worksheet(worksheet)
        item = {'pathname': worksheet.pathname, 'kernelname': worksheet.kernelname, 'date': worksheet.get_last_saved()}
        self.recently_opened_worksheets.add_item(item)
        self.add_change_code('new_worksheet', worksheet)

    def create_worksheet(self, pathname, kernelname):
        self.recently_opened_worksheets.remove_worksheet_by_pathname(pathname)
        self.remove_worksheet_by_pathname(pathname)

        worksheet = model_worksheet.Worksheet(pathname)
        worksheet.set_kernelname(kernelname)
        worksheet.save_to_disk()
        self.activate_worksheet(worksheet)
        worksheet.create_cell(0, '', activate=True)
        worksheet.save_to_disk()

    def activate_worksheet(self, worksheet):
        if not worksheet in self.open_worksheets:
            self.add_worksheet(worksheet)
            worksheet.load_from_disk()
        self.set_active_worksheet(worksheet)

    def activate_worksheet_by_pathname(self, pathname):
        for worksheet in self.open_worksheets:
            if worksheet.pathname == pathname:
                self.set_active_worksheet(worksheet)
                return
        worksheet = model_worksheet.Worksheet(pathname)
        try:
            worksheet.load_from_disk()
        except FileNotFoundError:
            self.recently_opened_worksheets.remove_worksheet_by_pathname(pathname)
        else:
            self.add_worksheet(worksheet)
            self.set_active_worksheet(worksheet)

    def set_active_worksheet(self, worksheet):
        if worksheet != self.active_worksheet:
            self.active_worksheet = worksheet
            self.add_change_code('changed_active_worksheet', worksheet)
            if worksheet != None:
                self.open_worksheets_list.activate_item_by_worksheet(worksheet)
        
    def get_active_worksheet(self):
        return self.active_worksheet
        
    def get_unsaved_worksheets(self):
        ''' return worksheets with unsaved changes '''
        
        matching_worksheets = list()
        for worksheet in self.open_worksheets.values():
            if worksheet.get_save_state() == 'modified':
                matching_worksheets.append(worksheet)
        return matching_worksheets

    def get_worksheet_by_pathname(self, pathname):
        for worksheet in self.open_worksheets.values():
            if worksheet.pathname == pathname:
                return worksheet
        return None

    def remove_worksheet(self, worksheet):
        try: worksheet = self.open_worksheets[worksheet]
        except KeyError: pass
        else:
            worksheet.shutdown_kernel()
            self.open_worksheets_list.remove_item_by_worksheet(worksheet)
            del(self.open_worksheets[worksheet])
            if len(self.open_worksheets) < 1:
                self.set_active_worksheet(None)
            elif self.get_active_worksheet() == worksheet:
                new_active = False
                def sort_func(ws): return ws.last_saved
                for ws in sorted(self.open_worksheets, key=sort_func, reverse=True):
                    if ws.last_saved <= worksheet.last_saved:
                        self.set_active_worksheet(ws)
                        new_active = True
                        break
                if new_active == False:
                    for ws in sorted(self.open_worksheets, key=sort_func, reverse=False):
                        self.set_active_worksheet(ws)
                        break
            self.add_change_code('worksheet_removed', worksheet)
        
    def remove_worksheet_by_pathname(self, pathname):
        worksheet = self.get_worksheet_by_pathname(pathname)
        if worksheet != None:
            self.remove_worksheet(worksheet)

    def set_show_sidebar(self, value):
        self.show_sidebar = value
        self.add_change_code('sidebar_state', value)

    def set_pretty_print(self, value):
        self.add_change_code('set_pretty_print', value)


