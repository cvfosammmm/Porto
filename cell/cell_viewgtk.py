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
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import GObject


class CellView(Gtk.HBox):

    def __init__(self, cell):
        Gtk.HBox.__init__(self)

        self.set_hexpand(False)
        self.set_can_focus(True)
        self.get_style_context().add_class('cellview')

        self.state_display = CellViewStateDisplay()

        self.pack_start(self.state_display, False, False, 0) #TODO

        self.vbox = Gtk.VBox()

        self.text_widget = Gtk.Revealer()
        self.text_widget.set_reveal_child(True)

        self.text_widget_wrapper = Gtk.HBox()

        self.text_widget_sw = Gtk.ScrolledWindow()
        self.text_widget_sw.set_hexpand(False)
        self.text_widget_sw.set_kinetic_scrolling(False)
        self.text_widget_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.text_widget_sw.set_propagate_natural_height(False)
        self.text_widget_sw.set_propagate_natural_width(False)
        self.text_widget_sw.set_overlay_scrolling(False)
        self.text_widget_sw.set_size_request(768, -1)
        self.text_widget_sw.set_margin_right(9)

        self.box_to_prevent_scrolling = Gtk.HBox()

        self.text_entry = GtkSource.View.new_with_buffer(cell)
        self.text_entry.set_monospace(True)
        self.text_entry.set_can_focus(True)
        self.text_entry.set_pixels_inside_wrap(2)
        self.text_entry.set_pixels_below_lines(2)
        self.text_entry.set_pixels_above_lines(0)
        self.text_entry.set_vadjustment(Gtk.Adjustment())
        self.text_entry.set_hadjustment(Gtk.Adjustment())
        self.text_entry.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_entry.set_show_line_numbers(False)
        self.text_entry.set_hexpand(False)
        self.text_entry.set_indent_width(4)
        self.text_entry.set_smart_home_end(GtkSource.SmartHomeEndType.AFTER)
        self.text_entry.set_indent_on_tab(True)
        self.text_entry.set_auto_indent(True)
        self.text_entry.set_insert_spaces_instead_of_tabs(True)
        self.text_entry.set_left_margin(9)
        self.text_entry.set_right_margin(15)
        self.text_entry.set_top_margin(11)
        self.text_entry.set_bottom_margin(11)

        self.box_to_prevent_scrolling.pack_start(self.text_entry, True, True, 0)
        self.text_widget_sw.add(self.box_to_prevent_scrolling)

        self.text_widget_wrapper.add(self.text_widget_sw)

        self.text_widget.add(self.text_widget_wrapper)

        self.vbox.pack_start(self.text_widget, False, False, 0)

        self.result_view_revealer = ResultViewRevealer(self)
        self.vbox.pack_start(self.result_view_revealer, False, False, 0)

        self.set_center_widget(self.vbox)

        self.line_height = 20
        self.size = {'width': self.get_allocated_width(), 'height': self.get_allocated_height()}
        self.cell = cell
        self.allocation = self.get_allocation()
        
    def get_source_view(self):
        return self.text_entry

    def get_cell(self):
        return self.cell

    def set_active(self):
        self.get_style_context().add_class('active')

    def set_inactive(self):
        self.get_style_context().remove_class('active')

    def has_changed_size(self):
        if self.size['width'] == self.get_allocated_width() and self.size['height'] == self.get_allocated_height():
            return False
        return True

    def update_size(self):
        self.size['width'] = self.get_allocated_width()
        self.size['height'] = self.get_allocated_height()
        

class CellViewCode(CellView):

    def __init__(self, cell):
        CellView.__init__(self, cell)

        self.get_style_context().add_class('cellviewcode')

        self.show_all()


class CellViewMarkdown(CellView):

    def __init__(self, cell):
        CellView.__init__(self, cell)

        self.get_style_context().add_class('cellviewmarkdown')

        self.result_view_revealer.get_style_context().add_class('markdown')

        self.show_all()

    def reveal(self, show_animation=True):
        if show_animation == False:
            self.text_widget.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.text_widget.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.text_widget.set_reveal_child(True)
        
    def unreveal(self, show_animation=True):
        if show_animation == False:
            self.text_widget.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.text_widget.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.text_widget.set_reveal_child(False)
    

class CellViewStateDisplay(Gtk.DrawingArea):

    def __init__(self):
        Gtk.Box.__init__(self)

        self.get_style_context().add_class('cellviewstatedisplay')

        self.set_hexpand(False)
        self.state = 'nothing'
        self.set_size_request(9, -1)
        self.spinner_state = 0
        self.connect('draw', self.draw)
        GObject.timeout_add(10, self.draw_spinner)

    def show_spinner(self):
        if self.state != 'spinner':
            self.state = 'spinner'
        
    def draw_spinner(self):
        self.spinner_state += 1
        self.queue_draw()
        return True
    
    def draw(self, widget, cr, data = None):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        context = self.get_style_context()
        Gtk.render_background(context, cr, 0, 0, width, height)
        
        if self.state == 'spinner':
            cr.set_source_rgba(1, 1, 1, 0.5)
            i = -20 + (self.spinner_state % 20)
            while i < height:
                cr.rectangle(0, i, 10, 10)
                cr.fill()
                i += 20
        return True
    
    def show_nothing(self):
        if self.state != 'nothing':
            self.state = 'nothing'


class ResultViewRevealer(Gtk.EventBox):

    def __init__(self, cell_view):
        Gtk.EventBox.__init__(self)

        self.get_style_context().add_class('resultviewrevealer')

        self.cell_view = cell_view
        self.wrapper = Gtk.HBox()
        self.revealer = Gtk.Revealer()

        self.seperator1 = ResultViewSeperator1(isinstance(self.cell_view, CellViewCode))
        self.superbox = Gtk.VBox()
        self.superbox.pack_start(self.seperator1, False, False, 0)
        self.superbox.set_margin_right(9)

        self.box = Gtk.VBox()
        self.revealer.add(self.box)
        self.superbox.pack_start(self.revealer, True, True, 0)

        self.wrapper.set_center_widget(self.superbox)
        self.add(self.wrapper)
        self.revealer.set_reveal_child(False)
        
        self.result_view = None
        self.allocation = self.get_allocation()
        self.autoscroll_on_reveal = False
        
    def set_result(self, result_view):
        if self.result_view != None:
            self.box.remove(self.result_view)
        
        self.result_view = result_view
        self.box.pack_start(self.result_view, True, True, 0)
    
    def reveal(self, show_animation=True, duration=250):
        self.revealer.set_transition_duration(duration)
        if show_animation == False:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        if isinstance(self.cell_view, CellViewCode):
            self.seperator1.reveal()
        self.revealer.set_reveal_child(True)
        
    def unreveal(self, show_animation=True, duration=250):
        self.seperator1.unreveal(100)
        self.revealer.set_transition_duration(duration)
        if show_animation == False:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        else:
            self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer.set_reveal_child(False)
        
    def set_autoscroll_on_reveal(self, value):
        self.autoscroll_on_reveal = value
    

class ResultViewSeperator1(Gtk.DrawingArea):
    
    def __init__(self, is_white):
        Gtk.DrawingArea.__init__(self)

        self.get_style_context().add_class('resultviewseperator1')

        self.set_size_request(-1, 1)
        self.connect('draw', self.draw)
        self.opacity = 0
        self.bgcolor = 'white' if is_white else 'grey'
        
    def draw(self, widget, cr, data = None):
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        context = self.get_style_context()
        if self.bgcolor == 'white':
            Gtk.render_background(context, cr, 0, 0, width, height)
        else:
            cr.set_source_rgba(0.97, 0.97, 0.97, 1)
            cr.rectangle(0, 0, width, height)
            cr.fill()
        
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
        GObject.timeout_add(duration / 20, self.increase_opacity)
        self.queue_draw()
        return False
    
    def unreveal(self, duration=100):
        GObject.timeout_add(duration / 20, self.reduce_opacity)
        return False


