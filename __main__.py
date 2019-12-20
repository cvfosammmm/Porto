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

import sys

import workspace.workspace_viewgtk as view
from workspace.workspace import Workspace
from app.service_locator import ServiceLocator


class MainApplicationController(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        
    def do_activate(self):
        ''' Everything starts here. '''
        
        # load settings
        self.settings = ServiceLocator.get_settings()
        
        # init view
        self.main_window = view.MainWindow(self)
        ServiceLocator.init_main_window(self.main_window)
        self.main_window.set_default_size(self.settings.get_value('window_state', 'width'), 
                                          self.settings.get_value('window_state', 'height'))
        if self.settings.get_value('window_state', 'is_maximized'): self.main_window.maximize()
        else: self.main_window.unmaximize()
        if self.settings.get_value('window_state', 'is_fullscreen'): self.main_window.fullscreen()
        else: self.main_window.unfullscreen()
        self.main_window.show_all()

        self.workspace = Workspace()
        ServiceLocator.init_dialogs(self.main_window, self.workspace)

        # controllers
        self.main_window.quit_action.connect('activate', self.on_quit_action)

        # watch changes in view
        self.observe_main_window()

    def observe_main_window(self):
        self.main_window.connect('size-allocate', self.on_window_size_allocate)
        self.main_window.connect('window-state-event', self.on_window_state_event)
        self.main_window.connect('delete-event', self.on_window_close)
    
    def on_window_size_allocate(self, main_window, window_size):
        ''' signal handler, update window size variables '''
        
        if not(main_window.is_maximized) and not(main_window.is_fullscreen):
            main_window.current_width, main_window.current_height = main_window.get_size()
            main_window.set_default_size(main_window.current_width, main_window.current_height)

    def on_window_state_event(self, main_window, state_event):
        ''' signal handler, update window state variables '''
    
        main_window.is_maximized = not((state_event.new_window_state & Gdk.WindowState.MAXIMIZED) == 0)
        main_window.is_fullscreen = not((state_event.new_window_state & Gdk.WindowState.FULLSCREEN) == 0)
        return False
        
    def save_window_state(self):
        main_window = self.main_window
        self.settings.set_value('window_state', 'width', main_window.current_width)
        self.settings.set_value('window_state', 'height', main_window.current_height)
        self.settings.set_value('window_state', 'is_maximized', main_window.is_maximized)
        self.settings.set_value('window_state', 'is_fullscreen', main_window.is_fullscreen)
        self.settings.set_value('window_state', 'sidebar_visible', self.workspace.show_sidebar)
        self.settings.set_value('window_state', 'paned_position', self.workspace.sidebar_position)
        self.settings.pickle()
        
    def on_window_close(self, window=None, parameter=None):
        self.save_quit()
        return True

    def on_quit_action(self, action=None, parameter=None):
        self.save_quit()

    def save_quit(self, accel_group=None, window=None, key=None, mask=None):
        ''' signal handler, ask user to save unsaved worksheets or discard changes '''
        
        worksheets = self.workspace.get_unsaved_worksheets()
        active_worksheet = self.workspace.get_active_worksheet()

        if len(worksheets) == 0 or active_worksheet == None or ServiceLocator.get_dialog('close_confirmation').run(worksheets)['all_save_to_close']: 
            self.save_window_state()
            self.quit()

    def do_startup(self):
        Gtk.Application.do_startup(self)


main_controller = MainApplicationController()
exit_status = main_controller.run(sys.argv)
sys.exit(exit_status)
