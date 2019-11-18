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


class WorkspaceController(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()

        self.main_window.toggle_sidebar_action.connect('activate', self.toggle_sidebar)
        self.main_window.preferences_action.connect('activate', self.show_preferences_dialog)
        self.main_window.show_about_dialog_action.connect('activate', self.show_about_dialog)
        self.main_window.show_shortcuts_window_action.connect('activate', self.show_shortcuts_window)
        self.main_window.sidebar.connect('size-allocate', self.on_sidebar_size_allocate)

    def on_sidebar_size_allocate(self, paned, paned_size):
        self.workspace.sidebar_position = self.main_window.paned.get_position()
            
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


