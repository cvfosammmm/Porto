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


class WorksheetView(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_hexpand(True)
        self.set_propagate_natural_height(True)
        self.set_propagate_natural_width(True)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.get_style_context().add_class('worksheetview')
        
        self.set_overlay_scrolling(True)

        self.box = Gtk.VBox()
        self.add(self.box)
        self.viewport = self.get_children().pop()
        
        # add padding to the top and bottom
        self.box.set_margin_top(10)
        self.box.set_margin_bottom(100)

        # contains all types of cell view, result views, ...
        self.children = list()

        # disable auto scrolling
        self.get_child().set_focus_vadjustment(Gtk.Adjustment())
        self.get_child().set_focus_hadjustment(Gtk.Adjustment())

    def add_child_at_position(self, view, position):
        self.children.insert(position, view)
        self.box.pack_start(view, False, False, 0)
        self.box.reorder_child(view, position)
        self.show_all()
        
    def move_child(self, child, position):
        old_position = self.get_child_position(child)
        self.children[old_position], self.children[position] = self.children[position], self.children[old_position]
        self.box.reorder_child(child, position)
        
    def get_child_by_position(self, position):
        if position < len(self.children):
            return self.children[position]
        else:
            return None
    
    def get_child_position(self, child):
        try: index = self.children.index(child)
        except ValueError: index = -1
        return index
    
    def remove_child_by_position(self, position):
        self.box.remove(self.children[position])
        del(self.children[position])
        self.show_all()
        
    def scroll(self, amount):
        scroll_position = self.get_vadjustment()
        scroll_position.set_value(scroll_position.get_value() + amount)


