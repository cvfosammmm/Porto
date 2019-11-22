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
from gi.repository import Pango

import datetime
import time
import os.path

import helpers.helpers as helpers


class WorksheetListRecentView(Gtk.ListBox):

    def __init__(self):
        Gtk.ListBox.__init__(self)

        self.items = dict()
        self.selected_row = None
        self.visible_items_count = 0
        
    def add_item(self, item):
        try: item = self.items[item.pathname]
        except KeyError:
            self.items[item.pathname] = item
            self.prepend(item)
            if item.revealer.get_reveal_child() == True:
                self.visible_items_count += 1
        else: item.set_last_save(item.last_saved)
        self.show_all()
        
    def remove_item_by_pathname(self, pathname):
        try: item = self.items[pathname]
        except KeyError:
            pass
        else:
            del(self.items[pathname])
            self.remove(item)
            if item.revealer.get_reveal_child() == True:
                self.visible_items_count -= 1
        self.show_all()
        
    def hide_item_by_pathname(self, pathname):
        try: item = self.items[pathname]
        except KeyError:
            pass
        else:
            if item.revealer.get_reveal_child() == True:
                self.visible_items_count -= 1
                item.unreveal()
        self.show_all()
        
    def show_item_by_pathname(self, pathname):
        try: item = self.items[pathname]
        except KeyError:
            pass
        else:
            if item.revealer.get_reveal_child() == False:
                self.visible_items_count += 1
                item.reveal()
        self.show_all()
        
    def get_row_index_by_pathname(self, pathname):
        index = 0
        for row in self.get_children():
            if row.pathname == pathname:
                return index
            index += 1
            
    def get_item_by_pathname(self, pathname):
        try: item = self.items[pathname]
        except KeyError: pass
        else: return item


class WorksheetListViewItem(Gtk.ListBoxRow):

    def __init__(self, pathname, kernelname, last_saved=None):
        Gtk.ListBoxRow.__init__(self)
        self.get_style_context().add_class('wslist_item')

        self.icon_stack = Gtk.Stack()
        self.icon_normal = None
        self.icon_active = None
        self.icon_type = None
        
        self.worksheet_name = pathname
        self.last_saved = last_saved
        
        self.name = Gtk.Label()
        self.name.set_justify(Gtk.Justification.LEFT)
        self.name.set_xalign(0)
        self.name.set_hexpand(False)
        self.name.set_single_line_mode(True)
        self.name.set_max_width_chars(-1)
        self.name.set_ellipsize(Pango.EllipsizeMode.END)
        self.name.get_style_context().add_class('wslist_name')

        self.box = Gtk.HBox()
        self.box.pack_start(self.icon_stack, False, False, 0)

    def update_kernel_icons(self, icon_normal, icon_active):
        if self.icon_normal != None: self.icon_stack.remove(self.icon_normal)
        if self.icon_active != None: self.icon_stack.remove(self.icon_active)
        self.icon_normal = icon_normal
        self.icon_active = icon_active
        self.icon_stack.add_named(self.icon_normal, 'normal')
        self.icon_stack.add_named(self.icon_active, 'active')
        self.show_all()
        if self.icon_type != None:
            self.set_icon_type(self.icon_type)

    def set_icon_type(self, icon_type='normal'):
        self.icon_type = icon_type
        self.icon_stack.set_visible_child_name(icon_type)


class RecentWorksheetListViewItem(WorksheetListViewItem):
    ''' Link in sidebar to activate worksheet, show some data about it '''
    
    def __init__(self, pathname, kernelname, last_saved):
        WorksheetListViewItem.__init__(self, pathname, kernelname, last_saved)

        self.pathname = pathname
        self.statebox = Gtk.HBox()
        self.folder = Gtk.Label()
        self.folder.set_justify(Gtk.Justification.LEFT)
        self.folder.set_xalign(0)
        self.folder.set_hexpand(False)
        self.folder.get_style_context().add_class('wslist_folder')
        self.last_save = Gtk.Label()
        self.last_save.set_justify(Gtk.Justification.LEFT)
        self.last_save.set_xalign(1)
        self.last_save.set_yalign(0)
        self.last_save.set_hexpand(False)
        self.last_save.get_style_context().add_class('wslist_last_save')
        self.statebox.pack_start(self.folder, True, True, 0)
        self.statebox.pack_start(self.last_save, True, True, 0)
        
        self.textbox = Gtk.VBox()
        self.textbox.pack_start(self.name, False, False, 0)
        self.textbox.pack_start(self.statebox, True, True, 0)

        self.box.pack_end(self.textbox, True, True, 0)
        self.box.get_style_context().add_class('wslist_wrapper')
        self.revealer = Gtk.Revealer()
        self.revealer.add(self.box)
        self.revealer.set_reveal_child(True)
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.add(self.revealer)
        
        self.set_name(helpers.get_worksheet_name_from_pathname(pathname))
        self.set_last_save(last_saved)
        self.set_folder(os.path.dirname(pathname))

    def unreveal(self):
        self.revealer.set_reveal_child(False)
        
    def reveal(self):
        self.revealer.set_reveal_child(True)
        
    def set_name(self, new_name):
        self.worksheet_name = new_name
        self.name.set_text(self.worksheet_name)
        
    def set_last_save(self, new_date):
        self.last_saved = new_date
        today = datetime.date.today()
        yesterday = datetime.date.fromtimestamp(time.time() - 86400)
        monday = datetime.date.fromtimestamp(time.time() - today.weekday()*86400)
        if self.last_saved.date() == today:
            datestring = '{:02d}:{:02d}'.format((self.last_saved.hour), (self.last_saved.minute))
        elif self.last_saved.date() == yesterday:
            datestring = 'yesterday'
        elif self.last_saved.date() >= monday:
            datestring = self.last_saved.strftime('%a')
        elif self.last_saved.year == today.year:
            datestring = self.last_saved.strftime('%d %b')
        else:
            datestring = self.last_saved.strftime('%d %b %Y')
        self.last_save.set_text(datestring)
        self.changed()
        
    def set_folder(self, new_folder):
        self.folder.set_text(helpers.shorten_folder(new_folder, 18))
        

