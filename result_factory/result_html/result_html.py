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
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import WebKit2

import webbrowser
import nbformat

from result_factory.result import Result
import app.service_locator as service_locator


class ResultHtml(Result):
    
    def __init__(self, data):
        Result.__init__(self)

        self.data = data
        self.html = data.replace('/nbextensions', 'resources/nbextensions')

        self.content = WebKit2.WebView()
        self.content.get_settings().set_enable_webgl(True)
        self.content.set_size_request(750, -1)

        self.get_style_context().add_class('resulthtmlview')

        self.centerbox.set_center_widget(self.content)
        self.show_all()

        # observe result view
        self.content.connect('load-changed', self.on_load_changed)
        self.content.connect('context-menu', self.on_context_menu)
        self.content.connect('button-press-event', self.on_mouse_click)

        self.content.load_html(self.html, 'file://' + service_locator.ServiceLocator.get_base_path())

    def export_nbformat(self):
        return nbformat.v4.new_output(
            output_type='display_data',
            data={'text/html': self.data}
        )

    def on_mouse_click(self, web_view, click_event):
        if click_event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            Gtk.propagate_event(self, click_event)
            return True
        return False

    def on_context_menu(self, view, menu, event, hit_test_result, user_data=None):
        return True

    def on_load_changed(self, view, load_event, user_data=None):
        if load_event == WebKit2.LoadEvent.FINISHED:
            view.run_javascript('document.documentElement.scrollHeight', None, self.set_size, '')

    def set_size(self, view, task, user_data=None):
        result = view.run_javascript_finish(task)
        view.set_size_request(750, int(result.get_js_value().to_string()))


