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

import app.settings as settingscontroller
import app.kernelspecs as kernelspecs
import result_factory.result_factory as result_factory

import dialogs.about.about as about_dialog
import dialogs.close_confirmation.close_confirmation as close_confirmation_dialog
import dialogs.create_worksheet.create_worksheet as create_worksheet_dialog
import dialogs.delete_worksheet.delete_worksheet as delete_worksheet_dialog
import dialogs.keyboard_shortcuts.keyboard_shortcuts as keyboard_shortcuts_dialog
import dialogs.open_worksheet.open_worksheet as open_worksheet_dialog
import dialogs.overwrite_confirmation.overwrite_confirmation as overwrite_confirmation_dialog
import dialogs.preferences.preferences as preferences_dialog
import dialogs.save_as.save_as as save_as_dialog
import dialogs.select_folder.select_folder as select_folder_dialog

import re


class ServiceLocator(object):

    dialogs = dict()
    settings = None
    main_window = None
    kernelspecs = None
    result_factory = None
    ansi_escape_regex = re.compile('\\x1B\[[0-9]*[;]*[0-9]*m')

    def init_dialogs(main_window, workspace):
        settings = ServiceLocator.get_settings()
        ServiceLocator.dialogs['about'] = about_dialog.AboutDialog(main_window)
        ServiceLocator.dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(main_window)
        ServiceLocator.dialogs['create_worksheet'] = create_worksheet_dialog.CreateWorksheetDialog(main_window)
        ServiceLocator.dialogs['delete_worksheet'] = delete_worksheet_dialog.DeleteWorksheetDialog(main_window)
        ServiceLocator.dialogs['keyboard_shortcuts'] = keyboard_shortcuts_dialog.KeyboardShortcutsDialog(main_window)
        ServiceLocator.dialogs['open_worksheet'] = open_worksheet_dialog.OpenWorksheetDialog(main_window)
        ServiceLocator.dialogs['overwrite_confirmation'] = overwrite_confirmation_dialog.OverwriteConfirmationDialog(main_window)
        ServiceLocator.dialogs['preferences'] = preferences_dialog.PreferencesDialog(main_window, settings)
        ServiceLocator.dialogs['save_as'] = save_as_dialog.SaveAsDialog(workspace, main_window)
        ServiceLocator.dialogs['select_folder'] = select_folder_dialog.SelectFolderDialog(main_window)
    
    def init_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window

    def get_dialog(dialog_type):
        return ServiceLocator.dialogs[dialog_type]

    def get_kernelspecs():
        if ServiceLocator.kernelspecs == None:
            ServiceLocator.kernelspecs = kernelspecs.Kernelspecs()
        return ServiceLocator.kernelspecs

    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings()
        return ServiceLocator.settings

    def get_result_factory():
        if ServiceLocator.result_factory == None:
            ServiceLocator.result_factory = result_factory.ResultFactory()
        return ServiceLocator.result_factory

    def get_ansi_escape_regex():
        return ServiceLocator.ansi_escape_regex


