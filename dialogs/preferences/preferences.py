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

from dialogs.dialog import Dialog
import dialogs.preferences.preferences_viewgtk as view


class PreferencesDialog(Dialog):

    def __init__(self, main_window, settings):
        self.main_window = main_window
        self.settings = settings

    def run(self):
        self.setup()
        self.view.run()
        del(self.view)

    def setup(self):
        self.view = view.Preferences(self.main_window)

        self.view.option_pretty_print.set_active(self.settings.get_value('preferences', 'pretty_print'))
        self.view.option_pretty_print.connect('toggled', self.on_button_toggle, 'pretty_print')

    def on_button_toggle(self, button, preference_name):
        self.settings.set_value('preferences', preference_name, button.get_active())


