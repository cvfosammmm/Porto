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
from gi.repository import GLib

from app.service_locator import ServiceLocator
import worksheet.worksheet as model_worksheet

import os.path


class WorkspaceController(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.settings = ServiceLocator.get_settings()

        self.main_window.toggle_sidebar_action.connect('activate', self.toggle_sidebar)
        self.main_window.preferences_action.connect('activate', self.show_preferences_dialog)
        self.main_window.show_about_dialog_action.connect('activate', self.show_about_dialog)
        self.main_window.show_shortcuts_window_action.connect('activate', self.show_shortcuts_window)
        self.main_window.sidebar.connect('size-allocate', self.on_sidebar_size_allocate)

        self.main_window.restart_kernel_action.connect('activate', self.on_wsmenu_restart_kernel)
        self.main_window.change_kernel_action.connect('activate', self.on_wsmenu_change_kernel)
        self.main_window.save_all_action.connect('activate', self.on_wsmenu_save_all)
        self.main_window.save_as_action.connect('activate', self.on_wsmenu_save_as)
        self.main_window.delete_ws_action.connect('activate', self.on_wsmenu_delete)
        self.main_window.close_action.connect('activate', self.on_wsmenu_close)
        self.main_window.close_all_action.connect('activate', self.on_wsmenu_close_all)

        self.main_window.welcome_page_view.create_ws_link.connect('clicked', self.on_create_ws_button_click)
        self.main_window.welcome_page_view.open_ws_link.connect('clicked', self.on_open_ws_button_click)

        self.main_window.headerbar.hb_left.open_ws_button.connect('clicked', self.on_open_ws_button_click)
        self.main_window.headerbar.hb_right.worksheet_chooser.open_button.connect('clicked', self.on_open_ws_button_click)

        self.settings.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'pretty_print'):
                self.workspace.set_pretty_print(self.settings.get_value('preferences', 'pretty_print'))

    def on_sidebar_size_allocate(self, paned, paned_size):
        self.workspace.sidebar_position = self.main_window.paned.get_position()
            
    def on_open_ws_button_click(self, button_object=None):
        filename = ServiceLocator.get_dialog('open_worksheet').run()
        if filename != None:
            if filename.split('.')[-1] == 'ipynb':
                worksheet = model_worksheet.Worksheet(filename)
                self.workspace.activate_worksheet(worksheet)

    def on_create_ws_button_click(self, button_object=None):
        parameters = ServiceLocator.get_dialog('create_worksheet').run()
        if parameters != None:
            pathname, kernelname = parameters
            self.workspace.create_worksheet(pathname, kernelname)

    def on_wsmenu_restart_kernel(self, action=None, parameter=None):
        if self.workspace.active_worksheet != None:
            self.workspace.active_worksheet.restart_kernel()
        
    def on_wsmenu_change_kernel(self, action=None, parameter=None):
        if parameter != None:
            self.main_window.change_kernel_action.set_state(parameter)
            worksheet = self.workspace.active_worksheet
            if worksheet.get_kernelname() != parameter.get_string():
                worksheet.set_kernelname(parameter.get_string())
                worksheet.restart_kernel()

    def on_wsmenu_save_as(self, action=None, parameter=None):
        worksheet = self.workspace.get_active_worksheet()
        if worksheet != None:
            ServiceLocator.get_dialog('save_as').run(worksheet)

    def on_wsmenu_save_all(self, action=None, parameter=None):
        for worksheet in self.workspace.open_worksheets:
            worksheet.save_to_disk()

    def on_wsmenu_delete(self, action, parameter=None):
        self.delete_worksheet(self.workspace.get_active_worksheet())

    def on_wsmenu_close(self, action=None, parameter=None):
        worksheet = self.workspace.get_active_worksheet()
        if worksheet != None:
            self.close_worksheet_after_modified_check(worksheet)

    def on_wsmenu_close_all(self, action=None, parameter=None):
        self.close_all_worksheets_after_modified_check()

    def close_worksheet(self, worksheet, add_to_recently_opened=True):
        self.workspace.remove_worksheet(worksheet)
        self.workspace.recently_opened_worksheets.remove_worksheet_by_pathname(worksheet.pathname)
        if add_to_recently_opened:
            pathname = worksheet.get_pathname()
            kernelname = worksheet.get_kernelname()
            if os.path.isfile(pathname):
                item = {'pathname': pathname, 'kernelname': kernelname, 'date': worksheet.get_last_saved()}
                self.workspace.recently_opened_worksheets.add_item(item, notify=True, save=True)        

    def close_worksheet_after_modified_check(self, worksheet):
        if worksheet.get_save_state() != 'modified' or ServiceLocator.get_dialog('close_confirmation').run([worksheet])['all_save_to_close']:
            self.close_worksheet(worksheet)

    def close_all_worksheets_after_modified_check(self):
        worksheets = self.workspace.get_unsaved_worksheets()
        active_worksheet = self.workspace.get_active_worksheet()

        if len(worksheets) == 0 or active_worksheet == None or ServiceLocator.get_dialog('close_confirmation').run(worksheets)['all_save_to_close']: 
            for worksheet in list(self.workspace.open_worksheets.values()):
                self.close_worksheet(worksheet)

    def toggle_sidebar(self, action, parameter=None):
        show_sidebar = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(show_sidebar))
        self.workspace.set_show_sidebar(show_sidebar)

    def show_shortcuts_window(self, action, parameter=''):
        ServiceLocator.get_dialog('keyboard_shortcuts').run()

    def show_preferences_dialog(self, action=None, parameter=''):
        ServiceLocator.get_dialog('preferences').run()

    def show_about_dialog(self, action, parameter=''):
        ServiceLocator.get_dialog('about').run()

    def delete_worksheet(self, worksheet):
        if ServiceLocator.get_dialog('delete_worksheet').run(worksheet):
            self.close_worksheet(worksheet, add_to_recently_opened=False)
            worksheet.remove_from_disk()


