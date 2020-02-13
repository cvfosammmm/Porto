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
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk

import cell.cell as model_cell
from app.service_locator import ServiceLocator


class ResultRevealerPresenter(object):

    def __init__(self, result_revealer, view):

        self.result_revealer = result_revealer
        self.view = view

        if result_revealer.result != None:
            self.add_result_view(result_revealer.result, show_animation=False)
        self.result_revealer.register_observer(self)

        self.view.show_all()


class CodeResultRevealerPresenter(ResultRevealerPresenter):

    def __init__(self, result_revealer, view):
        ResultRevealerPresenter.__init__(self, result_revealer, view)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_result':
            self.add_result_view(parameter['result'], show_animation=parameter['show_animation'])
            self.update_stream_visibility()

        if change_code == 'stream_update':
            show_animation = parameter

            if self.result_revealer.result == None and not self.result_revealer.stderr_stream_visible and not self.result_revealer.stdout_stream_visible:
                self.view.unreveal()
                self.result_revealer.cell.view.text_widget.set_reveal_child(True)
                self.result_revealer.cell.view.text_entry.set_editable(True)
            else:
                GLib.idle_add(lambda: self.view.reveal(show_animation))
            self.update_stream_visibility()

    def update_stream_visibility(self):
        if self.result_revealer.stderr_stream_visible:
            self.result_revealer.streams['stderr'].show_all()
        else:
            self.result_revealer.streams['stderr'].hide()
        if self.result_revealer.stdout_stream_visible:
            self.result_revealer.streams['stdout'].show_all()
        else:
            self.result_revealer.streams['stdout'].hide()

    def add_result_view(self, result, show_animation=False):
        cell_view_position = self.result_revealer.cell.get_notebook_position()
        cell = self.result_revealer.cell
                
        # check if cell view is still present
        if cell_view_position >= 0:

            # add result
            if result == None and not self.result_revealer.stderr_stream_visible and not self.result_revealer.stdout_stream_visible:
                self.view.unreveal()
                self.view.set_result(result)
                self.result_revealer.cell.view.text_widget.set_reveal_child(True)
                self.result_revealer.cell.view.text_entry.set_editable(True)
            else:
                self.view.set_result(result)
                GLib.idle_add(lambda: self.view.reveal(show_animation))
                result.scrolled_window.connect('scroll-event', self.result_on_scroll)

            # enable auto-scrolling for this cell (not enabled on startup)
            GLib.idle_add(lambda: self.view.set_autoscroll_on_reveal(True))

    def result_on_scroll(self, scrolled_window, event):
        if(abs(event.delta_y) > 0):
            adjustment = self.notebook.view.get_vadjustment()

            page_size = adjustment.get_page_size()
            scroll_unit = pow (page_size, 2.0 / 3.0)

            adjustment.set_value(adjustment.get_value() + event.delta_y*scroll_unit)
        return True

    def add_streams(self, streams):
        for stream in streams.values():
            self.view.add_stream_view(stream)


class MarkdownResultRevealerPresenter(ResultRevealerPresenter):

    def __init__(self, result_revealer, view):
        ResultRevealerPresenter.__init__(self, result_revealer, view)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_result':
            self.add_result_view(parameter['result'], show_animation=parameter['show_animation'])

    def add_result_view(self, result, show_animation=False):
        cell_view_position = self.result_revealer.cell.get_notebook_position()
        cell = self.result_revealer.cell
                
        # check if cell view is still present
        if cell_view_position >= 0:

            # remove previous results
            revealer = self.result_revealer

            # add result
            if result == None:
                self.view.unreveal()
                self.result_revealer.cell.view.text_widget.set_reveal_child(True)
                self.result_revealer.cell.view.text_entry.set_editable(True)
            else:
                self.result_revealer.cell.view.unreveal(show_animation)
                self.result_revealer.cell.view.text_entry.set_editable(False)
                self.view.set_result(result)
                if show_animation == False:
                    revealer.reveal(show_animation)
                else:
                    GLib.idle_add(lambda: self.view.reveal(show_animation))
                result.content.connect('button-press-event', self.result_on_button_press)

            # enable auto-scrolling for this cell (not enabled on startup)
            GLib.idle_add(lambda: self.view.set_autoscroll_on_reveal(True))

    def result_on_button_press(self, widget, event, user_data=None):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            cell = self.result_revealer.cell
            notebook = cell.get_notebook()
            cell.remove_result()
            notebook.set_active_cell(cell)
            return True
        elif event.type == Gdk.EventType.BUTTON_PRESS:
            cell = self.result_revealer.cell
            notebook = cell.get_notebook()
            notebook.set_active_cell(cell)
            return False


