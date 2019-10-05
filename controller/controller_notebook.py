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
from gi.repository import Gtk
from gi.repository import GLib

import os.path

import model.model_worksheet as model_worksheet
import viewgtk.viewgtk_worksheet as viewgtk_worksheet
import viewgtk.viewgtk_dialogs_close_confirmation as viewgtk_dialogs_close_confirmation
import controller.controller_worksheet as worksheetcontroller
import controller.controller_dialogs_delete_worksheet as dwsdialogcontroller


class NotebookController(object):

    def __init__(self, notebook, main_window, main_controller):

        self.notebook = notebook
        self.main_window = main_window
        self.main_controller = main_controller
        self.dws_dialog_controller = dwsdialogcontroller.ControllerDialogDeleteWorksheet(self.notebook,
                                                                                         self.main_window, self)

        self.notebook.set_pretty_print(self.main_controller.settings.get_value('preferences', 'pretty_print'))

        # observe worksheet
        self.notebook.register_observer(self)
        self.notebook.register_observer(self.main_controller.backend_controller_code)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_worksheet':
            worksheet = parameter

            self.main_controller.activate_worksheet_mode()

            # add worksheet view
            worksheet_view = viewgtk_worksheet.WorksheetView()
            self.main_window.worksheet_views[worksheet] = worksheet_view

            # observe changes in this worksheet
            self.main_controller.worksheet_controllers[worksheet] = worksheetcontroller.WorksheetController(worksheet, worksheet_view, self.main_controller)
            
        if change_code == 'worksheet_removed':
            worksheet = parameter
            worksheet_view = self.main_window.worksheet_views[worksheet]
            self.remove_view(worksheet_view)
            del(self.main_window.worksheet_views[worksheet])
            self.main_controller.worksheet_controllers[worksheet].destruct()
            del(self.main_controller.worksheet_controllers[worksheet])

        if change_code == 'changed_active_worksheet':
            worksheet = parameter

            if worksheet != None:
                self.main_controller.activate_worksheet_mode()

                # change title, subtitle in headerbar
                self.main_controller.update_title(worksheet)
                self.main_controller.update_subtitle(worksheet)
                self.main_controller.update_save_button()
                self.main_controller.update_hamburger_menu()
                self.main_controller.change_kernel_action.set_state(GLib.Variant.new_string(worksheet.get_kernelname()))

                # change worksheet_view
                self.main_window.active_worksheet_view = self.main_window.worksheet_views[worksheet]
                self.set_worksheet_view(self.main_window.active_worksheet_view)
                if worksheet.get_active_cell() != None: worksheet.set_active_cell(worksheet.get_active_cell())
                self.main_controller.update_stop_button()

    def close_worksheet(self, worksheet, add_to_recently_opened=True):
        self.notebook.remove_worksheet(worksheet)
        self.notebook.recently_opened_worksheets.remove_worksheet_by_pathname(worksheet.pathname)
        if add_to_recently_opened:
            pathname = worksheet.get_pathname()
            kernelname = worksheet.get_kernelname()
            if os.path.isfile(pathname):
                item = {'pathname': pathname, 'kernelname': kernelname, 'date': worksheet.get_last_saved()}
                self.notebook.recently_opened_worksheets.add_item(item, notify=True, save=True)        

    def close_worksheet_after_modified_check(self, worksheet):
        if worksheet.get_save_state() == 'modified':
            self.save_changes_dialog = viewgtk_dialogs_close_confirmation.CloseConfirmation(self.main_window, [worksheet])
            response = self.save_changes_dialog.run()
            if response == Gtk.ResponseType.YES:
                worksheet.save_to_disk()
                self.save_changes_dialog.destroy()
            elif response == Gtk.ResponseType.NO:
                self.save_changes_dialog.destroy()
            else:
                self.save_changes_dialog.destroy()
                return
        self.close_worksheet(worksheet)

    def close_all_worksheets_after_modified_check(self):
        worksheets = self.notebook.get_unsaved_worksheets()
        if len(worksheets) > 0:
            self.save_changes_dialog = viewgtk_dialogs_close_confirmation.CloseConfirmation(self.main_window, worksheets)
            response = self.save_changes_dialog.run()
            if response == Gtk.ResponseType.NO:
                self.save_changes_dialog.destroy()
            elif response == Gtk.ResponseType.YES:
                selected_worksheets = list()
                if len(worksheets) == 1:
                    selected_worksheets.append(worksheets[0])
                else:
                    dialog_worksheets = self.save_changes_dialog.worksheets
                    for child in self.save_changes_dialog.chooser.get_children():
                        if child.get_child().get_active():
                            selected_worksheets.append(dialog_worksheets[int(child.get_child().get_name()[30:])])
                for worksheet in worksheets:
                    if worksheet in selected_worksheets:
                        worksheet.save_to_disk()
                self.save_changes_dialog.destroy()
            else:
                self.save_changes_dialog.destroy()
                return
        for worksheet in list(self.notebook.open_worksheets.values()):
            self.close_worksheet(worksheet)

    def delete_worksheet(self, worksheet):
        if self.dws_dialog_controller.show(worksheet):
            self.close_worksheet(worksheet, add_to_recently_opened=False)
            worksheet.remove_from_disk()

    def create_worksheet(self, pathname, kernelname):
        self.notebook.recently_opened_worksheets.remove_worksheet_by_pathname(pathname)
        self.notebook.remove_worksheet_by_pathname(pathname)

        worksheet = model_worksheet.NormalWorksheet(pathname)
        worksheet.set_kernelname(kernelname)
        worksheet.save_to_disk()
        self.main_controller.activate_worksheet(worksheet)
        worksheet.create_cell(0, '', activate=True)
        worksheet.save_to_disk()

    def set_worksheet_view(self, worksheet_view):
        wswrapper = self.main_window.worksheet_view_wrapper
        page_index = wswrapper.page_num(worksheet_view)
        if page_index == -1:
            page_index = wswrapper.append_page(worksheet_view)
        worksheet_view.show_all()
        wswrapper.set_current_page(page_index)
        wswrapper.show_all()
        
    def remove_view(self, view):
        wswrapper = self.main_window.worksheet_view_wrapper
        page_index = wswrapper.page_num(view)
        if page_index >= 0:
            wswrapper.remove_page(page_index)
        

