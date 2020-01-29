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


class HeaderbarControlsController(object):

    def __init__(self, notebook, button_box, save_button):
        self.notebook = notebook
        self.button_box = button_box
        self.save_button = save_button
        self.button_box.add_codecell_button.connect('clicked', self.on_add_codecell_button_click)
        self.button_box.add_markdowncell_button.connect('clicked', self.on_add_markdowncell_button_click)
        self.button_box.down_button.connect('clicked', self.on_down_button_click)
        self.button_box.up_button.connect('clicked', self.on_up_button_click)
        self.button_box.delete_button.connect('clicked', self.on_delete_button_click)
        self.button_box.eval_button.connect('clicked', self.on_eval_button_click)
        self.button_box.eval_nc_button.connect('clicked', self.on_eval_nc_button_click)
        self.button_box.stop_button.connect('clicked', self.on_stop_button_click)
        self.save_button.connect('clicked', self.on_save_ws_button_click)

    def on_add_codecell_button_click(self, button_object=None):
        self.notebook.add_codecell_below_active_cell()
                
    def on_add_markdowncell_button_click(self, button_object=None):
        self.notebook.add_markdowncell_below_active_cell()
                
    def on_down_button_click(self, button_object=None):
        self.notebook.move_cell_down()

    def on_up_button_click(self, button_object=None):
        self.notebook.move_cell_up()
            
    def on_delete_button_click(self, button_object=None):
        self.notebook.delete_active_cell()
            
    def on_eval_button_click(self, button_object=None):
        self.notebook.evaluate_active_cell()

    def on_eval_nc_button_click(self, button_object=None):
        self.notebook.evaluate_active_cell_and_go_to_next()
            
    def on_stop_button_click(self, button_object=None):
        self.notebook.stop_evaluation()

    def on_save_ws_button_click(self, button_object=None):
        self.notebook.save_to_disk()
        

