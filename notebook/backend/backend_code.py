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
from gi.repository import GObject

import jupyter_client
import _thread as thread
import queue
import time

from helpers.observable import Observable
from app.service_locator import ServiceLocator


class BackendCode(Observable):

    def __init__(self, notebook):
        Observable.__init__(self)
        self.kernel = None
        self.notebook = notebook
        self.continue_fetching = True
        self.result_factory = ServiceLocator.get_result_factory()
        self.fetch_func_id = GObject.timeout_add(50, self.fetch_results)

    def fetch_results(self):
        if self.kernel == None: return True

        result = self.kernel.get_result()
        if result:
            if result.result_message == 'evaluation_stopped':
                self.add_change_code('cell_evaluation_stopped', result.cell)

            elif result.result_msg != None and result.cell != None:
                result_msg = result.result_msg
                msg_type = result_msg['header']['msg_type']

                if msg_type == 'error':
                    result_object = self.result_factory.get_error_from_result_message(result_msg)
                    self.add_change_code('evaluation_result', {'cell': result.cell, 'result': result_object})

                if msg_type == 'execute_input' and result.cell != None:
                    self.add_change_code('evaluation_started', result)

                if msg_type == 'stream':
                    text = result_msg['content'].get('text', None)
                    stream_type = result_msg['content'].get('name', None)
                    if text != None and stream_type != None:
                        self.add_change_code('stream_output', {'cell': result.cell, 'text': text, 'stream_type': stream_type})

                if msg_type == 'execute_result':
                    data = result_msg['content'].get('data', None)
                    result_object = self.result_factory.get_result_from_blob(data)
                    self.add_change_code('evaluation_result', {'cell': result.cell, 'result': result_object})

                if msg_type == 'display_data':
                    data = result_msg['content'].get('data', None)
                    result_object = self.result_factory.get_result_from_blob(data)
                    self.add_change_code('evaluation_result', {'cell': result.cell, 'result': result_object})

                if msg_type == 'status':
                    if result_msg['content'].get('execution_state', '') == 'idle':
                        self.add_change_code('kernel_started')
                        if result.cell != None:
                            self.add_change_code('cell_evaluation_stopped', result.cell)
                    else:
                        print(result_msg['content'])
        return True

    def start_kernel(self):
        if self.kernel == None:
            self.kernel = Kernel(self.notebook.get_kernelname(), self.notebook.get_folder())
        self.add_change_code('kernel_started')

    def run_cell(self, cell):
        if self.kernel == None:
            self.start_kernel()
        query = Query(cell, cell.get_all_text().strip())
        self.kernel.add_query(query)
        self.add_change_code('query_queued', query)

    def stop_evaluation_of_cell(self, cell):
        if self.kernel != None:
            self.kernel.remove_queries_by_cell(cell)

    def stop_evaluation(self):
        if self.kernel != None:
            self.kernel.remove_all_queries()
            self.kernel.kernel_manager.interrupt_kernel()

    def shutdown_for_real(self):
        if self.notebook.get_busy_cell_count() == 0:
            if self.kernel != None:
                self.kernel.shutdown()
                self.kernel.kernel_manager.finish_shutdown()
                self.kernel = None
            return False
        return True

    def restart_for_real(self):
        if self.notebook.get_busy_cell_count() == 0:
            if self.kernel != None:
                self.kernel.shutdown()
                self.kernel.kernel_manager.finish_shutdown()
                self.kernel = None
            self.start_kernel()
            return False
        return True

    def shutdown(self):
        self.stop_evaluation()
        GObject.timeout_add(50, self.shutdown_for_real)

    def restart(self):
        self.stop_evaluation()
        shutdown_func_id = GObject.timeout_add(50, self.restart_for_real)

    def shutdown_now(self):
        if self.kernel != None:
            self.kernel.shutdown()
            self.kernel.kernel_manager.finish_shutdown()
            self.kernel = None


class Query():

    def __init__(self, cell, code):
        self.cell = cell
        self.code = code


class Kernel():

    def __init__(self, kernel_name, cwd):
        self.query_queue = list()
        self.query_queue_lock = thread.allocate_lock()
        self.active_queries = dict()
        self.active_queries_lock = thread.allocate_lock()
        self.result_queue = queue.Queue()
        self.kernel_name = kernel_name
        self.cwd = cwd
        self.kernel_started = False
        thread.start_new_thread(self.run_queries, ())

    def start_kernel(self):
        self.kernel_manager = jupyter_client.KernelManager()
        self.kernel_manager.kernel_name = self.kernel_name
        self.kernel_manager.start_kernel()
        self.client = self.kernel_manager.blocking_client()
        self.client.start_channels()
        try: self.client.wait_for_ready()
        except RuntimeError: pass
        else:
            query_id = self.client.comm_info()

            with self.active_queries_lock:
                self.active_queries[query_id] = None

            self.add_query(Query(None, 'import os'))
            self.add_query(Query(None, 'os.chdir("' + self.cwd + '")'))

    def start_fetching(self):
        thread.start_new_thread(self.fetch_results, ())

    def add_query(self, query):
        with self.query_queue_lock:
            self.query_queue.append(query)

    def get_result(self):
        try:
            result = self.result_queue.get(block=False)
        except queue.Empty:
            return None
        else:
            if result.query_id in self.active_queries:
                if result.result_msg['content'].get('execution_state', '') == 'idle':
                    del(self.active_queries[result.query_id])
                return result

    def run_queries(self):
        while True:
            time.sleep(0.05)
            with self.active_queries_lock:
                nothing_running = (len(self.active_queries) == 0)
            if not self.kernel_started:
                self.kernel_started = True
                self.start_kernel()
                self.start_fetching()
            elif nothing_running:
                with self.query_queue_lock:
                    try: query = self.query_queue.pop(0)
                    except IndexError: query = None
                if query != None:
                    query_id = self.client.execute(query.code)
                    with self.active_queries_lock:
                        self.active_queries[query_id] = query

    def remove_queries_by_cell(self, cell):
        with self.query_queue_lock:
            for query in self.query_queue:
                if query.cell == cell:
                    self.query_queue.remove(query)

        with self.active_queries_lock:
            del_ids = list()
            for query_id, query in self.active_queries.items():
                if query.cell == cell:
                    self.kernel_manager.interrupt_kernel()
                    del_ids.append(query_id)
            for query_id in del_ids:
                del(self.active_queries[query_id])

    def remove_all_queries(self):
        with self.query_queue_lock:
            queue_empty = (len(self.query_queue) == 0)
        while not queue_empty:
            with self.query_queue_lock:
                try: query = self.query_queue.pop(0)
                except IndexError: query = None
            if query != None:
                result = Result(query.cell)
                result.result_message = 'evaluation_stopped'
                self.result_queue.put(result)
                with self.query_queue_lock:
                    queue_empty = (len(self.query_queue) == 0)

    def fetch_results(self):
        while True:
            '''try: print(self.client.get_stdin_msg(timeout=0.1))
            except queue.Empty: pass
            try: print(self.client.get_shell_msg(timeout=0.1))
            except queue.Empty: pass'''
            try: result = self.client.get_iopub_msg(timeout=1)
            except queue.Empty: pass
            else:
                try: query_id = result['parent_header']['msg_id']
                except KeyError: pass
                else:
                    if result['parent_header']['msg_type'] == 'shutdown_request':
                        return
                    else:
                        with self.active_queries_lock:
                            if query_id in self.active_queries:
                                if self.active_queries[query_id] != None:
                                    cell = self.active_queries[query_id].cell
                                else:
                                    cell = None
                                result_object = Result(cell, query_id)
                                result_object.result_msg = result
                                self.result_queue.put(result_object)

    def shutdown(self):
        self.client.shutdown()


class Result():

    def __init__(self, cell, query_id=None):
        self.cell = cell
        self.query_id = query_id
        self.result_msg = None
        self.result_message = None


