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

import notebook.backend.backend_code as backend_code
import notebook.backend.backend_markdown as backend_markdown
import cell.cell as cell_model
from app.service_locator import ServiceLocator


class NotebookEvaluator(object):

    def __init__(self, notebook):
        self.notebook = notebook
        self.notebook.register_observer(self)

        self.result_factory = ServiceLocator.get_result_factory()

        self.backend_code = backend_code.BackendCode()
        self.backend_code.register_observer(self)

        self.markdown_compute_queue = backend_markdown.ComputeQueue()
        self.markdown_compute_queue.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'kernel_state_changed' and parameter == 'kernel_to_start':
            self.backend_code.start_kernel(self.notebook)
            self.notebook.set_kernel_state('starting')

        '''if change_code == 'set_pretty_print':
            value = parameter
            self.compute_queue.set_pretty_print(value)'''
            
        if change_code == 'kernel_started':
            self.notebook.set_kernel_state('running')
            
        if change_code == 'kernel_to_restart':
            self.backend_code.restart(self.notebook)
            self.notebook.set_kernel_state('starting')
        
        if change_code == 'kernel_to_shutdown':
            self.backend_code.shutdown(self.notebook)
        
        if change_code == 'kernel_to_shutdown_now':
            self.backend_code.shutdown_now()
        
        if change_code == 'nb_evaluation_to_stop':
            self.backend_code.stop_evaluation(self.notebook)
        
        if change_code == 'cell_state_change' and parameter == 'ready_for_evaluation':
            cell = notifying_object
            if isinstance(cell, cell_model.MarkdownCell):
                query_string = cell.get_text(cell.get_start_iter(), cell.get_end_iter(), False)
                query = backend_markdown.MarkdownQuery(self.notebook, cell, query_string)
                self.markdown_compute_queue.add_query(query)
            else:
                self.backend_code.run_cell(self.notebook, cell)

        if change_code == 'cell_state_change' and parameter == 'ready_for_evaluation_quickly_please':
            cell = notifying_object
            if isinstance(cell, cell_model.MarkdownCell):
                result_blob = backend_markdown.evaluate_markdown(cell.get_all_text())
                cell.set_result(self.result_factory.get_markdown_result_from_blob(result_blob))
            else:
                self.backend_code.run_cell(self.notebook, cell)

        if change_code == 'cell_state_change' and parameter == 'evaluation_to_stop':
            cell = notifying_object
            if isinstance(cell, cell_model.MarkdownCell):
                self.markdown_compute_queue.stop_evaluation_by_cell(cell)
            else:
                self.backend_code.stop_evaluation_of_cell(self.notebook, cell)

        if change_code == 'query_queued':
            cell = parameter.cell
            cell.change_state('queued_for_evaluation')
    
        if change_code == 'evaluation_started':
            cell = parameter.cell
            cell.change_state('evaluation_in_progress')

        if change_code == 'evaluation_result':
            cell = parameter['cell']
            cell.set_result(parameter['result'])
            cell.change_state('idle')

        if change_code == 'cell_evaluation_stopped':
            cell = parameter
            if isinstance(cell, cell_model.MarkdownCell):
                cell.change_state('edit')
            else:
                cell.change_state('idle')
                self.notebook.set_kernel_state('running')

        if change_code == 'evaluation_finished':
            result_blob = parameter
            result = self.result_factory.get_markdown_result_from_blob(result_blob['result_blob'])
            result_blob['cell'].set_result(result)
            result_blob['cell'].change_state('display')


