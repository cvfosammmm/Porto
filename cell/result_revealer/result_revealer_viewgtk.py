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
from gi.repository import GObject


class ResultViewRevealer(Gtk.EventBox):

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.get_style_context().add_class('resultviewrevealer')

        self.wrapper = Gtk.HBox()
        self.revealer = Gtk.Revealer()

        self.superbox = Gtk.VBox()

    def set_result(self, result_view):
        if self.result_view != None:
            self.box.remove(self.result_view)

        if result_view != None:
            self.result_view = result_view
            self.box.pack_start(self.result_view, True, True, 0)

    def set_autoscroll_on_reveal(self, value):
        self.autoscroll_on_reveal = value
    

class ResultViewRevealerMarkdown(ResultViewRevealer):

    def __init__(self):
        ResultViewRevealer.__init__(self)
        self.get_style_context().add_class('markdown')

        self.box = Gtk.VBox()
        self.revealer.add(self.box)
        self.superbox.pack_start(self.revealer, True, True, 0)

        self.wrapper.set_center_widget(self.superbox)
        self.add(self.wrapper)
        self.revealer.set_reveal_child(False)
        
        self.result_view = None
        self.allocation = self.get_allocation()
        self.autoscroll_on_reveal = False

    def reveal(self, show_animation=True, duration=250):
        self.revealer.set_transition_duration(duration)
        if show_animation == False:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_reveal_child(True)
        
    def unreveal(self, show_animation=True, duration=250):
        self.revealer.set_transition_duration(duration)
        if show_animation == False:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_reveal_child(False)
        

class ResultViewRevealerCode(ResultViewRevealer):

    def __init__(self):
        ResultViewRevealer.__init__(self)
        self.separator = ResultViewSeparator()
        self.superbox.pack_start(self.separator, False, False, 0)

        self.box = Gtk.VBox()
        self.revealer.add(self.box)
        self.superbox.pack_start(self.revealer, True, True, 0)

        self.wrapper.set_center_widget(self.superbox)
        self.add(self.wrapper)
        self.revealer.set_reveal_child(False)
        
        self.result_view = None
        self.allocation = self.get_allocation()
        self.autoscroll_on_reveal = False

    def add_stream_view(self, view):
        self.box.pack_start(view, False, False, 0)

    def reveal(self, show_animation=True, duration=250):
        self.revealer.set_transition_duration(duration)
        if show_animation == False:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.separator.reveal()
        self.revealer.set_reveal_child(True)
        
    def unreveal(self, show_animation=True, duration=250):
        self.separator.unreveal(100)
        self.revealer.set_transition_duration(duration)
        if show_animation == False:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_reveal_child(False)
        

class ResultViewSeparator(Gtk.DrawingArea):
    
    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.get_style_context().add_class('resultviewseparator')

        self.set_size_request(-1, 1)
        self.connect('draw', self.draw)
        self.opacity = 0
        
    def draw(self, widget, cr, data = None):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        context = self.get_style_context()
        Gtk.render_background(context, cr, 0, 0, width, height)
        
        if self.opacity > 0:
            cr.set_source_rgba(0.86, 0.86, 0.86, self.opacity)
            i = 0
            while i < width:
                cr.rectangle(i, 0, 9, 9)
                cr.fill()
                i += 18
        else:
            pass
        return False
    
    def reduce_opacity(self):
        if self.opacity > 0:
            self.opacity -= 0.05
            self.queue_draw()
            return True
        else:
            self.opacity = 0
            self.hide()
            self.queue_draw()
            return False
        
    def increase_opacity(self):
        if self.opacity < 1:
            self.opacity += 0.05
            self.queue_draw()
            return True
        else:
            self.opacity = 1
            self.queue_draw()
            return False

    def reveal(self, duration=100):
        self.show_all()
        GObject.timeout_add(duration / 20, self.increase_opacity)
        self.queue_draw()
        return False
    
    def unreveal(self, duration=100):
        GObject.timeout_add(duration / 20, self.reduce_opacity)
        return False


