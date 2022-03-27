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
gi.require_version('GtkSource', '4')
from gi.repository import GLib
from gi.repository import GtkSource
import datetime
import os, os.path
import nbformat

import notebook.notebook_viewgtk as notebook_viewgtk
import notebook.notebook_controller as notebook_controller
import notebook.notebook_presenter as notebook_presenter
import notebook.notebook_evaluator as notebook_evaluator
import notebook.notebook_list_item.notebook_list_item as list_item_model
import notebook.headerbar_controls.headerbar_controls as headerbar_controls
import cell.cell as model_cell
from helpers.observable import Observable
from app.service_locator import ServiceLocator


class Notebook(Observable):

    def __init__(self, pathname):
        Observable.__init__(self)

        self.pathname = pathname
        self.kernelname = None
        self.cells = []
        self.active_cell = None
        self.busy_cells = set()
        self.modified_cells = set()
        self.kernel_state = None
        self.result_factory = ServiceLocator.get_result_factory()

        self.save_state = 'saved'
        try: self.last_saved = datetime.datetime.fromtimestamp(os.path.getmtime(pathname))
        except FileNotFoundError:
            self.last_saved = datetime.datetime.fromtimestamp(0)
        
        # set source language for syntax highlighting
        self.source_language_manager = GtkSource.LanguageManager()
        self.source_language_manager.set_search_path((os.path.dirname(__file__) + '/../resources/gtksourceview/language-specs',))
        self.source_language_code = self.source_language_manager.get_language('sage')
        self.source_language_markdown = self.source_language_manager.get_language('markdown')
        
        self.source_style_scheme_manager = GtkSource.StyleSchemeManager()
        self.source_style_scheme_manager.set_search_path((os.path.dirname(__file__) + '/../resources/gtksourceview/styles',))
        self.source_style_scheme = self.source_style_scheme_manager.get_scheme('sage')

        self.cursor_position = {'cell': None, 'cell_position': None, 'cell_size': None, 'position': None}

        self.list_item = list_item_model.NotebookListItem(self)
        self.view = notebook_viewgtk.NotebookView()
        self.presenter = notebook_presenter.NotebookPresenter(self, self.view)
        self.controller = notebook_controller.NotebookController(self, self.view)
        self.evaluator = notebook_evaluator.NotebookEvaluator(self)
        self.headerbar_controls = headerbar_controls.HeaderbarControls(self)

    def remove_all_cells(self):
        while len(self.cells) > 0:
            self.remove_cell(self.cells[0])
        
    def create_cell(self, position='last', text='', activate=False, set_unmodified=True):
        ''' Creates a code cell, then adds it to notebook. '''
        
        if position == 'last': position = len(self.cells)
        new_cell = model_cell.CodeCell(self)
        if text == '': new_cell.set_text(' ')
        self.add_cell(new_cell, position)
        GLib.idle_add(lambda: new_cell.first_set_text(text, activate, set_unmodified))
        return new_cell
        
    def create_markdowncell(self, position='last', text='', activate=False, set_unmodified=True):
        ''' Creates a text cell, then adds it to notebook. '''
        
        if position == 'last': position = len(self.cells)
        new_cell = model_cell.MarkdownCell(self)
        if text == '': new_cell.set_text(' ')
        self.add_cell(new_cell, position)
        #GLib.idle_add(lambda: new_cell.first_set_text(text, activate, set_unmodified))
        new_cell.first_set_text(text, activate, set_unmodified)
        return new_cell
        
    def add_cell(self, cell, position='last'):
        ''' Adds cell object to notebook. '''

        if position == 'last': position = len(self.cells)
        self.cells.insert(position, cell)
        self.add_change_code('new_cell', cell)
        self.set_save_state('modified')
        cell.connect('modified-changed', self.on_modified_changed)
    
    def move_cell(self, position, new_position):
        ''' Move cell '''
        
        if len(self.cells) > max(position, new_position):
            self.cells[position], self.cells[new_position] = self.cells[new_position], self.cells[position]
            #self.cells[position].get_notebook_position()
            #self.cells[new_position].get_notebook_position()
            self.add_change_code('cell_moved', {'position': position, 'new_position': new_position})
            self.set_save_state('modified')
        
    def on_modified_changed(self, cell):
        if cell.get_modified() == True:
            self.add_modified_cell(cell)
        else:
            self.remove_modified_cell(cell)
        if self.get_modified_cell_count() > 0:
            self.set_save_state('modified')
        else:
            self.set_save_state('saved')
    
    def remove_cell(self, cell):
        try: index = self.cells.index(cell)
        except ValueError: pass
        else:
            self.cells[index].stop_evaluation()
            del(self.cells[index])
            self.add_change_code('deleted_cell', cell)
            self.set_save_state('modified')
            if len(self.cells) == 0:
                self.active_cell = None
    
    def set_active_cell(self, cell):
        if not self.active_cell == None: self.add_change_code('new_inactive_cell', self.active_cell)
        self.active_cell = cell
        self.add_change_code('new_active_cell', cell)
    
    def get_active_cell(self):
        return self.active_cell
    
    def get_next_cell(self, cell):
        try: lindex = self.cells.index(cell)
        except ValueError: return None
        else:
            try: return self.cells[lindex+1]
            except IndexError: return None
    
    def get_next_visible_cell(self, cell):
        try: lindex = self.cells.index(cell)
        except ValueError: return None
        else:
            while lindex < (len(self.cells)-1) and not isinstance(self.cells[lindex+1], model_cell.CodeCell) \
                and not (isinstance(self.cells[lindex+1], model_cell.MarkdownCell) and self.cells[lindex+1].get_result() == None):
                lindex += 1 
            try: return self.cells[lindex+1]
            except IndexError: return None
    
    def get_prev_cell(self, cell):
        try: lindex = self.cells.index(cell)
        except ValueError: return None
        else: return self.cells[lindex-1] if lindex > 0 else None
    
    def get_prev_visible_cell(self, cell):
        try: lindex = self.cells.index(cell)
        except ValueError: return None
        else:
            while lindex > 0 and not isinstance(self.cells[lindex-1], model_cell.CodeCell) and not (isinstance(self.cells[lindex-1], model_cell.MarkdownCell) and self.cells[lindex-1].get_result() == None):
                lindex -= 1 
            return self.cells[lindex-1] if lindex > 0 else None
    
    def get_cell_count(self):
        return len(self.cells)

    def load_from_disk(self):
        nb = nbformat.read(self.pathname, nbformat.current_nbformat)
        if self.get_cell_count() == 0:
            kernelname = nb.metadata['kernelspec']['name']
            if not ServiceLocator.get_kernelspecs().is_installed(kernelname):
                raise KernelMissing(kernelname)
            self.set_kernelname(kernelname)
            self.set_kernel_state('kernel_to_start')
            is_first_cell = True
            for cell in nb.cells:
                if cell.cell_type == 'markdown':
                    new_cell = self.create_markdowncell('last', cell.source)
                    try: in_edit_mode = cell.metadata['in_edit_mode']
                    except KeyError: in_edit_mode = False
                    if len(cell.source) > 0 and in_edit_mode == False:
                        new_cell.evaluate_now()
                elif cell.cell_type == 'code':
                    new_cell = self.create_cell('last', cell.source)
                    if is_first_cell == True:
                        is_first_cell = False
                        self.set_active_cell(new_cell)
                    for output in cell.outputs:
                        if output['output_type'] == 'error':
                            result = self.result_factory.get_error_from_nbformat_dict(output)
                            new_cell.set_result(result)
                        elif output['output_type'] == 'execute_result' or output['output_type'] == 'display_data':
                            try: data = output['data']
                            except KeyError: pass
                            else:
                                result = self.result_factory.get_result_from_blob(data)
                                new_cell.set_result(result)
                        elif output['output_type'] == 'stream':
                            new_cell.add_to_stream(output['name'], output['text'])
        self.set_save_state('saved')
        
    def save_to_disk(self):
        try: filehandle = open(self.pathname, 'w+')
        except IOError: pass
        else:
            nb = nbformat.v4.new_notebook()
            for cell in self.cells:
                if isinstance(cell, model_cell.CodeCell):
                    cell_node = nbformat.v4.new_code_cell(
                        source=cell.get_all_text(),
                        execution_count=0
                    )
                    outputs = list()
                    for stream in cell.get_streams():
                        outputs.append(stream.export_nbformat())
                    result = cell.get_result()
                    if result != None:
                        outputs.append(result.export_nbformat())
                    if len(outputs):
                        cell_node.outputs = outputs

                elif isinstance(cell, model_cell.MarkdownCell):
                    result = cell.get_result()
                    metadata = {'in_edit_mode': (result == None)}
                    cell_node = nbformat.v4.new_markdown_cell(
                        source=cell.get_all_text(),
                        metadata=metadata
                    )
                nb.cells.append(cell_node)

            kernelspec_meta = {'name': self.kernelname, 'display_name': self.kernelname, 'language': self.kernelname}
            nb.metadata['kernelspec'] = kernelspec_meta
            nbformat.write(nb, filehandle)
            self.last_saved = datetime.datetime.now()
            self.reset_modified_cells()               
            self.set_save_state('saved')
            filehandle.close()

    def remove_from_disk(self):
        os.remove(self.pathname)

    def save_as(self, new_path):
        self.set_pathname(new_path)
        self.save_to_disk()

    def set_save_state(self, state):
        if self.save_state != state:
            self.save_state = state
            self.add_change_code('save_state_change', self.save_state)
            
        if self.save_state == 'saved':
            for cell in self.cells:
                cell.set_modified(False)
        
    def get_save_state(self):
        return self.save_state
        
    def get_pathname(self):
        return self.pathname
    
    def set_pathname(self, pathname):
        old_path = self.pathname
        self.pathname = pathname
        self.add_change_code('pathname_changed', old_path)

    def get_kernelname(self):
        return self.kernelname
    
    def set_kernelname(self, kernelname):
        if kernelname != self.kernelname:
            self.kernelname = kernelname
            self.set_save_state('modified')
            self.list_item.set_kernel(kernelname)
            self.add_change_code('kernelname_changed')

    def get_cells_in_order(self):
        pass
        
    def get_source_language_code(self):
        return self.source_language_code
        
    def get_source_language_markdown(self):
        return self.source_language_markdown
        
    def get_source_style_scheme(self):
        return self.source_style_scheme
        
    def get_name(self):
        return self.pathname.split('/')[-1].replace('.ipynb', '')
        
    def get_folder(self):
        return '/'.join(self.pathname.split('/')[:-1])
        
    def get_last_saved(self):
        return self.last_saved
        
    def set_kernel_state(self, state):
        if self.kernel_state != state:
            self.kernel_state = state
            self.add_change_code('kernel_state_changed', self.kernel_state)
    
    def get_kernel_state(self):
        return self.kernel_state
        
    def restart_kernel(self):
        self.add_change_code('kernel_to_restart', None)

    def shutdown_kernel(self):
        self.add_change_code('kernel_to_shutdown', None)

    def shutdown_kernel_now(self):
        self.add_change_code('kernel_to_shutdown_now', None)

    def evaluate_active_cell(self):
        active_cell = self.active_cell
        if not (isinstance(active_cell, model_cell.MarkdownCell) and active_cell.get_result() != None):
            active_cell.evaluate()

    def evaluate_active_cell_and_go_to_next(self):
        active_cell = self.active_cell
        if not (isinstance(active_cell, model_cell.MarkdownCell) and active_cell.get_result() != None):
            active_cell.evaluate()

        new_active_cell = self.get_next_visible_cell(active_cell)
        if not new_active_cell == None:
            self.set_active_cell(new_active_cell)
            new_active_cell.place_cursor(new_active_cell.get_start_iter())
        else:
            self.create_cell()
            new_active_cell = self.get_next_visible_cell(active_cell)
            self.set_active_cell(new_active_cell)
            new_active_cell.place_cursor(new_active_cell.get_start_iter())

    def add_codecell_below_active_cell(self):
        position = self.get_active_cell().get_notebook_position() + 1
        self.create_cell(position, '', activate=True, set_unmodified=False)

    def add_markdowncell_below_active_cell(self):
        position = self.get_active_cell().get_notebook_position() + 1
        self.create_markdowncell(position, '', activate=True, set_unmodified=False)

    def move_cell_down(self):
        position = self.get_active_cell().get_notebook_position()
        cell_count = self.get_cell_count()
        if position < cell_count:
            self.move_cell(position, position + 1)

    def move_cell_up(self):
        position = self.get_active_cell().get_notebook_position()
        cell_count = self.get_cell_count()
        if position > 0:
            self.move_cell(position, position - 1)

    def delete_active_cell(self):
        cell = self.get_active_cell()
        prev_cell = self.get_prev_cell(cell)
        if prev_cell != None: 
            cell.remove_result()
            self.set_active_cell(prev_cell)
            #prev_cell.place_cursor(prev_cell.get_iter_at_line(prev_cell.get_line_count() - 1))
            prev_cell.place_cursor(prev_cell.get_start_iter())
            self.remove_cell(cell)
        else:
            next_cell = self.get_next_cell(cell)
            if next_cell != None:
                cell.remove_result()
                self.set_active_cell(next_cell)
                next_cell.place_cursor(next_cell.get_start_iter())
                self.remove_cell(cell)
            else:
                cell.remove_result()
                self.remove_cell(cell)
                self.create_cell('last', '', activate=True)

    def stop_evaluation(self):
        self.add_change_code('nb_evaluation_to_stop', None)
        
    def add_busy_cell(self, cell):
        self.busy_cells.add(cell)
        self.add_change_code('busy_cell_count_changed', self.get_busy_cell_count())
        
    def remove_busy_cell(self, cell):
        self.busy_cells.discard(cell)
        self.add_change_code('busy_cell_count_changed', self.get_busy_cell_count())

    def get_busy_cell_count(self):
        return len(self.busy_cells)

    def add_modified_cell(self, cell):
        self.modified_cells.add(cell)
        
    def remove_modified_cell(self, cell):
        self.modified_cells.discard(cell)

    def reset_modified_cells(self):
        self.modified_cells = set()

    def get_modified_cell_count(self):
        return len(self.modified_cells)


class KernelMissing(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


