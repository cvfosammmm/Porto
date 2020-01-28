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

    def __init__(self):
        Observable.__init__(self)
        self.kernels = dict()
        self.continue_fetching = True
        self.result_factory = ServiceLocator.get_result_factory()
        self.fetch_func_id = GObject.timeout_add(50, self.fetch_results)

    def fetch_results(self):
        for kernel in self.kernels.values():
            result = kernel.get_result()
            if result:
                if result.result_message == 'evaluation_stopped':
                    self.add_change_code('cell_evaluation_stopped', result.cell)

                elif len(result.result_list) > 0:
                    for result_msg in result.result_list:
                        msg_type = result_msg['header']['msg_type']

                        if msg_type == 'error':
                            result_object = self.result_factory.get_error_from_result_message(result_msg)
                            self.add_change_code('evaluation_result', {'cell': result.cell, 'result': result_object})

                        if msg_type == 'execute_input' and result.cell != None:
                            self.add_change_code('evaluation_started', result)

                        if msg_type == 'stream':
                            text = result_msg['content'].get('text', None)
                            if text != None:
                                print(text)

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
                                self.add_change_code('kernel_started', result.worksheet)
                                if result.cell != None:
                                    self.add_change_code('cell_evaluation_stopped', result.cell)
                            elif result_msg['content'].get('execution_state', '') == 'idle':
                                self.add_change_code('kernel_started', result.worksheet)
                            else:
                                print(result_msg['content'])
        return True

    def start_kernel(self, worksheet):
        try: kernel = self.kernels[worksheet]
        except KeyError:
            kernel = Kernel(worksheet.get_kernelname(), worksheet)
            self.kernels[worksheet] = kernel
        else: self.add_change_code('kernel_started', worksheet)

    def run_cell(self, worksheet, cell):
        try: kernel = self.kernels[worksheet]
        except KeyError:
            kernel = Kernel(worksheet.get_kernelname(), worksheet)
            self.kernels[worksheet] = kernel
        query = Query(worksheet, cell, cell.get_all_text().strip())
        kernel.add_query(query)
        self.add_change_code('query_queued', query)

    def stop_evaluation_of_cell(self, worksheet, cell):
        try: kernel = self.kernels[worksheet]
        except KeyError: return
        kernel.remove_queries_by_cell(cell)

    def stop_evaluation(self, worksheet):
        try: kernel = self.kernels[worksheet]
        except KeyError: return

        kernel.remove_all_queries()
        kernel.kernel_manager.interrupt_kernel()

    def shutdown_for_real(self, worksheet):
        if worksheet.get_busy_cell_count() == 0:
            try: kernel = self.kernels[worksheet]
            except KeyError: return
            else:
                del(self.kernels[worksheet])
                kernel.shutdown()
                kernel.kernel_manager.finish_shutdown()
            return False
        return True

    def restart_for_real(self, worksheet):
        if worksheet.get_busy_cell_count() == 0:
            try: kernel = self.kernels[worksheet]
            except KeyError: return
            else:
                del(self.kernels[worksheet])
                kernel.shutdown()
                kernel.kernel_manager.finish_shutdown()
            self.start_kernel(worksheet)
            return False
        return True

    def shutdown(self, worksheet):
        self.stop_evaluation(worksheet)
        GObject.timeout_add(50, self.shutdown_for_real, worksheet)

    def restart(self, worksheet):
        self.stop_evaluation(worksheet)
        shutdown_func_id = GObject.timeout_add(50, self.restart_for_real, worksheet)

    def shutdown_now(self):
        keys = list(self.kernels.keys())
        for worksheet in keys:
            try: kernel = self.kernels[worksheet]
            except KeyError: return
            else:
                del(self.kernels[worksheet])
                kernel.shutdown()
                kernel.kernel_manager.finish_shutdown()


class Query():

    def __init__(self, worksheet, cell, code):
        self.worksheet = worksheet
        self.cell = cell
        self.code = code


class Kernel():

    def __init__(self, kernel_name, worksheet):
        self.query_queue = list()
        self.query_queue_lock = thread.allocate_lock()
        self.results_temp = dict()
        self.results_temp_lock = thread.allocate_lock()
        self.result_queue = queue.Queue()
        self.kernel_name = kernel_name
        self.kernel_started = False
        self.worksheet = worksheet
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
            self.results_temp_lock.acquire()
            self.results_temp[query_id] = Result(self.worksheet, None)
            self.results_temp_lock.release()

    def start_fetching(self):
        thread.start_new_thread(self.fetch_results, ())

    def add_query(self, query):
        self.query_queue_lock.acquire()
        self.query_queue.append(query)
        self.query_queue_lock.release()

    def get_result(self):
        try: return self.result_queue.get(block=False)
        except queue.Empty: return None

    def run_queries(self):
        while True:
            time.sleep(0.05)
            self.results_temp_lock.acquire()
            nothing_running = (len(self.results_temp) == 0)
            self.results_temp_lock.release()
            if not self.kernel_started:
                self.kernel_started = True
                self.start_kernel()
                self.start_fetching()
            elif nothing_running:
                    self.query_queue_lock.acquire()
                    try: query = self.query_queue.pop(0)
                    except IndexError: query = None
                    self.query_queue_lock.release()
                    if query != None:
                        query_id = self.client.execute(query.code)
                        self.results_temp_lock.acquire()
                        self.results_temp[query_id] = Result(query.worksheet, query.cell)
                        self.results_temp_lock.release()

    def remove_queries_by_cell(self, cell):
        self.query_queue_lock.acquire()
        for query in self.query_queue:
            if query.cell == cell:
                self.query_queue.remove(query)
        self.query_queue_lock.release()
        self.results_temp_lock.acquire()
        for result_temp in self.results_temp.values():
            if result_temp.cell == cell:
                self.kernel_manager.interrupt_kernel()
        self.results_temp_lock.release()

    def remove_all_queries(self):
        self.query_queue_lock.acquire()
        queue_empty = (len(self.query_queue) == 0)
        self.query_queue_lock.release()
        while not queue_empty:
            self.query_queue_lock.acquire()
            try: query = self.query_queue.pop(0)
            except IndexError: query = None
            self.query_queue_lock.release()
            if query != None:
                result = Result(query.worksheet, query.cell)
                result.result_message = 'evaluation_stopped'
                self.result_queue.put(result)
                self.query_queue_lock.acquire()
                queue_empty = (len(self.query_queue) == 0)
                self.query_queue_lock.release()

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
                        self.results_temp_lock.acquire()
                        worksheet = self.results_temp[query_id].worksheet
                        cell = self.results_temp[query_id].cell
                        self.results_temp_lock.release()
                        if result['msg_type'] == 'execute_input':
                            eval_started_result = Result(worksheet, cell)
                            eval_started_result.result_list.append(result)
                            self.result_queue.put(eval_started_result)
                        else:
                            self.results_temp_lock.acquire()
                            self.results_temp[query_id].result_list.append(result)
                            if result['content'].get('execution_state', '') == 'idle':
                                self.result_queue.put(self.results_temp[query_id])
                                del(self.results_temp[query_id])
                            self.results_temp_lock.release()

    def shutdown(self):
        self.client.shutdown()


class Result():

    def __init__(self, worksheet, cell):
        self.worksheet = worksheet
        self.cell = cell
        self.result_list = list()
        self.result_message = None


