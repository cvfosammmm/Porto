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

import model.model_cell as model_cell


class HeaderbarControlsController(object):

    def __init__(self, worksheet, view):
        self.worksheet = worksheet
        self.view = view
        self.view.add_codecell_button.connect('clicked', self.on_add_codecell_button_click)
        self.view.add_markdowncell_button.connect('clicked', self.on_add_markdowncell_button_click)
        self.view.down_button.connect('clicked', self.on_down_button_click)
        self.view.up_button.connect('clicked', self.on_up_button_click)
        self.view.delete_button.connect('clicked', self.on_delete_button_click)
        self.view.eval_button.connect('clicked', self.on_eval_button_click)
        self.view.eval_nc_button.connect('clicked', self.on_eval_nc_button_click)
        self.view.stop_button.connect('clicked', self.on_stop_button_click)

    def on_add_codecell_button_click(self, button_object=None):
        self.worksheet.add_codecell_below_active_cell()
                
    def on_add_markdowncell_button_click(self, button_object=None):
        self.worksheet.add_markdowncell_below_active_cell()
                
    def on_down_button_click(self, button_object=None):
        self.worksheet.move_cell_down()

    def on_up_button_click(self, button_object=None):
        self.worksheet.move_cell_up()
            
    def on_delete_button_click(self, button_object=None):
        self.worksheet.delete_active_cell()
            
    def on_eval_button_click(self, button_object=None):
        self.worksheet.evaluate_active_cell()

    def on_eval_nc_button_click(self, button_object=None):
        self.worksheet.evaluate_active_cell_and_go_to_next()
            
    def on_stop_button_click(self, button_object=None):
        self.worksheet.stop_evaluation()


