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


class ButtonBox(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.add_cell_box = Gtk.HBox()
        self.add_cell_box.get_style_context().add_class('linked')

        self.add_codecell_button = Gtk.Button.new_from_icon_name('add-codecell-symbolic', Gtk.IconSize.BUTTON)
        self.add_codecell_button.set_tooltip_text('Add code cell below (Alt+Return)')
        self.add_codecell_button.set_focus_on_click(False)
        self.add_cell_box.add(self.add_codecell_button)
        self.add_markdowncell_button = Gtk.Button.new_from_icon_name('add-markdowncell-symbolic', Gtk.IconSize.BUTTON)
        self.add_markdowncell_button.set_tooltip_text('Add markdown cell below (Ctrl+M)')
        self.add_markdowncell_button.set_focus_on_click(False)
        self.add_cell_box.add(self.add_markdowncell_button)
        
        self.move_cell_box = Gtk.HBox()
        self.move_cell_box.get_style_context().add_class('linked')
        self.up_button = Gtk.Button.new_from_icon_name('up-button-symbolic', Gtk.IconSize.BUTTON)
        self.up_button.set_tooltip_text('Move cell up (Ctrl+Up)')
        self.up_button.set_focus_on_click(False)
        self.up_button.set_sensitive(False)
        self.move_cell_box.add(self.up_button)
        self.down_button = Gtk.Button.new_from_icon_name('down-button-symbolic', Gtk.IconSize.BUTTON)
        self.down_button.set_tooltip_text('Move cell down (Ctrl+Down)')
        self.down_button.set_focus_on_click(False)
        self.down_button.set_sensitive(False)
        self.move_cell_box.add(self.down_button)
        self.delete_button = Gtk.Button.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON)
        self.delete_button.set_tooltip_text('Delete cell (Ctrl+Backspace)')
        self.delete_button.set_focus_on_click(False)
        self.move_cell_box.add(self.delete_button)

        self.eval_box = Gtk.HBox()
        self.eval_box.get_style_context().add_class('linked')
        self.eval_button = Gtk.Button.new_from_icon_name('eval-button-symbolic', Gtk.IconSize.BUTTON)
        self.eval_button.set_tooltip_text('Evaluate Cell (Shift+Return)')
        self.eval_button.set_focus_on_click(False)
        self.eval_box.add(self.eval_button)
        self.eval_nc_button = Gtk.Button.new_from_icon_name('eval-nc-button-symbolic', Gtk.IconSize.BUTTON)
        self.eval_nc_button.set_tooltip_text('Evaluate Cell, then Go to next Cell (Ctrl+Return)')
        self.eval_nc_button.set_focus_on_click(False)
        self.eval_box.add(self.eval_nc_button)
        self.stop_button = Gtk.Button.new_from_icon_name('media-playback-stop-symbolic', Gtk.IconSize.BUTTON)
        self.stop_button.set_tooltip_text('Stop Evaluation (Ctrl+H)')
        self.stop_button.set_focus_on_click(False)
        self.stop_button.set_sensitive(False)
        self.eval_box.add(self.stop_button)

        self.pack_start(self.add_cell_box, False, False, 0)
        self.pack_start(self.move_cell_box, False, False, 0)
        self.pack_start(self.eval_box, False, False, 0)

        self.show_all()

