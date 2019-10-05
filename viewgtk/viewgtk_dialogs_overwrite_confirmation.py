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


class OverwriteConfirmation(Gtk.MessageDialog):

    def __init__(self, main_window, name, folder):
        Gtk.MessageDialog.__init__(self, main_window, 0, Gtk.MessageType.QUESTION)

        self.set_property('text', 'A file named »' + name + '« already exists. Do you want to replace it?')
        self.format_secondary_markup('The file already exists in »' + folder + '«. Replacing it will overwrite its contents.')

        self.add_buttons('_Cancel', Gtk.ResponseType.CANCEL, '_Replace', Gtk.ResponseType.YES)
        self.set_default_response(Gtk.ResponseType.CANCEL)


