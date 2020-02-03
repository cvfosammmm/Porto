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

import workspace.recently_opened_notebooks_list.recently_opened_notebooks_list_viewgtk as viewgtk_notebook_list
from app.service_locator import ServiceLocator


class RecentlyOpenedNotebooksListPresenter(object):

    def __init__(self, workspace, recently_opened_notebooks):
        self.sidebar = ServiceLocator.get_main_window().sidebar
        self.hbchooser = ServiceLocator.get_main_window().headerbar.hb_right.notebook_chooser
        self.kernelspecs = ServiceLocator.get_kernelspecs()
        self.workspace = workspace
        self.recently_opened_notebooks = recently_opened_notebooks
        self.recently_opened_notebooks.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'add_recently_opened_notebook':
            item = parameter

            for widget in [self.sidebar, self.hbchooser]:
                icon_normal = self.kernelspecs.get_normal_sidebar_icon(item['kernelname'])
                icon_active = self.kernelspecs.get_active_sidebar_icon(item['kernelname'])
                widget.recent_notebooks_list_view.add_item(item['pathname'], item['kernelname'], item['date'], icon_normal, icon_active)
                if widget.recent_notebooks_list_view.visible_items_count >= 1:
                    widget.recent_notebooks_label_revealer.set_reveal_child(True)
                    widget.recent_notebooks_list_view_wrapper.show_all()

        if change_code == 'remove_recently_opened_notebook':
            item = parameter

            for widget in [self.sidebar, self.hbchooser]:
                widget.recent_notebooks_list_view.remove_item_by_pathname(item['pathname'])
                if widget.recent_notebooks_list_view.visible_items_count < 1:
                    widget.recent_notebooks_label_revealer.set_reveal_child(False)
                    widget.recent_notebooks_list_view_wrapper.hide()


