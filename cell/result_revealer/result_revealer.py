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

from helpers.observable import Observable
import cell.result_revealer.result_revealer_controller as result_revealer_controller
import cell.result_revealer.result_revealer_presenter as result_revealer_presenter
import cell.result_revealer.result_revealer_viewgtk as result_revealer_view
import cell.result_revealer.stream.stream as stream


class ResultRevealer(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.result = None

    def set_result(self, result, show_animation=True):
        self.result = result
        self.add_change_code('new_result', {'result': self.result, 'show_animation': show_animation})
        
    def get_result(self):
        return self.result

    def remove_result(self, show_animation=True):
        self.result = None
        self.add_change_code('new_result', {'result': self.result, 'show_animation': show_animation})

    
class CodeResultRevealer(ResultRevealer):

    def __init__(self, cell):
        ResultRevealer.__init__(self)
        self.cell = cell

        self.streams = dict()
        self.streams['stderr'] = stream.Stream('stderr')
        self.streams['stdout'] = stream.Stream('stdout')
        self.stderr_stream_visible = False
        self.stdout_stream_visible = False

        self.view = result_revealer_view.ResultViewRevealerCode()
        cell.view.vbox.pack_start(self.view, False, False, 0)
        self.presenter = result_revealer_presenter.CodeResultRevealerPresenter(self, self.view)
        self.presenter.add_streams(self.streams)
        self.controller = result_revealer_controller.CodeResultRevealerController(self, self.view)

    def reset_streams(self, show_animation=True):
        for stream in self.streams.values():
            stream.reset()
        self.stderr_stream_visible = False
        self.stdout_stream_visible = False
        self.add_change_code('stream_update', show_animation)

    def add_to_stream(self, stream_type, text, show_animation=True):
        if len(text) == 0: return

        self.streams[stream_type].add_text(text)
        if stream_type == 'stderr':
            self.stderr_stream_visible = True
        elif stream_type == 'stdout':
            self.stdout_stream_visible = True
        self.add_change_code('stream_update', show_animation)


class MarkdownResultRevealer(ResultRevealer):

    def __init__(self, cell):
        ResultRevealer.__init__(self)
        self.cell = cell

        self.view = result_revealer_view.ResultViewRevealerMarkdown()
        cell.view.vbox.pack_start(self.view, False, False, 0)
        self.presenter = result_revealer_presenter.MarkdownResultRevealerPresenter(self, self.view)
        self.controller = result_revealer_controller.MarkdownResultRevealerController(self, self.view)


