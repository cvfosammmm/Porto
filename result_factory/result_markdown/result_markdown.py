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
from gi.repository import Gtk
from gi.repository import WebKit2

import webbrowser

import helpers.helpers as helpers

from result_factory.result import Result


class MarkdownResult(Gtk.HBox):

    def __init__(self, result_blob):
        Gtk.HBox.__init__(self)

        self.get_style_context().add_class('mdresultview')

        self.html = result_blob

        self.content = WebKit2.WebView()
        self.centerbox = Gtk.VBox()

        self.contentwrap = Gtk.VBox()
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
p { font-size: 16px; font-family: nimbus sans l, Source Serif Pro, Nimbus Roman No9 L, nimbus sans l, lora, linux libertine display o, liberation serif, freeserif, libertine, cantarell, sans-serif; margin-top: 10px; margin-bottom: 10px; line-height: 125%; }
h1 { font-size: 32px; line-height: 40px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; font-weight: 800; text-align: left; }
h2 { font-size: 24px; line-height: 30px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; }
h3 { font-size: 20px; line-height: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; }
h4 { font-size: 16px; line-height: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; font-style: italic; }
h5 { font-size: 16px; line-height: 20px; margin-top: 20px; margin-bottom: 20px; }
h6 { font-size: 16px; line-height: 20px; margin-top: 20px; margin-bottom: 20px; }

math {font-size: 19px; line-height: 20px; font-family: STIX Math}
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


