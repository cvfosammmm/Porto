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

from helpers.observable import Observable
from app.service_locator import ServiceLocator
import cell.cell_controller as cell_controller
import cell.cell_presenter as cell_presenter
import cell.cell_viewgtk as cell_view
import cell.result_revealer.result_revealer as result_revealer


class Cell(GtkSource.Buffer, Observable):

    def __init__(self, notebook):
        GtkSource.Buffer.__init__(self)
        Observable.__init__(self)

        self.notebook = notebook
        self.notebook_position = None

        self.set_modified(False)
        self.set_highlight_matching_brackets(False)

    def first_set_text(self, text, activate=False, set_unmodified=True):
        self.begin_not_undoable_action()
        self.set_text(text)
        self.place_cursor(self.get_start_iter())
        if activate == True:
            self.notebook.set_active_cell(self)
        if set_unmodified == True:
            self.set_modified(False)
        self.end_not_undoable_action()

    def get_all_text(self):
        return self.get_text(self.get_start_iter(), self.get_end_iter(), False)
        
    def stop_evaluation(self):
        if self.state != 'idle':
            self.change_state('evaluation_to_stop')

    def reset_streams(self):
        self.result_revealer.reset_streams()
        self.set_modified(True)

    def add_to_stream(self, stream_type, text):
        self.result_revealer.add_to_stream(stream_type, text)
        self.set_modified(True)

    def set_result(self, result, show_animation=True):
        self.result_revealer.set_result(result, show_animation)
        self.set_modified(True)
        
    def get_result(self):
        return self.result_revealer.get_result()

    def get_streams(self):
        return self.result_revealer.streams.values()
        
    def remove_result(self, show_animation=True):
        self.result_revealer.remove_result(show_animation)
        self.set_modified(True)
    
    def get_notebook(self):
        return self.notebook

    def get_notebook_position(self):
        cells = self.get_notebook().cells
        try: position = cells.index(self)
        except ValueError: return self.notebook_position
        else: 
            self.notebook_position = position
            return position
        
    def is_active_cell(self):
        return True if self.get_notebook().get_active_cell() == self else False
        

class CodeCell(Cell):

    def __init__(self, notebook):
        Cell.__init__(self, notebook)
        self.register_observer(notebook.evaluator)

        # possible states: idle, ready_for_evaluation, queued_for_evaluation
        # evaluation_in_progress, evaluation_to_stop
        self.state = 'idle'
        
        # syntax highlighting
        self.set_language(self.get_notebook().get_source_language_code())
        self.set_style_scheme(self.get_notebook().get_source_style_scheme())

        self.view = cell_view.CellViewCode(self)
        self.result_revealer = result_revealer.CodeResultRevealer(self)
        self.presenter = cell_presenter.CodeCellPresenter(self)
        self.controller = cell_controller.CodeCellController(self, self.view, notebook)

    def evaluate(self):
        self.reset_streams()
        self.remove_result()
        self.stop_evaluation()
        self.change_state('ready_for_evaluation')

    def change_state(self, state):
        self.state = state
        self.add_change_code('cell_state_change', self.state)
        
        # promote info to associated notebook
        if self.state != 'idle':
            self.notebook.add_busy_cell(self)
        else:
            self.notebook.remove_busy_cell(self)
            

class MarkdownCell(Cell):

    def __init__(self, notebook):
        Cell.__init__(self, notebook)
        self.register_observer(notebook.evaluator)

        # possible states: edit, display, ready_for_evaluation, queued_for_evaluation
        # evaluation_in_progress, evaluation_to_stop
        self.state = 'edit'
        
        # syntax highlighting
        self.set_language(self.get_notebook().get_source_language_markdown())
        self.set_style_scheme(self.get_notebook().get_source_style_scheme())

        self.view = cell_view.CellViewMarkdown(self)
        self.result_revealer = result_revealer.MarkdownResultRevealer(self)
        self.presenter = cell_presenter.MarkdownCellPresenter(self)
        self.controller = cell_controller.MarkdownCellController(self, self.view, notebook)

    def evaluate(self):
        self.remove_result()
        self.stop_evaluation()
        self.change_state('ready_for_evaluation')

    def evaluate_now(self):
        self.remove_result()
        self.stop_evaluation()
        self.change_state('ready_for_evaluation_quickly_please')

    def change_state(self, state):
        self.state = state
        self.add_change_code('cell_state_change', self.state)
        
        # promote info to associated notebook
        if self.state != 'edit' and self.state != 'display':
            self.notebook.add_busy_cell(self)
        else:
            self.notebook.remove_busy_cell(self)
            

