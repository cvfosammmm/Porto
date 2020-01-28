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
from gi.repository import GdkPixbuf
import os.path
import jupyter_client


class Kernelspecs():

    def __init__(self):
        self.installed_kernels = dict()
        self.fetch_kernelspecs()

    def fetch_kernelspecs(self):
        self.installed_kernels = jupyter_client.kernelspec.find_kernel_specs()
        for name in list(self.installed_kernels.keys()):
            self.installed_kernels[name] = jupyter_client.kernelspec.get_kernel_spec(name)

    def get_default(self):
        return 'python3'

    def get_list_of_names(self):
        list_of_names = ['python3']
        for name in self.installed_kernels.keys():
            if name not in ['python3']:
                list_of_names.append(name)
        return list_of_names

    def get_displayname(self, name):
        try: return self.installed_kernels[name].display_name
        except KeyError: return None

    def get_menu_icon(self, name):
        filename = './resources/images/' + name + '_icon_1.png'
        if os.path.isfile(filename):
            icon = self.get_icon_from_filename(filename)
            return icon
        filename = self.get_kernelspec_icon_path(name)
        if filename != None and os.path.isfile(filename):
            icon = self.get_icon_from_resource_dir(filename, 16)
            return icon
        filename = './resources/images/placeholder_icon_1.png'
        if os.path.isfile(filename):
            icon = self.get_icon_from_filename(filename)
            return icon

    def get_normal_sidebar_icon(self, name):
        filename = './resources/images/' + name + '_icon_2.png'
        if os.path.isfile(filename):
            icon = self.get_icon_from_filename(filename)
            icon.get_style_context().add_class('wslist_icon')
            return icon
        filename = self.get_kernelspec_icon_path(name)
        if filename != None and os.path.isfile(filename):
            icon = self.get_icon_from_resource_dir(filename, 30)
            icon.get_style_context().add_class('wslist_icon')
            return icon
        filename = './resources/images/placeholder_icon_2.png'
        if os.path.isfile(filename):
            icon = self.get_icon_from_filename(filename)
            icon.get_style_context().add_class('wslist_icon')
            return icon

    def get_active_sidebar_icon(self, name):
        filename = './resources/images/' + name + '_icon_4.png'
        if os.path.isfile(filename):
            icon = self.get_icon_from_filename(filename)
            icon.get_style_context().add_class('wslist_icon')
            return icon
        filename = self.get_kernelspec_icon_path(name)
        if filename != None and os.path.isfile(filename):
            icon = self.get_icon_from_resource_dir(filename, 30)
            icon.get_style_context().add_class('wslist_icon')
            return icon
        filename = './resources/images/placeholder_icon_4.png'
        if os.path.isfile(filename):
            icon = self.get_icon_from_filename(filename)
            icon.get_style_context().add_class('wslist_icon')
            return icon

    def get_background_path(self, name):
        return './resources/images/' + name + '_icon_3.png'

    def get_kernelspec_icon_path(self, name):
        if name in self.installed_kernels:
            return self.installed_kernels[name].resource_dir + '/logo-64x64.png'
        else:
            return None

    def get_icon_from_filename(self, filename):
        return Gtk.Image.new_from_file(filename)

    def get_icon_from_resource_dir(self, filename, size):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, size, size)
        return Gtk.Image.new_from_pixbuf(pixbuf)


