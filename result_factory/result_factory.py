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
gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio, GdkPixbuf, Pango
from gi.repository import WebKit2

import webbrowser
import base64

import helpers.helpers as helpers


class Result(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.get_style_context().add_class('resultview')

        self.innerwrap = Gtk.HBox()
        self.innerwrap.set_margin_left(9)
        self.innerwrap.set_margin_right(9)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_margin_top(13)
        self.scrolled_window.set_margin_bottom(11)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        
        self.centerbox = Gtk.HBox()
        self.scrolled_window.add(self.centerbox)
        self.scrolled_window.set_size_request(750, -1)

        self.innerwrap.set_center_widget(self.scrolled_window)
        self.set_center_widget(self.innerwrap)
        self.set_hexpand(True)


class MarkdownResult(Gtk.HBox):

    def __init__(self, result_blob):
        Gtk.HBox.__init__(self)

        self.get_style_context().add_class('mdresultview')

        self.html = result_blob

        self.content = WebKit2.WebView()
        self.centerbox = Gtk.VBox()

        self.contentwrap = Gtk.VBox()
        self.contentwrap.set_margin_top(16)
        self.contentwrap.set_margin_bottom(22)
        self.contentwrap.set_margin_left(12)
        self.contentwrap.set_margin_right(6)
        self.contentwrap.pack_start(self.content, False, False, 0)
        self.centerbox.set_center_widget(self.contentwrap)
        self.set_center_widget(self.centerbox)
        self.set_hexpand(True)
        self.show_all()

        self.compile()

        # observe result view
        self.content.connect('decide-policy', self.on_policy_decision)
        self.content.connect('load-changed', self.on_load_changed)
        self.content.connect('context-menu', self.on_context_menu)

    def compile(self):
        html = '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="" xml:lang="">
<head>
<meta charset="utf-8" />
<style>
body { width: 750px; font-family: nimbus sans l, cantarell, sans-serif; margin: 0px; color: ''' + helpers.theme_color_to_css(self.get_style_context(), 'theme_fg_color') + '''; background-color: ''' + helpers.theme_color_to_css(self.get_style_context(), 'theme_bg_color') + '''; }
p { font-size: 16px; font-family: nimbus sans l, Source Serif Pro, Nimbus Roman No9 L, nimbus sans l, lora, linux libertine display o, liberation serif, freeserif, libertine, cantarell, sans-serif; margin-top: 12px; margin-bottom: 3px; line-height: 135%; }
h1 { font-size: 30px; font-weight: bold; margin-top: 21px; }
h2 { font-size: 24px; font-weight: bold; margin-top: 21px; margin-bottom: 1px; }
h3 { font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 3px; }
h4 { font-size: 16px; font-weight: bold; margin-top: 22px; margin-bottom: 3px; font-style: italic; }
h5 { font-size: 16px; margin-top: 22px; margin-bottom: 3px; }
h6 { font-size: 16px; margin-top: 22px; margin-bottom: 3px; }

math {font-size: 19px; font-family: STIX Math}
</style>
</head>
<body>
''' + self.get_html() + '''
</body>
</html>'''
        self.content.load_html(html)

    def on_policy_decision(self, view, decision, decision_type, user_data=None):
        na = WebKit2.PolicyDecisionType.NAVIGATION_ACTION
        nwa = WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION
        ra = WebKit2.PolicyDecisionType.RESPONSE
        if decision_type == na or decision_type == nwa:
            uri = decision.get_navigation_action().get_request().get_uri()
            if uri == 'about:blank':
                pass
            else:
                webbrowser.open_new_tab(uri)
                decision.ignore()
        elif decision_type == ra:
            pass

    def on_context_menu(self, view, menu, event, hit_test_result, user_data=None):
        return True

    def on_load_changed(self, view, load_event, user_data=None):
        if load_event == WebKit2.LoadEvent.FINISHED:
            view.run_javascript('document.documentElement.scrollHeight', None, self.set_size, '')

    def set_size(self, view, task, user_data=None):
        result = view.run_javascript_finish(task)
        view.set_size_request(750, int(result.get_js_value().to_string()))

    def get_html(self):
        return self.html
        
    def get_as_raw_text(self):
        return self.html


class ResultText(Result):
    
    def __init__(self, result_text):
        Result.__init__(self)

        self.get_style_context().add_class('resulttextview')

        self.result_text = result_text.rstrip()

        self.label = Gtk.Label()
        self.label.set_single_line_mode(False)
        self.label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        self.label.set_line_wrap(True)
        self.label.set_selectable(True)
        self.set_text(self.result_text)

        self.size_box = Gtk.VBox()
        self.size_box.pack_start(self.label, False, False, 0)
        self.centerbox.pack_start(self.size_box, False, False, 0)
        self.show_all()
        self.label.connect('size-allocate', self.allocation_hack)
    
    def allocation_hack(self, label, allocation):
        self.size_box.set_size_request(-1, allocation.height)
        number_of_lines = label.get_text().count('\n') + 1
        if (number_of_lines * 20) < allocation.height:
            self.label.set_justify(Gtk.Justification.LEFT)
            self.label.set_xalign(0)
        else:
            self.label.set_justify(Gtk.Justification.CENTER)
            self.label.set_xalign(0.5)

    def set_text(self, text):
        if not len(text) > 0: text = ''
        #resolution = self.get_style_context().get_screen().get_resolution()
        #rise_units = int(4*1024.0 * (max(resolution, 96)/72))
        rise_units = 6144
        self.label.set_markup('<span rise="' + str(rise_units) + '"><span font_desc="">' + GLib.markup_escape_text(text) + '</span></span>')

    def get_text(self):
        return self.result_text

    def export_nbformat(self):
        return {'text/plain': self.result_text}


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
        return {'image/png': self.image_base64}


