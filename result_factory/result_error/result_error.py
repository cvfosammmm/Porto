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
import app.service_locator as service_locator

import re
import nbformat


class ResultError(Result):
    
    def __init__(self, error_type, error_message, traceback):
        Result.__init__(self)

        self.error_type = error_type
        self.error_message = error_message
        self.traceback = traceback

        self.get_style_context().add_class('resulterrorview')

        self.traceback_text = ''
        ansi_escape_regex = service_locator.ServiceLocator.get_ansi_escape_regex()
        for t_string in self.traceback[2:-1]:
            self.traceback_text += '\n' + GLib.markup_escape_text(ansi_escape_regex.sub('', t_string).strip())
        self.header_box = Gtk.HBox()

        self.type_label = Gtk.Label(self.error_type)
        self.type_label.set_selectable(True)
        self.type_label.get_style_context().add_class('type')
        
        # remove "<ipython-input-0123456789abcde-abcde>, " from the error message 
        ipython_message_escape_regex = service_locator.ServiceLocator.get_ipython_message_escape_regex()
        self.message_label = Gtk.Label(': ' + ipython_message_escape_regex.sub('', self.error_message))
        
        self.message_label.set_single_line_mode(False)
        self.message_label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        self.message_label.set_line_wrap(True)
        self.message_label.set_selectable(True)
        self.message_label.get_style_context().add_class('message')

        self.header_box.pack_start(self.type_label, False, False, 0)
        self.header_box.pack_start(self.message_label, False, False, 0)
        self.header_box.set_margin_bottom(4)

        self.label = Gtk.Label()
        self.label.set_single_line_mode(False)
        self.label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.label.set_xalign(0)
        self.set_text(self.traceback_text)

        self.size_box = Gtk.VBox()
        self.size_box.pack_start(self.header_box, False, False, 0)
        self.size_box.pack_start(self.label, False, False, 0)
        self.centerbox.pack_start(self.size_box, False, False, 0)
        self.show_all()
    
    def set_text(self, text):
        if not len(text) > 0: text = ''
        rise_units = 6144
        self.label.set_markup('<span rise="' + str(rise_units) + '"><span font_desc="">' + text + '</span></span>')

    def export_nbformat(self):
        return nbformat.v4.new_output(
            output_type='error',
            data=None,
            ename=self.error_type,
            evalue=self.error_message,
            traceback=self.traceback
        )


