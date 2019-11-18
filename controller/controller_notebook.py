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
from gi.repository import Gtk
from gi.repository import GLib

import os.path

import model.model_worksheet as model_worksheet
import viewgtk.viewgtk_worksheet as viewgtk_worksheet
import controller.controller_worksheet as worksheetcontroller
from app.service_locator import ServiceLocator


class NotebookController(object):

    def __init__(self, notebook, main_window, main_controller):
        self.settings = ServiceLocator.get_settings()
        self.notebook = notebook
        self.main_window = main_window
        self.main_controller = main_controller

        self.notebook.set_pretty_print(self.main_controller.settings.get_value('preferences', 'pretty_print'))

        self.window_mode = None
        self.activate_welcome_page_mode()

        # observe worksheet
        self.settings.register_observer(self)
        self.notebook.register_observer(self)
        self.notebook.register_observer(self.main_controller.backend_controller_code)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_worksheet':
            worksheet = parameter

            self.activate_worksheet_mode()

            # add worksheet view
            worksheet_view = viewgtk_worksheet.WorksheetView()
            self.main_window.worksheet_views[worksheet] = worksheet_view

            # observe changes in this worksheet
            self.main_controller.worksheet_controllers[worksheet] = worksheetcontroller.WorksheetController(worksheet, worksheet_view, self.main_controller)
            
        if change_code == 'worksheet_removed':
            worksheet = parameter
            worksheet_view = self.main_window.worksheet_views[worksheet]
            self.remove_view(worksheet_view)
            del(self.main_window.worksheet_views[worksheet])
            self.main_controller.worksheet_controllers[worksheet].destruct()
            del(self.main_controller.worksheet_controllers[worksheet])
            if self.notebook.get_active_worksheet() == None:
                self.activate_welcome_page_mode()

        if change_code == 'changed_active_worksheet':
            worksheet = parameter

            if worksheet != None:
                self.activate_worksheet_mode()

                # change title, subtitle in headerbar
                self.main_controller.update_title(worksheet)
                self.main_controller.update_subtitle(worksheet)
                self.main_controller.update_save_button()
                self.main_controller.update_hamburger_menu()
                self.main_window.change_kernel_action.set_state(GLib.Variant.new_string(worksheet.get_kernelname()))

                # change worksheet_view
                self.main_window.active_worksheet_view = self.main_window.worksheet_views[worksheet]
                self.set_worksheet_view(self.main_window.active_worksheet_view)
                if worksheet.get_active_cell() != None: worksheet.set_active_cell(worksheet.get_active_cell())
                self.main_controller.update_stop_button()

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'pretty_print'):
                self.notebook.set_pretty_print(self.settings.get_value('preferences', 'pretty_print'))

    def close_worksheet(self, worksheet, add_to_recently_opened=True):
        self.notebook.remove_worksheet(worksheet)
        self.notebook.recently_opened_worksheets.remove_worksheet_by_pathname(worksheet.pathname)
        if add_to_recently_opened:
            pathname = worksheet.get_pathname()
            kernelname = worksheet.get_kernelname()
            if os.path.isfile(pathname):
                item = {'pathname': pathname, 'kernelname': kernelname, 'date': worksheet.get_last_saved()}
                self.notebook.recently_opened_worksheets.add_item(item, notify=True, save=True)        

    def close_worksheet_after_modified_check(self, worksheet):
        if worksheet.get_save_state() != 'modified' or ServiceLocator.get_dialog('close_confirmation').run([worksheet])['all_save_to_close']:
            self.close_worksheet(worksheet)

    def close_all_worksheets_after_modified_check(self):
        worksheets = self.notebook.get_unsaved_worksheets()
        active_worksheet = self.notebook.get_active_worksheet()

        if len(worksheets) == 0 or active_worksheet == None or ServiceLocator.get_dialog('close_confirmation').run(worksheets)['all_save_to_close']: 
            for worksheet in list(self.notebook.open_worksheets.values()):
                self.close_worksheet(worksheet)

    def delete_worksheet(self, worksheet):
        if ServiceLocator.get_dialog('delete_worksheet').run(worksheet):
            self.close_worksheet(worksheet, add_to_recently_opened=False)
            worksheet.remove_from_disk()

    def create_worksheet(self, pathname, kernelname):
        self.notebook.recently_opened_worksheets.remove_worksheet_by_pathname(pathname)
        self.notebook.remove_worksheet_by_pathname(pathname)

        worksheet = model_worksheet.NormalWorksheet(pathname)
        worksheet.set_kernelname(kernelname)
        worksheet.save_to_disk()
        self.main_controller.activate_worksheet(worksheet)
        worksheet.create_cell(0, '', activate=True)
        worksheet.save_to_disk()

    def set_worksheet_view(self, worksheet_view):
        wswrapper = self.main_window.worksheet_view_wrapper
        page_index = wswrapper.page_num(worksheet_view)
        if page_index == -1:
            page_index = wswrapper.append_page(worksheet_view)
        worksheet_view.show_all()
        wswrapper.set_current_page(page_index)
        wswrapper.show_all()
        
    def remove_view(self, view):
        wswrapper = self.main_window.worksheet_view_wrapper
        page_index = wswrapper.page_num(view)
        if page_index >= 0:
            wswrapper.remove_page(page_index)
        
    def activate_worksheet_mode(self):
        if self.window_mode != 'worksheet':
            self.window_mode = 'worksheet'
            hb_right = self.main_window.headerbar.hb_right
            hb_right.show_buttons()

    def activate_welcome_page_mode(self):
        if self.window_mode != 'welcome_page':
            self.window_mode = 'welcome_page'
            self.main_window.headerbar.set_title('Welcome to Porto')
            self.main_window.headerbar.set_subtitle('')
            hb_right = self.main_window.headerbar.hb_right
            hb_right.hide_buttons()
            self.set_worksheet_view(self.main_window.welcome_page_view)


