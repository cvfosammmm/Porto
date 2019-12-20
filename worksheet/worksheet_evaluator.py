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

import worksheet.backend.backend_code as backend_code
import worksheet.backend.backend_markdown as backend_markdown
import cell.cell as cell_model


class WorksheetEvaluator(object):

    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.worksheet.register_observer(self)

        self.backend_code = backend_code.BackendCode()
        self.backend_code.register_observer(self)

        self.markdown_compute_queue = backend_markdown.ComputeQueue()
        self.markdown_compute_queue.register_observer(self)

        self.worksheet.set_kernel_state('starting')
        self.backend_code.start_kernel(worksheet)

    def change_notification(self, change_code, notifying_object, parameter):

        '''if change_code == 'set_pretty_print':
            value = parameter
            self.compute_queue.set_pretty_print(value)'''
            
        if change_code == 'kernel_started':
            self.worksheet.set_kernel_state('running')
            
        if change_code == 'kernel_to_restart':
            self.backend_code.restart(self.worksheet)
            self.worksheet.set_kernel_state('starting')
        
        if change_code == 'kernel_to_shutdown':
            self.backend_code.shutdown(self.worksheet)
        
        if change_code == 'ws_evaluation_to_stop':
            self.backend_code.stop_evaluation(self.worksheet)
        
        if change_code == 'cell_state_change' and parameter == 'ready_for_evaluation':
            cell = notifying_object
            if isinstance(cell, cell_model.MarkdownCell):
                query_string = cell.get_text(cell.get_start_iter(), cell.get_end_iter(), False)
                query = backend_markdown.MarkdownQuery(self.worksheet, cell, query_string)
                self.markdown_compute_queue.add_query(query)
            else:
                self.backend_code.run_cell(self.worksheet, cell)
            
        if change_code == 'cell_state_change' and parameter == 'evaluation_to_stop':
            cell = notifying_object
            if isinstance(cell, cell_model.MarkdownCell):
                self.markdown_compute_queue.stop_evaluation_by_cell(cell)
            else:
                self.backend_code.stop_evaluation_of_cell(self.worksheet, cell)

        if change_code == 'query_queued':
            cell = parameter.cell
            cell.change_state('queued_for_evaluation')
    
        if change_code == 'evaluation_started':
            cell = parameter.cell
            cell.change_state('evaluation_in_progress')

        if change_code == 'evaluation_result':
            cell = parameter['cell']
            data = parameter['data']
            cell.change_state('idle')
            if data != None:
                cell.set_result_blob(data)
                cell.parse_result_blob()

        if change_code == 'cell_evaluation_stopped':
            cell = parameter
            if isinstance(cell, cell_model.MarkdownCell):
                cell.change_state('edit')
            else:
                cell.change_state('idle')
                self.worksheet.set_kernel_state('running')

        if change_code == 'evaluation_finished':
            result_blob = parameter
            result_blob['cell'].change_state('edit')
            result_blob['cell'].set_result_blob(result_blob['result_blob'])
            result_blob['cell'].parse_result_blob()
            result_blob['cell'].change_state('display')

