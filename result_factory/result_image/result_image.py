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
from gi.repository import Gtk, GLib, Gio, GdkPixbuf

import base64
import nbformat

from result_factory.result import Result


class ResultImage(Result):
    
    def __init__(self, image_base64):
        Result.__init__(self)

        self.get_style_context().add_class('resultimageview')

        self.image_base64 = image_base64
        image_bytes = GLib.Bytes(base64.b64decode(self.image_base64))
        image_stream = Gio.MemoryInputStream.new_from_bytes(image_bytes)
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_stream(image_stream)

        self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)
        self.centerbox.set_center_widget(self.image)
        self.show_all()

    def export_nbformat(self):
        return nbformat.v4.new_output(
            output_type='execute_result',
            data={'image/png': self.image_base64},
            execution_count=0
        )


