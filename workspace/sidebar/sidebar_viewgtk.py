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

import workspace.recently_opened_worksheets_list.recently_opened_worksheets_list_viewgtk as viewgtk_worksheet_list


class Sidebar(Gtk.VBox):
    ''' As name suggests, this is the left hand sidebar. '''

    def __init__(self):
        Gtk.Paned.__init__(self)
        self.get_style_context().add_class('sidebar')
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_size_request(260, 500)
        
        self.open_worksheets_label_revealer = Gtk.Revealer()
        self.open_worksheets_label = Gtk.Label('Open Worksheets')
        self.open_worksheets_label.set_xalign(0)
        self.open_worksheets_label.get_style_context().add_class('wslist_header')
        self.open_worksheets_label_revealer.add(self.open_worksheets_label)
        self.open_worksheets_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.get_style_context().add_class('wslist_top')

        self.recent_worksheets_list_view = viewgtk_worksheet_list.WorksheetListRecentView()
        self.recent_worksheets_list_view.set_selection_mode(Gtk.SelectionMode.NONE)
        self.recent_worksheets_list_view.set_can_focus(False)
        self.recent_worksheets_label_revealer = Gtk.Revealer()
        self.recent_worksheets_label = Gtk.Label('Recently Opened Worksheets')
        self.recent_worksheets_label.set_xalign(0)
        self.recent_worksheets_label.get_style_context().add_class('wslist_header')
        self.recent_worksheets_label_revealer.add(self.recent_worksheets_label)
        self.recent_worksheets_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)

        self.open_worksheets_list_view_wrapper = Gtk.ScrolledWindow()
        self.open_worksheets_list_view_wrapper.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.recent_worksheets_list_view_wrapper = Gtk.ScrolledWindow()
        self.recent_worksheets_list_view_wrapper.add(self.recent_worksheets_list_view)
        
        self.pack_start(self.open_worksheets_label_revealer, False, False, 0)
        self.pack_start(self.open_worksheets_list_view_wrapper, False, False, 0)
        self.pack_start(self.recent_worksheets_label_revealer, False, False, 0)
        self.pack_start(self.recent_worksheets_list_view_wrapper, True, True, 0)


