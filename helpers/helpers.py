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


import time


def theme_color_to_css(style_context, color_string):
    rgba = style_context.lookup_color(color_string)[1]
    return '#' + format(int(rgba.red * 255), '02x') + format(int(rgba.green * 255), '02x') + format(int(rgba.blue * 255), '02x')
    

def theme_color_to_rgba(style_context, color_string):
    return style_context.lookup_color(color_string)[1]


def get_notebook_name_from_pathname(pathname):
    return pathname.split('/')[-1].replace('.ipynb', '')


def shorten_folder(folder, max_characters):
    old_folder = ' ' + folder
    while len(folder) > max_characters and old_folder != folder:
        old_folder = folder
        folder = '.../' + '/'.join(folder.split('/')[2:])
    return folder

def timer(original_function):
    
    def new_function(*args, **kwargs):
        start_time = time.time()
        return_value = original_function(*args, **kwargs)
        print(original_function.__name__ + ': ' + str(time.time() - start_time) + ' seconds')
        return return_value
    
    return  new_function
