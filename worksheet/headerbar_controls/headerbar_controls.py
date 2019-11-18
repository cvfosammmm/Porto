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

import worksheet.headerbar_controls.headerbar_controls_viewgtk as headerbar_controls_viewgtk
import worksheet.headerbar_controls.headerbar_controls_controller as headerbar_controls_controller


class HeaderbarControls(object):

    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.view = headerbar_controls_viewgtk.ButtonBox()
        self.controller = headerbar_controls_controller.HeaderbarControlsController(worksheet, self.view)


