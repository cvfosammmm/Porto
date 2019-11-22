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

from helpers.observable import Observable
from app.service_locator import ServiceLocator


class WorkspacePresenter(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.window_mode = None
        self.activate_welcome_page_mode()

        self.main_window.paned.set_position(self.workspace.sidebar_position)
        if self.workspace.show_sidebar:
            self.on_show_sidebar()
        else:
            self.on_hide_sidebar()

        self.workspace.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_worksheet':
            self.window_mode = 'worksheet'

        if change_code == 'worksheet_removed':
            worksheet = parameter
            self.remove_view(worksheet.view)
            del(worksheet.controller)
            if self.workspace.get_active_worksheet() == None:
                self.activate_welcome_page_mode()

        if change_code == 'changed_active_worksheet':
            worksheet = parameter

            if worksheet != None:
                self.window_mode = 'worksheet'

                kernel_changer_state = GLib.Variant.new_string(worksheet.get_kernelname())
                self.main_window.change_kernel_action.set_state(kernel_changer_state)

                # change worksheet_view
                self.main_window.active_worksheet_view = worksheet.view
                self.set_worksheet_view(worksheet.view)
                if worksheet.get_active_cell() != None: worksheet.set_active_cell(worksheet.get_active_cell())

        if change_code == 'sidebar_state':
            if parameter == True:
                self.on_show_sidebar()
            else:
                self.on_hide_sidebar()

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

    def activate_welcome_page_mode(self):
        if self.window_mode != 'welcome_page':
            self.window_mode = 'welcome_page'
            self.set_worksheet_view(self.main_window.welcome_page_view)

    def on_show_sidebar(self):
        self.main_window.sidebar.show_all()
        self.main_window.welcome_page_view.set_sidebar_visible(True)

    def on_hide_sidebar(self):
        self.main_window.sidebar.hide()
        self.main_window.welcome_page_view.set_sidebar_visible(False)


