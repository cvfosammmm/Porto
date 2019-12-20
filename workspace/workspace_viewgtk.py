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
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib

import os, os.path

import workspace.welcome_page.welcome_page_viewgtk as viewgtk_welcome_page
import workspace.headerbar.headerbar_viewgtk as viewgtk_headerbars
import workspace.sidebar.sidebar_viewgtk as viewgtk_sidebar


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.app = app
        self.set_size_request(1000, 550)
        Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.dirname(__file__) + '/../resources/icons')
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        
        # window state variables
        self.current_width, self.current_height = self.get_size()
        self.is_maximized = False
        self.is_fullscreen = False

        # headerbar
        self.headerbar = viewgtk_headerbars.HeaderBar(app.settings.button_layout)
        self.set_titlebar(self.headerbar)

        # window content
        self.sidebar = viewgtk_sidebar.Sidebar()
        self.welcome_page_view = viewgtk_welcome_page.WelcomePageView()
        self.worksheet_view_wrapper = Gtk.Notebook()
        self.worksheet_view_wrapper.append_page(self.welcome_page_view)
        self.worksheet_view_wrapper.set_show_border(False)
        self.worksheet_view_wrapper.set_show_tabs(False)
        self.worksheet_view_wrapper.set_size_request(763, -1)

        self.paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.paned.pack1(self.sidebar, False, False)
        self.paned.pack2(self.worksheet_view_wrapper, True, False)
        self.paned.set_position(250)
        self.add(self.paned)

        # sync paneds
        self.paned.bind_property('position', self.headerbar, 'position', 1)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_path(os.getcwd() + '/resources/style_gtk.css')
        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(self.get_screen(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # actions
        self.restart_kernel_action = Gio.SimpleAction.new('restart_kernel', None)
        self.add_action(self.restart_kernel_action)
        default = GLib.Variant.new_string('python3')
        self.change_kernel_action = Gio.SimpleAction.new_stateful('change_kernel', GLib.VariantType('s'), default)
        self.add_action(self.change_kernel_action)
        self.delete_ws_action = Gio.SimpleAction.new('delete_worksheet', None)
        self.add_action(self.delete_ws_action)
        self.save_as_action = Gio.SimpleAction.new('save_as', None)
        self.add_action(self.save_as_action)
        self.save_all_action = Gio.SimpleAction.new('save_all', None)
        self.add_action(self.save_all_action)
        self.close_action = Gio.SimpleAction.new('close_worksheet', None)
        self.add_action(self.close_action)
        self.close_all_action = Gio.SimpleAction.new('close_all_worksheets', None)
        self.add_action(self.close_all_action)
        sv_default = GLib.Variant.new_boolean(app.settings.get_value('window_state', 'sidebar_visible'))
        self.toggle_sidebar_action = Gio.SimpleAction.new_stateful('toggle-sidebar', None, sv_default)
        self.add_action(self.toggle_sidebar_action)
        self.preferences_action = Gio.SimpleAction.new('show_preferences_dialog', None)
        self.add_action(self.preferences_action)
        self.quit_action = Gio.SimpleAction.new('quit', None)
        self.add_action(self.quit_action)
        self.show_about_dialog_action = Gio.SimpleAction.new('show_about_dialog', None)
        self.add_action(self.show_about_dialog_action)
        self.show_shortcuts_window_action = Gio.SimpleAction.new('show_shortcuts_window', None)
        self.add_action(self.show_shortcuts_window_action)


