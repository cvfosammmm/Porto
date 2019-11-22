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
gi.require_version('GtkSource', '3.0')
from gi.repository import GtkSource

import result_factory.result_factory as result_factory
from helpers.observable import Observable
import backend.backend_markdown as backend_markdown
import cell.cell_controller as cell_controller
import cell.cell_viewgtk as cell_view


class Cell(GtkSource.Buffer, Observable):

    def __init__(self, worksheet):
        GtkSource.Buffer.__init__(self)
        Observable.__init__(self)

        self.worksheet = worksheet
        self.worksheet_position = None

        self.set_modified(False)
        self.set_highlight_matching_brackets(False)

        self.result_blob = None
        self.result = None

    def first_set_text(self, text, activate=False, set_unmodified=True):
        self.set_text(text)
        self.place_cursor(self.get_start_iter())
        if activate == True:
            self.worksheet.set_active_cell(self)
        if set_unmodified == True:
            self.set_modified(False)

    def get_all_text(self):
        return self.get_text(self.get_start_iter(), self.get_end_iter(), False)
        
    def stop_evaluation(self):
        if self.state != 'idle':
            self.change_state('evaluation_to_stop')

    def set_result_blob(self, result_blob):
        self.result_blob = result_blob
        
    def set_result(self, result, show_animation=True):
        ''' set new result object. '''

        self.result = result
        self.add_change_code('new_result', {'result': self.result, 'show_animation': show_animation})
        self.set_modified(True)
        
    def get_result(self):
        return self.result
        
    def remove_result(self, show_animation=True):
        ''' remove result including all of it's assets. '''
        
        self.result = None
        self.add_change_code('new_result', {'result': self.result, 'show_animation': show_animation})
        self.set_modified(True)
    
    def get_worksheet(self):
        return self.worksheet

    def get_worksheet_position(self):
        cells = self.get_worksheet().cells
        try: position = cells.index(self)
        except ValueError: return self.worksheet_position
        else: 
            self.worksheet_position = position
            return position
        
    def is_active_cell(self):
        return True if self.get_worksheet().get_active_cell() == self else False
        

class CodeCell(Cell):

    def __init__(self, worksheet):
        Cell.__init__(self, worksheet)
        
        # possible states: idle, ready_for_evaluation, queued_for_evaluation
        # evaluation_in_progress, evaluation_to_stop
        self.state = 'idle'
        
        # syntax highlighting
        self.set_language(self.get_worksheet().get_source_language_code())
        self.set_style_scheme(self.get_worksheet().get_source_style_scheme())

        self.view = cell_view.CellViewCode(self)
        self.controller = cell_controller.CodeCellController(self, self.view, worksheet.controller)

    def evaluate(self):
        self.remove_result()
        self.stop_evaluation()
        self.change_state('ready_for_evaluation')

    def parse_result_blob(self):
        text = self.result_blob.get('text/plain', None)
        image = self.result_blob.get('image/png', None)

        if image != None:
            self.set_result(result_factory.ResultImage(image))

        elif text != None:
            self.set_result(result_factory.ResultText(text))

    def change_state(self, state):
        self.state = state
        self.add_change_code('cell_state_change', self.state)
        
        # promote info to associated worksheet
        if self.state != 'idle':
            self.worksheet.add_busy_cell(self)
        else:
            self.worksheet.remove_busy_cell(self)
            

class MarkdownCell(Cell):

    def __init__(self, worksheet):
        Cell.__init__(self, worksheet)

        # possible states: edit, display, ready_for_evaluation, queued_for_evaluation
        # evaluation_in_progress, evaluation_to_stop
        self.state = 'edit'
        
        # syntax highlighting
        self.set_language(self.get_worksheet().get_source_language_markdown())
        self.set_style_scheme(self.get_worksheet().get_source_style_scheme())

        self.view = cell_view.CellViewMarkdown(self)
        self.controller = cell_controller.MarkdownCellController(self, self.view, worksheet.controller)

    def evaluate(self):
        self.remove_result()
        self.stop_evaluation()
        self.change_state('ready_for_evaluation')

    def evaluate_now(self):
        result_blob = backend_markdown.evaluate_markdown(self.get_all_text())
        self.set_result_blob(result_blob)
        self.parse_result_blob()

    def parse_result_blob(self):
        self.set_result(result_factory.MarkdownResult(self.result_blob))

    def change_state(self, state):
        self.state = state
        self.add_change_code('cell_state_change', self.state)
        
        # promote info to associated worksheet
        if self.state != 'edit' and self.state != 'display':
            self.worksheet.add_busy_cell(self)
        else:
            self.worksheet.remove_busy_cell(self)
            

