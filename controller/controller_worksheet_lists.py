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

import model.model_worksheet as model_worksheet
import viewgtk.viewgtk_sidebar as viewgtk_sidebar
import viewgtk.viewgtk_worksheet_list as viewgtk_worksheet_list


class WSListsController(object):

    def __init__(self, sidebar, hbchooser, main_controller):

        self.sidebar = sidebar
        self.hbchooser = hbchooser
        self.main_controller = main_controller
        self.recently_opened_worksheets = self.main_controller.notebook.recently_opened_worksheets
        self.open_ws_should_scroll = False
        self.open_ws_hb_should_scroll = False
        self.hbchooser.open_worksheets_list_view_wrapper.hide()

        self.sidebar.connect('size-allocate', self.on_open_ws_view_size_allocate)
        self.on_open_ws_hb_view_size_allocate()
        for widget in [self.sidebar, self.hbchooser]:
            widget.recent_worksheets_list_view.set_sort_func(self.sort_func)
            widget.recent_worksheets_list_view.connect('row-activated', self.on_recent_worksheets_list_click)
            widget.open_worksheets_list_view.connect('row-selected', self.on_open_worksheets_list_selected)

        self.recently_opened_worksheets.register_observer(self)
        self.main_controller.notebook.register_observer(self)
        self.recently_opened_worksheets.populate_from_disk()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_worksheet':
            worksheet = parameter

            for widget in [self.sidebar, self.hbchooser]:
                wslist_item = viewgtk_worksheet_list.OpenWorksheetListViewItem(worksheet, worksheet.get_last_saved())
                icon_normal = self.main_controller.kernelspecs.get_normal_sidebar_icon(worksheet.get_kernelname())
                icon_active = self.main_controller.kernelspecs.get_active_sidebar_icon(worksheet.get_kernelname())
                wslist_item.update_kernel_icons(icon_normal, icon_active)
                widget.open_worksheets_list_view.add_item(wslist_item)
                self.on_open_ws_view_size_allocate()
                self.on_open_ws_hb_view_size_allocate()
                wslist_item.close_button.connect('clicked', self.on_close_button_clicked, worksheet)
                widget.open_worksheets_label_revealer.set_reveal_child(True)
                widget.open_worksheets_list_view_wrapper.show_all()
                widget.recent_worksheets_list_view.hide_item_by_pathname(worksheet.pathname)
                if widget.recent_worksheets_list_view.visible_items_count < 1:
                    widget.recent_worksheets_label_revealer.set_reveal_child(False)
                    widget.recent_worksheets_list_view_wrapper.hide()
            self.main_controller.main_window.headerbar.hb_right.increment_worksheets_number()

        if change_code == 'worksheet_removed':
            worksheet = parameter

            for widget in [self.sidebar, self.hbchooser]:
                if worksheet == self.main_controller.notebook.get_active_worksheet():
                    row_index = widget.open_worksheets_list_view.get_row_index_by_worksheet(worksheet)
                    row = widget.open_worksheets_list_view.get_row_at_index(row_index + 1)
                    if row != None:
                        widget.open_worksheets_list_view.select_row(row)
                    else:
                        row = widget.open_worksheets_list_view.get_row_at_index(row_index - 1)
                        if row != None:
                            widget.open_worksheets_list_view.select_row(row)
                widget.open_worksheets_list_view.remove_item_by_worksheet(worksheet)
                self.on_open_ws_view_size_allocate()
                self.on_open_ws_hb_view_size_allocate()

                if widget.open_worksheets_list_view.visible_items_count < 1:
                    self.main_controller.activate_welcome_page_mode()
                    widget.open_worksheets_list_view_wrapper.hide()
                    widget.open_worksheets_label_revealer.set_reveal_child(False)

                widget.recent_worksheets_list_view.show_item_by_pathname(worksheet.pathname)
                if widget.recent_worksheets_list_view.visible_items_count >= 1:
                    widget.recent_worksheets_list_view_wrapper.show_all()
                    widget.recent_worksheets_label_revealer.set_reveal_child(True)
            self.main_controller.main_window.headerbar.hb_right.decrement_worksheets_number()

        if change_code == 'add_recently_opened_worksheet':
            item = parameter

            for widget in [self.sidebar, self.hbchooser]:
                wslist_item = viewgtk_worksheet_list.RecentWorksheetListViewItem(item['pathname'], item['kernelname'], item['date'])
                icon_normal = self.main_controller.kernelspecs.get_normal_sidebar_icon(item['kernelname'])
                icon_active = self.main_controller.kernelspecs.get_active_sidebar_icon(item['kernelname'])
                wslist_item.update_kernel_icons(icon_normal, icon_active)
                widget.recent_worksheets_list_view.add_item(wslist_item)
                if self.main_controller.notebook.get_worksheet_by_pathname(item['pathname']) != None:
                    widget.recent_worksheets_list_view.hide_item_by_pathname(item['pathname'])
                if widget.recent_worksheets_list_view.visible_items_count >= 1:
                    widget.recent_worksheets_label_revealer.set_reveal_child(True)
                    widget.recent_worksheets_list_view_wrapper.show_all()

        if change_code == 'remove_recently_opened_worksheet':
            item = parameter

            for widget in [self.sidebar, self.hbchooser]:
                widget.recent_worksheets_list_view.remove_item_by_pathname(item['pathname'])
                if widget.recent_worksheets_list_view.visible_items_count < 1:
                    widget.recent_worksheets_label_revealer.set_reveal_child(False)
                    widget.recent_worksheets_list_view_wrapper.hide()

    def on_recent_worksheets_list_click(self, wslist_view, wslist_item_view):
        if wslist_item_view != None:
            for widget in [self.sidebar, self.hbchooser]:
                widget.open_worksheets_list_view.unselect_all()
            pathname = wslist_item_view.pathname
            self.main_controller.activate_worksheet_by_pathname(pathname)
            self.hbchooser.popdown()

    def on_open_worksheets_list_selected(self, wslist_view, wslist_item_view):
        if wslist_item_view != None:
            worksheet = wslist_item_view.get_worksheet()
            self.main_controller.activate_worksheet(worksheet)
            for widget in [self.sidebar, self.hbchooser]:
                if widget.open_worksheets_list_view.selected_row != None:
                    widget.open_worksheets_list_view.selected_row.set_icon_type('normal')
                widget.open_worksheets_list_view.selected_row = wslist_item_view
            wslist_item_view.set_icon_type('active')
            self.hbchooser.popdown()

    def select_row_by_worksheet(self, worksheet):
        for widget in [self.sidebar, self.hbchooser]:
            row_index = widget.open_worksheets_list_view.get_row_index_by_worksheet(worksheet)
            row = widget.open_worksheets_list_view.get_row_at_index(row_index)
            widget.open_worksheets_list_view.select_row(row)
            self.scroll_row_on_screen(row)

    def scroll_row_on_screen(self, row):
        for widget in [self.sidebar, self.hbchooser]:
            sw = widget.open_worksheets_list_view_wrapper
            item_offset = 48 * (row.get_index() - 1)
            viewport_offset = sw.get_vadjustment().get_value()
            viewport_height = sw.get_allocated_height()
            if item_offset < viewport_offset:
                sw.get_vadjustment().set_value(item_offset)
            elif item_offset > (viewport_offset + viewport_height - 48):
                sw.get_vadjustment().set_value(item_offset + viewport_height - 48)

    def update_save_date(self, worksheet):
        if isinstance(worksheet, model_worksheet.NormalWorksheet):
            for widget in [self.sidebar, self.hbchooser]:
                item = widget.recent_worksheets_list_view.get_item_by_pathname(worksheet.pathname)
                item.set_last_save(worksheet.get_last_saved())

    def on_close_button_clicked(self, button, worksheet):
        self.main_controller.notebook_controller.close_worksheet_after_modified_check(worksheet)

    def on_open_ws_view_size_allocate(self, widget=None, allocation=None):
        sw = self.sidebar.open_worksheets_list_view_wrapper
        open_ws_height = 48 * self.sidebar.open_worksheets_list_view.visible_items_count
        self_height = self.sidebar.get_allocated_height()
        open_ws_should_scroll = (open_ws_height + 33) >= self_height / 2
        if open_ws_should_scroll != self.open_ws_should_scroll:
            self.open_ws_should_scroll = open_ws_should_scroll
        if self.open_ws_should_scroll:
            sw.set_size_request(-1, self_height / 2 - ((self_height / 2) % 48))
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        else:
            sw.set_size_request(-1, -1)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

    def on_open_ws_hb_view_size_allocate(self, widget=None, allocation=None):
        sw = self.hbchooser.open_worksheets_list_view_wrapper
        open_ws_height = 49 * self.hbchooser.open_worksheets_list_view.visible_items_count
        self_height = 500
        open_ws_hb_should_scroll = (open_ws_height >= 196)
        if open_ws_hb_should_scroll != self.open_ws_hb_should_scroll:
            self.open_ws_hb_should_scroll = open_ws_hb_should_scroll
        if self.open_ws_hb_should_scroll:
            sw.set_size_request(-1, 198)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        else:
            sw.set_size_request(-1, -1)
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

    def sort_func(self, row1, row2):
        if row1.last_saved > row2.last_saved: return -1
        elif row1.last_saved < row2.last_saved: return 1
        else: return 0


