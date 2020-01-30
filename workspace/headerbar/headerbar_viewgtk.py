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
from gi.repository import Gio

import workspace.recently_opened_notebooks_list.recently_opened_notebooks_list_viewgtk as viewgtk_notebook_list


class HeaderBar(Gtk.Paned):
    ''' Title bar of the app, contains always visible controls, 
        notebook title and state (computing, idle, ...) '''
        
    def __init__(self, button_layout):
        Gtk.Paned.__init__(self)
        
        show_close_button = True if (button_layout.find('close') < button_layout.find(':') and button_layout.find('close') >= 0) else False
        self.hb_left = HeaderBarLeft(show_close_button)
        
        show_close_button = True if (button_layout.find('close') > button_layout.find(':') and button_layout.find('close') >= 0) else False
        self.hb_right = HeaderBarRight(show_close_button)

        self.pack1(self.hb_left, False, False)
        self.pack2(self.hb_right, True, False)
        

class HeaderBarLeft(Gtk.HeaderBar):

    def __init__(self, show_close_button):
        Gtk.HeaderBar.__init__(self)

        self.set_show_close_button(show_close_button)

        self.create_buttons()

    def create_buttons(self):
        self.create_button = Gtk.Button.new_from_icon_name('document-new-symbolic', Gtk.IconSize.BUTTON)
        self.create_button.set_tooltip_text('Create new notebook')
        self.create_button.set_focus_on_click(False)
        self.create_button.set_action_name('win.create')
        self.pack_start(self.create_button)
        self.open_button = Gtk.Button.new_from_icon_name('document-open-symbolic', Gtk.IconSize.BUTTON)
        self.open_button.set_tooltip_text('Open notebook')
        self.open_button.set_focus_on_click(False)
        self.open_button.set_action_name('win.open')
        self.pack_start(self.open_button)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 250, 250
    

class HeaderBarRight(Gtk.HeaderBar):

    def __init__(self, show_close_button):
        Gtk.HeaderBar.__init__(self)

        self.set_show_close_button(show_close_button)
        self.props.title = ''
        self.open_notebooks_number = 0
        self.current_controls = None
        self.current_add_cell_box = None
        self.current_move_cell_box = None
        self.current_eval_box = None
        self.current_save_button = None

        self.welcome_title = Gtk.Label('Welcome to Porto')
        self.welcome_title.get_style_context().add_class('title')
        self.welcome_title.show_all()

        self.create_buttons()
        self.pack_buttons()

    def create_buttons(self):
        self.notebook_chooser = NotebookChooser()
        self.open_notebooks_button_label = Gtk.Label('Notebooks')
        self.open_notebooks_button_box = Gtk.HBox()
        self.open_notebooks_button_box.pack_start(Gtk.Image.new_from_icon_name('document-open-symbolic', Gtk.IconSize.MENU), False, False, 0)
        self.open_notebooks_button_box.pack_start(self.open_notebooks_button_label, False, False, 0)
        self.open_notebooks_button_box.pack_start(Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU), False, False, 0)
        self.open_notebooks_button = Gtk.MenuButton()
        self.open_notebooks_button.set_can_focus(False)
        self.open_notebooks_button.set_use_popover(True)
        self.open_notebooks_button.add(self.open_notebooks_button_box)
        self.open_notebooks_button.get_style_context().add_class("text-button")
        self.open_notebooks_button.get_style_context().add_class("image-button")
        self.open_notebooks_button.set_popover(self.notebook_chooser)

        self.create_full_hamburger_menu()
        self.create_blank_hamburger_menu()
        
    def create_full_hamburger_menu(self):
        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.BUTTON)
        self.menu_button.set_image(image)
        self.menu_button.set_focus_on_click(False)
        self.options_menu = Gio.Menu()

        kernel_section = Gio.Menu()
        item = Gio.MenuItem.new('Restart Language Kernel', 'win.restart_kernel')
        kernel_section.append_item(item)
        self.change_kernel_menu = Gio.Menu()
        kernel_section.append_submenu('Change Language', self.change_kernel_menu)

        save_section = Gio.Menu()
        item = Gio.MenuItem.new('Save As ...', 'win.save_as')
        save_section.append_item(item)
        item = Gio.MenuItem.new('Save All', 'win.save_all')
        save_section.append_item(item)

        notebook_section = Gio.Menu()
        item = Gio.MenuItem.new('Delete Notebook ...', 'win.delete')
        notebook_section.append_item(item)

        close_section = Gio.Menu()
        item = Gio.MenuItem.new('Close', 'win.close')
        close_section.append_item(item)
        item = Gio.MenuItem.new('Close All', 'win.close_all')
        close_section.append_item(item)

        self.options_menu.append_section(None, kernel_section)
        self.options_menu.append_section(None, save_section)
        self.options_menu.append_section(None, notebook_section)
        self.options_menu.append_section(None, close_section)

        view_section = Gio.Menu()
        view_menu = Gio.Menu()
        view_menu.append_item(Gio.MenuItem.new('Show Sidebar', 'win.toggle_sidebar'))
        view_section.append_submenu('View', view_menu)
        self.options_menu.append_section(None, view_section)
        preferences_section = Gio.Menu()
        item = Gio.MenuItem.new('Preferences', 'win.show_preferences_dialog')
        preferences_section.append_item(item)
        self.options_menu.append_section(None, preferences_section)
        meta_section = Gio.Menu()
        item = Gio.MenuItem.new('Keyboard Shortcuts', 'win.show_shortcuts_window')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('About', 'win.show_about_dialog')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('Quit', 'win.quit')
        meta_section.append_item(item)
        self.options_menu.append_section(None, meta_section)

        self.menu_button.set_menu_model(self.options_menu)

    def create_blank_hamburger_menu(self):
        self.blank_menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.BUTTON)
        self.blank_menu_button.set_image(image)
        self.blank_menu_button.set_focus_on_click(False)
        self.blank_options_menu = Gio.Menu()

        view_section = Gio.Menu()
        view_menu = Gio.Menu()
        view_menu.append_item(Gio.MenuItem.new('Show Sidebar', 'win.toggle_sidebar'))
        view_section.append_submenu('View', view_menu)
        self.blank_options_menu.append_section(None, view_section)
        preferences_section = Gio.Menu()
        item = Gio.MenuItem.new('Preferences', 'win.show_preferences_dialog')
        preferences_section.append_item(item)
        self.blank_options_menu.append_section(None, preferences_section)
        meta_section = Gio.Menu()
        item = Gio.MenuItem.new('Keyboard Shortcuts', 'win.show_shortcuts_window')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('About', 'win.show_about_dialog')
        meta_section.append_item(item)
        item = Gio.MenuItem.new('Quit', 'win.quit')
        meta_section.append_item(item)
        self.blank_options_menu.append_section(None, meta_section)

        self.blank_menu_button.set_menu_model(self.blank_options_menu)

    def pack_buttons(self):
        self.pack_start(self.open_notebooks_button)
        self.pack_end(self.menu_button)
        self.pack_end(self.blank_menu_button)
        self.show_all()

    def show_buttons(self):
        self.menu_button.show_all()
        self.blank_menu_button.hide()

    def hide_buttons(self):
        self.menu_button.hide()
        self.blank_menu_button.show_all()

    def increment_notebooks_number(self):
        self.open_notebooks_number += 1
        self.open_notebooks_button_label.set_text('Notebooks (' + str(self.open_notebooks_number) + ')')

    def decrement_notebooks_number(self):
        self.open_notebooks_number -= 1
        if self.open_notebooks_number == 0:
            self.open_notebooks_button_label.set_text('Notebooks')
        else:
            self.open_notebooks_button_label.set_text('Notebooks (' + str(self.open_notebooks_number) + ')')

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 763, 763


class NotebookChooser(Gtk.Popover):
    
    def __init__(self):
        Gtk.Popover.__init__(self)
        self.get_style_context().add_class('hb')
        self.set_size_request(300, -1)

        self.box = Gtk.VBox()

        self.open_notebooks_label_revealer = Gtk.Revealer()
        self.open_notebooks_label = Gtk.Label('Open Notebooks')
        self.open_notebooks_label.set_xalign(0)
        self.open_notebooks_label.get_style_context().add_class('nblist_header')
        self.open_notebooks_label_revealer.add(self.open_notebooks_label)
        self.open_notebooks_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.get_style_context().add_class('nblist_top')

        self.recent_notebooks_list_view = viewgtk_notebook_list.NotebookListRecentView()
        self.recent_notebooks_list_view.set_selection_mode(Gtk.SelectionMode.NONE)
        self.recent_notebooks_list_view.set_can_focus(False)
        self.recent_notebooks_label_revealer = Gtk.Revealer()
        self.recent_notebooks_label = Gtk.Label('Recently Opened Notebooks')
        self.recent_notebooks_label.set_xalign(0)
        self.recent_notebooks_label.get_style_context().add_class('nblist_header')
        self.recent_notebooks_label_revealer.add(self.recent_notebooks_label)
        self.recent_notebooks_label_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)

        self.open_notebooks_list_view_wrapper = Gtk.ScrolledWindow()
        self.open_notebooks_list_view_wrapper.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.recent_notebooks_list_view_wrapper = Gtk.ScrolledWindow()
        self.recent_notebooks_list_view_wrapper.add(self.recent_notebooks_list_view)
        self.recent_notebooks_list_view_wrapper.set_size_request(-1, 247)
        
        self.box.pack_start(self.open_notebooks_label_revealer, False, False, 0)
        self.box.pack_start(self.open_notebooks_list_view_wrapper, False, False, 0)
        self.box.pack_start(self.recent_notebooks_label_revealer, False, False, 0)
        self.box.pack_start(self.recent_notebooks_list_view_wrapper, True, True, 0)

        self.button_box = Gtk.HBox()
        self.button_box.get_style_context().add_class('linked')
        self.button_box.set_margin_top(12)
        self.button_box.set_margin_bottom(3)
        self.create_button = Gtk.Button.new_with_label('Create Notebook')
        self.create_button.set_action_name('win.create')
        self.open_button = Gtk.Button.new_with_label('Open Notebook')
        self.open_button.set_action_name('win.open')
        self.button_box.pack_start(self.open_button, False, False, 0)
        self.button_box.pack_start(self.create_button, False, False, 0)
        self.box.pack_start(self.button_box, False, False, 0)

        self.box.show_all()
        self.add(self.box)


