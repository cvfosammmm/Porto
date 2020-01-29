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


class NotebookListItemPresenter(object):

    def __init__(self, notebook, item, sb_view, hb_view):
        self.notebook = notebook
        self.sb_view = sb_view
        self.hb_view = hb_view
        self.item = item
        self.item.register_observer(self)
        self.notebook.register_observer(self)
        self.update_subtitle()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'icon_changed':
            self.update_kernel_icon()

        if change_code == 'kernel_state_changed':
            self.update_subtitle()

        if change_code == 'busy_cell_count_changed':
            self.update_subtitle()

        if change_code == 'save_state_change':
            self.update_title()
            self.sb_view.set_last_saved(self.notebook.get_last_saved())
            self.hb_view.set_last_saved(self.notebook.get_last_saved())

        if change_code == 'pathname_changed':
            self.update_title()
            self.sb_view.set_last_saved(self.notebook.get_last_saved())
            self.hb_view.set_last_saved(self.notebook.get_last_saved())

    def update_title(self):
        save_state = '*' if self.notebook.get_save_state() == 'modified' else ''
        self.sb_view.set_name(save_state + self.notebook.get_name())
        self.hb_view.set_name(save_state + self.notebook.get_name())

    def update_subtitle(self):
        busy_cell_count = self.notebook.get_busy_cell_count()
        if busy_cell_count > 0:
            plural = 's' if busy_cell_count > 1 else ''
            subtitle = 'evaluating ' + str(busy_cell_count) + ' cell' + plural + '.'
        elif self.notebook.get_kernel_state() == 'starting':
            subtitle = 'starting kernel.'
        else:
            subtitle = 'idle.'
        self.sb_view.state.set_text(subtitle)
        self.hb_view.state.set_text(subtitle)
            
    def update_kernel_icon(self):
        if self.sb_view.icon_normal != None: self.sb_view.icon_stack.remove(self.sb_view.icon_normal)
        if self.sb_view.icon_active != None: self.sb_view.icon_stack.remove(self.sb_view.icon_active)
        self.sb_view.icon_normal = self.item.sb_icon_normal
        self.sb_view.icon_active = self.item.sb_icon_active
        self.sb_view.icon_stack.add_named(self.sb_view.icon_normal, 'normal')
        self.sb_view.icon_stack.add_named(self.sb_view.icon_active, 'active')
        self.sb_view.show_all()
        if self.sb_view.icon_type != None:
            self.sb_view.set_icon_type(self.sb_view.icon_type)

        if self.hb_view.icon_normal != None: self.hb_view.icon_stack.remove(self.hb_view.icon_normal)
        if self.hb_view.icon_active != None: self.hb_view.icon_stack.remove(self.hb_view.icon_active)
        self.hb_view.icon_normal = self.item.hb_icon_normal
        self.hb_view.icon_active = self.item.hb_icon_active
        self.hb_view.icon_stack.add_named(self.hb_view.icon_normal, 'normal')
        self.hb_view.icon_stack.add_named(self.hb_view.icon_active, 'active')
        self.hb_view.show_all()
        if self.hb_view.icon_type != None:
            self.hb_view.set_icon_type(self.hb_view.icon_type)


