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

import os.path

import model.model_recently_opened as model_recently_opened
from helpers.observable import Observable


class Notebook(Observable):
    ''' A notebook contains a user's worksheets. '''

    def __init__(self):
        Observable.__init__(self)

        self.recently_opened_worksheets = model_recently_opened.RecentlyOpenedWorksheets()
        self.open_worksheets = dict()
        self.active_worksheet = None
        self.documentation_worksheets = dict()
        
    def add_worksheet(self, worksheet):
        if worksheet in self.open_worksheets: return False
        self.open_worksheets[worksheet] = worksheet
        item = {'pathname': worksheet.pathname, 'kernelname': worksheet.kernelname, 'date': worksheet.get_last_saved()}
        self.recently_opened_worksheets.add_item(item)
        self.add_change_code('new_worksheet', worksheet)

    def add_documentation_worksheet(self, worksheet):
        self.documentation_worksheets[worksheet] = worksheet
        self.add_change_code('new_worksheet', worksheet)
    
    def set_active_worksheet(self, worksheet):
        if worksheet != self.active_worksheet:
            self.active_worksheet = worksheet
            self.add_change_code('changed_active_worksheet', worksheet)
        
    def set_pretty_print(self, value):
        self.add_change_code('set_pretty_print', value)

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
            del(self.open_worksheets[worksheet])
            if len(self.open_worksheets) < 1:
                self.set_active_worksheet(None)
            self.add_change_code('worksheet_removed', worksheet)
        
    def remove_worksheet_by_pathname(self, pathname):
        worksheet = self.get_worksheet_by_pathname(pathname)
        if worksheet != None:
            self.remove_worksheet(worksheet)
        

