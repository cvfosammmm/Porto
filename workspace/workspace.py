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

import workspace.workspace_presenter as workspace_presenter
import workspace.workspace_controller as workspace_controller
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class Workspace(Observable):

    def __init__(self):
        Observable.__init__(self)

        settings = ServiceLocator.get_settings()
        self.show_sidebar = settings.get_value('window_state', 'sidebar_visible')
        self.sidebar_position = settings.get_value('window_state', 'paned_position')
        self.presenter = workspace_presenter.WorkspacePresenter(self)
        self.controller = workspace_controller.WorkspaceController(self)

    def set_show_sidebar(self, value):
        self.show_sidebar = value
        self.add_change_code('sidebar_state', value)


