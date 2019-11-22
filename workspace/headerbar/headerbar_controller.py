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


class HeaderbarController(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().headerbar
        self.view.hb_left.create_ws_button.connect('clicked', self.on_create_ws_button_click)
        self.view.hb_right.worksheet_chooser.create_button.connect('clicked', self.on_create_ws_button_click)

    def on_create_ws_button_click(self, button_object=None):
        parameters = ServiceLocator.get_dialog('create_worksheet').run()
        if parameters != None:
            pathname, kernelname = parameters
            self.workspace.create_worksheet(pathname, kernelname)


