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
from gi.repository import GLib
from gi.repository import Pango

import nbformat

from helpers.observable import Observable
import cell.cell_viewgtk as cell_view


class Stream(Gtk.HBox, Observable):

    def __init__(self, stream_type='stdout'):
        Gtk.HBox.__init__(self)
        Observable.__init__(self)

        self.get_style_context().add_class('resultview')

        self.innerwrap = Gtk.HBox()
        self.innerwrap.set_margin_left(9)
        self.innerwrap.set_margin_right(9)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_margin_top(10)
        self.scrolled_window.set_margin_bottom(8)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        
        self.centerbox = Gtk.HBox()
        self.scrolled_window.add(self.centerbox)
        self.scrolled_window.set_size_request(750, -1)

        self.innerwrap.set_center_widget(self.scrolled_window)
        self.set_center_widget(self.innerwrap)
        self.set_hexpand(True)

        self.get_style_context().add_class('resultstreamview')

        self.result_text = ''
        self.stream_type = stream_type

        self.label = Gtk.Label()
        self.label.set_single_line_mode(False)
        self.label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_xalign(0)
        self.label.set_markup('')

        self.size_box = Gtk.VBox()
        self.size_box.pack_start(self.label, False, False, 0)
        self.centerbox.pack_start(self.size_box, False, False, 0)
    
    def add_text(self, text):
        self.result_text += text
        if not len(text) > 0: text = ''
        #resolution = self.get_style_context().get_screen().get_resolution()
        #rise_units = int(4*1024.0 * (max(resolution, 96)/72))
        rise_units = 6144
        self.label.set_markup('<span rise="' + str(rise_units) + '"><span font_desc="">' + GLib.markup_escape_text(self.result_text.rstrip()) + '</span></span>')

    def get_text(self):
        return self.result_text

    def reset(self):
        self.result_text = ''
        self.label.set_markup('')

    def export_nbformat(self):
        return nbformat.v4.new_output(
            output_type='stream',
            name=self.stream_type,
            text=self.result_text
        )
            

