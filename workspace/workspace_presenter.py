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

from helpers.observable import Observable
from app.service_locator import ServiceLocator


class WorkspacePresenter(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.main_window.paned.set_position(self.workspace.sidebar_position)
        if self.workspace.show_sidebar:
            self.on_show_sidebar()
        else:
            self.on_hide_sidebar()

        self.workspace.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'sidebar_state':
            if parameter == True:
                self.on_show_sidebar()
            else:
                self.on_hide_sidebar()

    def on_show_sidebar(self):
        self.main_window.sidebar.show_all()
        self.main_window.headerbar.hb_left.show_all()
        self.main_window.headerbar.hb_right.open_worksheets_button.hide()
        self.main_window.welcome_page_view.set_sidebar_visible(True)

    def on_hide_sidebar(self):
        self.main_window.sidebar.hide()
        self.main_window.headerbar.hb_left.hide()
        self.main_window.headerbar.hb_right.open_worksheets_button.show_all()
        self.main_window.welcome_page_view.set_sidebar_visible(False)


