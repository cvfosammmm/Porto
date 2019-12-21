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


class Result(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.get_style_context().add_class('resultview')

        self.innerwrap = Gtk.HBox()
        self.innerwrap.set_margin_left(9)
        self.innerwrap.set_margin_right(9)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_margin_top(13)
        self.scrolled_window.set_margin_bottom(11)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        
        self.centerbox = Gtk.HBox()
        self.scrolled_window.add(self.centerbox)
        self.scrolled_window.set_size_request(750, -1)

        self.innerwrap.set_center_widget(self.scrolled_window)
        self.set_center_widget(self.innerwrap)
        self.set_hexpand(True)


