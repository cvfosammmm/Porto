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


class CellPresenter(object):

    def __init__(self, cell):

        self.cell = cell
        self.cell.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'cell_state_change':
            try: notebook_view = self.cell.get_notebook().view
            except KeyError: return
            child_position = self.cell.get_notebook_position()
            cell_view = notebook_view.get_child_by_position(child_position)

            if cell_view != None:
                if parameter == 'idle': cell_view.state_display.show_nothing()
                elif parameter == 'edit': cell_view.state_display.show_nothing()
                elif parameter == 'display': cell_view.state_display.show_nothing()
                elif parameter == 'queued_for_evaluation': cell_view.state_display.show_spinner()
                elif parameter == 'ready_for_evaluation': cell_view.state_display.show_spinner()
                elif parameter == 'evaluation_in_progress': cell_view.state_display.show_spinner()


class CodeCellPresenter(CellPresenter):

    def __init__(self, cell):
        CellPresenter.__init__(self, cell)


class MarkdownCellPresenter(CellPresenter):

    def __init__(self, cell):
        CellPresenter.__init__(self, cell)


