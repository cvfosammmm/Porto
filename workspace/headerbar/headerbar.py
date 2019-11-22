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

import workspace.headerbar.headerbar_presenter as headerbar_presenter
import workspace.headerbar.headerbar_controller as headerbar_controller
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class Headerbar(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)

        self.workspace = workspace
        self.presenter = headerbar_presenter.HeaderbarPresenter(workspace)
        self.controller = headerbar_controller.HeaderbarController(workspace)


