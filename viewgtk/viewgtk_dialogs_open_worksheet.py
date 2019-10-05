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


class OpenWorksheet(Gtk.FileChooserDialog):
    ''' File chooser for worksheets to open '''
    
    def __init__(self, main_window):
        self.action = Gtk.FileChooserAction.OPEN
        self.buttons = ('_Cancel', Gtk.ResponseType.CANCEL, '_Open', Gtk.ResponseType.OK)
        Gtk.FileChooserDialog.__init__(self, 'Open worksheet', main_window, self.action, self.buttons)
    
        for widget in self.get_header_bar().get_children():
            if isinstance(widget, Gtk.Button) and widget.get_label() == '_Open':
                widget.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
                widget.set_can_default(True)
                widget.grab_default()

        # file filtering
        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.ipynb')
        file_filter1.set_name('Jupyter Worksheets')
        self.add_filter(file_filter1)
        
        self.set_select_multiple(False)


