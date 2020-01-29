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
from gi.repository import GLib, GObject

import markdown
import time
import _thread as thread
import queue
import bleach
import pypandoc


def evaluate_markdown(text):

    # escaped $ should not be handled by following code, '\U000F0000' is a unicode private use character
    result_blob = text.replace('\$', '\U000F0000')

    # convert latex to mathml
    doubledollar_count = result_blob.count('$$')
    parts = result_blob.split('$$')
    result_blob = ''
    for i, part in enumerate(parts):
        if i < doubledollar_count and i % 2 == 1:
            part = pypandoc.convert('$' + part + '$',
                                    to='html5',
                                    format='latex',
                                    extra_args=['--mathml'])
        else:
            if i == doubledollar_count and i % 2 == 1: result_blob += '$$'
            dollar_count = part.count('$')
            inner_parts = part.split('$')
            part = ''
            for j, inner_part in enumerate(inner_parts):
                if j < dollar_count and j % 2 == 1:
                    inner_part = pypandoc.convert('$' + inner_part + '$',
                                                  to='html5',
                                                  format='latex',
                                                  extra_args=['--mathml']).replace(
                                                  '<p>', '').replace('</p>', '')
                else:
                    if j == dollar_count and j % 2 == 1: part += '$'
                part += inner_part
        result_blob += part

    result_blob = markdown.markdown(result_blob.replace('\U000F0000', '\$'))

    # remove unsupported tags with bleach
    supported_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a']
    supported_tags += ['em', 'strong', 'code', 'i', 'b', 'tt']
    supported_tags += ['ul', 'ol', 'li']
    supported_tags += ['math', 'maction', 'maligngroup', 'malignmark', 'menclose', 'merror', 'mfenced', 'mfrac', 'mglyph', 'mi', 'mlabeledtr', 'mlongdiv', 'mmultiscripts', 'mn', 'mo', 'mover', 'mpadded', 'mphantom', 'mroot', 'mrow', 'ms', 'mscarries', 'mscarry', 'msgroup', 'msline', 'mspace', 'msqrt', 'msrow', 'mstack', 'mstyle', 'msub', 'msup', 'msubsup', 'mtable', 'mtd', 'mtext', 'mtr', 'munder', 'munderover', 'semantics', 'annotation', 'annotation-xml']
    supported_attributes = {'a': ['href', 'title'],
                            'math': ['altimg', 'altimg-width', 'altimg-height', 'altimg-valign', 'alttext', 'dir', 'display', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'overflow', 'xmlns'],
                            'maction': ['actiontype', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'selection'],
                            'maligngroup': ['groupalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'malignmark': ['edge', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'menclose': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'notation'],
                            'mfenced': ['close', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'open', 'separators'],
                            'mfrac': ['bevelled', 'denomalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'linethickness', 'numalign'],
                            'mglyph': ['height', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'src', 'width'],
                            'mi': ['dir', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'mathsize', 'mathvariant'],
                            'mlabeledtr': ['columnalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'mlongdiv': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'longdivstyle'],
                            'mmultiscripts': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'subscriptshift', 'supscriptshift'],
                            'mn': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'mathsize', 'mathvariant'],
                            'mo': ['fence', 'form', 'indentalign', 'indentalignfirst', 'indentalignlast', 'indentshift', 'indentshiftfirst', 'indentshiftlast', 'indenttarget', 'linebreak', 'linebreakmultchar', 'linebreakstyle', 'lineleading', 'accent', 'dir', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'largeop', 'lspace', 'mathsize', 'mathvariant', 'maxsize', 'minsize', 'movablelimits', 'rspace', 'separator', 'stretchy', 'symmetric'],
                            'mover': ['accent', 'align', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'mpadded': ['depth', 'height', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'lspace', 'voffset', 'width'],
                            'mphantom': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'mroot': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'mrow': ['dir', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'ms': ['dir', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'rquote', 'lquote', 'mathsize', 'mathvariant'],
                            'mscarries': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'location', 'position'],
                            'mscarry': ['crossout', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'msgroup': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'position', 'shift'],
                            'msline': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'length', 'position'],
                            'mspace': ['indentalign', 'indentalignfirst', 'indentalignlast', 'indentshift', 'indentshiftfirst', 'indentshiftlast', 'indenttarget', 'linebreak', 'linebreakmultchar', 'linebreakstyle', 'lineleading', 'height', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'width'],
                            'msqrt': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'msrow': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'position'],
                            'mstack': ['align', 'charalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'stackalign'],
                            'mstyle': ['decimalpoint', 'displaystyle', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'infixlinebreakstyle', 'scriptlevel', 'scriptminsize', 'scriptsizemultiplier'],
                            'msub': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'subscriptshift'],
                            'msup': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'supscriptshift'],
                            'msubsup': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'subscriptshift', 'supscriptshift'],
                            'mtable': ['align', 'alignmentscope', 'columnalign', 'columnlines', 'columnspacing', 'columnwidth', 'displaystyle', 'equalcolumns', 'equalrows', 'frame', 'framespacing', 'groupalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'minlabelspacing', 'rowalign', 'rowlines', 'rowspacing', 'side', 'width'],
                            'mtd': ['columnalign', 'columnspan', 'groupalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'rowalign', 'rowspan'],
                            'mtext': ['dir', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'mathsize', 'mathvariant'],
                            'mtr': ['columnalign', 'groupalign', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href', 'rowalign'],
                            'munder': ['accentunder', 'align', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'munderover': ['accent', 'accentunder', 'align', 'href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'semantics': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'annotation': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href'],
                            'annotation-xml': ['href', 'id', 'mathbackground', 'mathcolor', 'xlink:href']}
    return bleach.clean(result_blob, tags=supported_tags, attributes=supported_attributes)


class ComputeQueue(object):

    def __init__(self):
        self.observers = set()
        self.state = 'idle'
        self.query_queue = queue.Queue() # put computation tasks on here
        self.query_ignore_counter = dict()
        self.active_query = None
        self.result_blobs_queue = queue.Queue() # computation results are put on here
        self.change_code_queue = queue.Queue() # change code for observers are put on here
        thread.start_new_thread(self.compute_loop, ())
        GObject.timeout_add(50, self.results_loop)
        GObject.timeout_add(50, self.change_code_loop)
        
    def compute_loop(self):
        ''' wait for queries, run them and put results on the queue.
            this method runs in thread. '''

        while True:
            time.sleep(0.05)
            
            # if query complete set state idle
            if self.state == 'busy':
                self.state = self.active_query.get_state()
            
            # check for tasks, start computation
            if self.state == 'idle':
                try:
                    self.active_query = self.query_queue.get(block=False)
                except queue.Empty:
                    pass
                else:
                    cell = self.active_query.get_cell()
                    if self.active_query.ignore_counter >= self.query_ignore_counter.get(cell, 0):
                        self.state = 'busy'
                        self.add_change_code('evaluation_started', self.active_query)
                        result_blob = self.active_query.evaluate()
                        self.add_result_blob(result_blob)
                    else: pass
                        
    def change_code_loop(self):
        ''' notify observers '''

        try:
            change_code = self.change_code_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            for observer in self.observers:
                observer.change_notification(change_code['change_code'], self, change_code['parameter'])
        return True
    
    def register_observer(self, observer):
        ''' Observer call this method to register themselves with observable
            objects. They have themselves to implement a method
            'change_notification(change_code, parameter)' which they observable
            will call when it's state changes. '''
        
        self.observers.add(observer)

    def add_change_code(self, change_code, parameter):
        self.change_code_queue.put({'change_code': change_code, 'parameter': parameter})
                
    def results_loop(self):
        ''' wait for results and add them to their cells '''

        try:
            result_blob = self.result_blobs_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            self.add_change_code('evaluation_finished', result_blob)
        return True
    
    def add_query(self, query):
        query.ignore_counter = self.query_ignore_counter.get(query.get_cell(), 0) + 1
        self.query_queue.put(query)
        self.add_change_code('query_queued', query)
        
    def stop_evaluation_by_cell(self, cell):
        self.query_ignore_counter[cell] = 1 + self.query_ignore_counter.get(cell, 0)
        if self.state == 'busy' and self.active_query.get_cell() == cell:
            self.active_query.stop_evaluation()
            self.state = 'idle'
        self.add_change_code('cell_evaluation_stopped', cell)
        
    def add_result_blob(self, result):
        self.result_blobs_queue.put(result)
        
    def stop_computation(self):
        while not self.query_queue.empty():
            self.query_queue.get(block=False)
        if self.state == 'busy':
            self.active_query.stop_evaluation()
            self.state = 'idle'
    

class MarkdownQuery():

    def __init__(self, notebook, cell, query_string = ''):
        self.set_query_string(query_string)
        self.notebook = notebook
        self.cell = cell
        self.state = 'idle'
        self.ignore_counter = 0
        
    def set_query_string(self, query_string):
        self.query_string = query_string

    def evaluate(self):
        self.state = 'busy'
        html = evaluate_markdown(self.query_string)
        self.state = 'idle'
        return {'notebook': self.notebook, 'cell': self.cell, 'result_blob': html}
    
    def stop_evaluation(self):
        if self.state == 'busy':
            pass
    
    def get_cell(self):
        return self.cell
        
    def get_state(self):
        return self.state
