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
from gi.repository import Gtk, GLib, Pango

from result_factory.result import Result

import nbformat


class ResultText(Result):
    
    def __init__(self, result_text):
        Result.__init__(self)

        self.get_style_context().add_class('resulttextview')

        self.result_text = result_text.rstrip()

        self.label = Gtk.Label()
        self.label.set_single_line_mode(False)
        self.label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.set_text(self.result_text)

        self.size_box = Gtk.VBox()
        self.size_box.pack_start(self.label, False, False, 0)
        self.centerbox.pack_start(self.size_box, False, False, 0)
        self.show_all()
        self.label.connect('size-allocate', self.allocation_hack)
    
    def allocation_hack(self, label, allocation):
        self.size_box.set_size_request(-1, allocation.height)
        number_of_lines = label.get_text().count('\n') + 1
        if (number_of_lines * 20) < allocation.height:
            self.label.set_justify(Gtk.Justification.LEFT)
            self.label.set_xalign(0)
        else:
            self.label.set_justify(Gtk.Justification.CENTER)
            self.label.set_xalign(0.5)

    def set_text(self, text):
        if not len(text) > 0: text = ''
        #resolution = self.get_style_context().get_screen().get_resolution()
        #rise_units = int(4*1024.0 * (max(resolution, 96)/72))
        rise_units = 6144
        self.label.set_markup('<span rise="' + str(rise_units) + '"><span font_desc="">' + GLib.markup_escape_text(text) + '</span></span>')

    def get_text(self):
        return self.result_text

    def export_nbformat(self):
        output = nbformat.v4.new_output(
            output_type='execute_result',
            data={'text/plain': self.result_text},
            execution_count=0
        )


