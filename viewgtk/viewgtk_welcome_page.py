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


class WelcomePageView(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_hexpand(True)
        self.get_style_context().add_class('welcomepageview')

        self.box = Gtk.VBox()
        self.add(self.box)
        self.viewport = self.get_children().pop()
        
        self.welcome_message = Gtk.Label()
        self.welcome_message.set_text('Porto is a notebook style interface to many programming\nlanguages. You create worksheets to type in commands for\ncomputation, plotting functions and many more things.\n')
        self.welcome_message.set_line_wrap(True)
        self.welcome_message.set_xalign(0)
        self.welcome_message.set_yalign(0)
        self.welcome_message.set_size_request(400, 50)
        
        self.welcome_links = Gtk.HBox()
        #self.welcome_links.set_size_request(400, 50)
        
        self.create_ws_link = Gtk.LinkButton('action://app.placeholder', 'Create New Worksheet')
        self.create_ws_link.set_can_focus(False)
        self.create_ws_link.set_tooltip_text('')
        self.open_ws_link = Gtk.LinkButton('action://app.placeholder', 'Open Worksheet(s)')
        self.open_ws_link.set_can_focus(False)
        self.open_ws_link.set_tooltip_text('')
        self.welcome_links.pack_start(self.create_ws_link, False, False, 0)
        self.welcome_links.pack_start(Gtk.Label(' or '), False, False, 0)
        self.welcome_links.pack_start(self.open_ws_link, False, False, 0)
        
        self.footer = Gtk.Label()
        self.footer.set_margin_bottom(20)
        self.footer.set_margin_left(25)
        self.footer.set_xalign(0)
        self.footer.set_line_wrap(True)

        self.welcome_box = Gtk.VBox()
        self.welcome_box.set_size_request(400, 250)
        self.welcome_box.pack_start(self.welcome_message, False, False, 0)
        self.welcome_box.pack_start(self.welcome_links, False, False, 0)
        self.welcome_box_wrapper = Gtk.HBox()
        self.welcome_box_wrapper.set_center_widget(self.welcome_box)
        self.box.set_center_widget(self.welcome_box_wrapper)
        self.box.pack_end(self.footer, False, False, 0)

    def set_sidebar_visible(self, sidebar_visible):
        pass
        #if sidebar_visible:
        #    self.footer.set_text('Of Note: To get started using Porto consider our "Absolute Beginners\' Guide" (in the sidebar).')
        #else:
        #    self.footer.set_text('Of Note: To get started using Porto consider our "Absolute Beginners\' Guide" (in the "Worksheets" menu above).')


