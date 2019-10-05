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
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gio

import sys

import model.model_worksheet as model_worksheet
import model.model_notebook as model_notebook
import model.model_cell as model_cell
import model.model_kernelspecs as model_kernelspecs
import viewgtk.viewgtk as view
import viewgtk.viewgtk_dialogs_preferences as view_dialogs_preferences
import viewgtk.viewgtk_dialogs_open_worksheet as viewgtk_dialogs_open_worksheet
import viewgtk.viewgtk_dialogs_close_confirmation as viewgtk_dialogs_close_confirmation
import viewgtk.viewgtk_welcome_page as viewgtk_welcome_page
import controller.controller_notebook as notebookcontroller
import controller.controller_worksheet_lists as wslistscontroller
import controller.controller_settings as settingscontroller
import controller.controller_shortcuts as shortcutscontroller
import controller.controller_dialogs_create_worksheet as cwsdialogcontroller
import controller.controller_dialogs_save_as as sadialogcontroller
import backend.backend_controller as backendcontroller


class MainApplicationController(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        
    def do_activate(self):
        ''' Everything starts here. '''
        
        # load settings
        self.settings = settingscontroller.Settings()
        
        self.construct_worksheet_menu()
        
        # init compute queue
        self.backend_controller_markdown = backendcontroller.BackendControllerMarkdown()
        self.backend_controller_code = backendcontroller.BackendControllerCode()
        self.kernelspecs = model_kernelspecs.Kernelspecs()
        
        # init view
        self.main_window = view.MainWindow(self)
        self.main_window.set_default_size(self.settings.get_value('window_state', 'width'), 
                                          self.settings.get_value('window_state', 'height'))
        self.welcome_page_view = viewgtk_welcome_page.WelcomePageView()
        self.welcome_page_view.create_ws_link.connect('clicked', self.on_create_ws_button_click)
        self.welcome_page_view.open_ws_link.connect('clicked', self.on_open_ws_button_click)
        self.setup_kernel_changer()

        self.notebook = model_notebook.Notebook()

        # controllers
        self.worksheet_controllers = dict()
        self.notebook_controller = notebookcontroller.NotebookController(self.notebook, self.main_window, self)
        self.wslists_controller = wslistscontroller.WSListsController(self.main_window.sidebar, self.main_window.headerbar.hb_right.worksheet_chooser, self)
        self.cws_dialog_controller = cwsdialogcontroller.ControllerDialogCreateWorksheet(self.notebook,
                                                                                         self.main_window, self)
        self.sa_dialog_controller = sadialogcontroller.ControllerDialogSaveAs(self.notebook, self.main_window, self)

        # to watch for cursor movements
        self.cursor_position = {'cell': None, 'cell_position': None, 'cell_size': None, 'position': None}

        if self.settings.get_value('window_state', 'is_maximized'): self.main_window.maximize()
        else: self.main_window.unmaximize()
        if self.settings.get_value('window_state', 'is_fullscreen'): self.main_window.fullscreen()
        else: self.main_window.unfullscreen()
        
        self.main_window.show_all()
        self.main_window.paned.set_position(self.settings.get_value('window_state', 'paned_position'))
        self.window_mode = None
        self.activate_welcome_page_mode()
        if self.settings.get_value('window_state', 'sidebar_visible'):
            self.show_sidebar()
        else:
            self.hide_sidebar()

        # populate app
        #self.notebook.populate_documentation()
        
        # watch changes in view
        self.observe_main_window()

        # shortcuts controller
        self.shortcuts_controller = shortcutscontroller.ShortcutsController(self.main_window, self)
        
    '''
    *** main observer functions
    '''

    def observe_main_window(self):
        hb_left = self.main_window.headerbar.hb_left
        hb_left.create_ws_button.connect('clicked', self.on_create_ws_button_click)
        hb_left.open_ws_button.connect('clicked', self.on_open_ws_button_click)
        
        hb_right = self.main_window.headerbar.hb_right
        hb_right.add_codecell_button.connect('clicked', self.on_add_codecell_button_click)
        hb_right.add_markdowncell_button.connect('clicked', self.on_add_markdowncell_button_click)
        hb_right.down_button.connect('clicked', self.on_down_button_click)
        hb_right.up_button.connect('clicked', self.on_up_button_click)
        hb_right.delete_button.connect('clicked', self.on_delete_button_click)
        hb_right.eval_button.connect('clicked', self.on_eval_button_click)
        hb_right.eval_nc_button.connect('clicked', self.on_eval_nc_button_click)
        hb_right.stop_button.connect('clicked', self.on_stop_button_click)
        hb_right.save_button.connect('clicked', self.on_save_ws_button_click)
        hb_right.revert_button.connect('clicked', self.on_revert_ws_button_click)
        hb_right.worksheet_chooser.create_button.connect('clicked', self.on_create_ws_button_click)
        hb_right.worksheet_chooser.open_button.connect('clicked', self.on_open_ws_button_click)

        self.main_window.connect('size-allocate', self.on_window_size_allocate)
        self.main_window.connect('window-state-event', self.on_window_state_event)
        self.main_window.connect('delete-event', self.on_window_close)
        self.main_window.sidebar.connect('size-allocate', self.on_ws_view_size_allocate)
    
    '''
    *** reconstruct window when worksheet is open / no worksheet present
    '''

    def activate_worksheet_mode(self):
        if self.window_mode != 'worksheet':
            self.window_mode = 'worksheet'
            hb_right = self.main_window.headerbar.hb_right
            hb_right.show_buttons()

    def activate_welcome_page_mode(self):
        if self.window_mode != 'welcome_page':
            self.window_mode = 'welcome_page'
            self.main_window.headerbar.set_title('Welcome to Porto')
            self.main_window.headerbar.set_subtitle('')
            hb_right = self.main_window.headerbar.hb_right
            hb_right.hide_buttons()
            self.notebook_controller.set_worksheet_view(self.welcome_page_view)

    def show_sidebar(self):
        self.main_window.sidebar.show_all()
        self.main_window.headerbar.hb_left.show_all()
        self.main_window.headerbar.hb_right.open_worksheets_button.hide()
        self.welcome_page_view.set_sidebar_visible(True)

    def hide_sidebar(self):
        self.main_window.sidebar.hide()
        self.main_window.headerbar.hb_left.hide()
        self.main_window.headerbar.hb_right.open_worksheets_button.show_all()
        self.welcome_page_view.set_sidebar_visible(False)

    def toggle_sidebar(self, action, parameter=None):
        sidebar_visible = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(sidebar_visible))
        if sidebar_visible:
            self.show_sidebar()
        else:
            self.hide_sidebar()
        self.settings.set_value('window_state', 'sidebar_visible', sidebar_visible)

    def setup_kernel_changer(self):
        menu = self.main_window.headerbar.hb_right.change_kernel_menu
        for name in self.kernelspecs.get_list_of_names():
            item = Gio.MenuItem.new(self.kernelspecs.get_displayname(name), 'app.change_kernel::' + name)
            menu.append_item(item)

    '''
    *** evaluation / save state indicators
    '''
    
    def update_stop_button(self):
        worksheet = self.notebook.active_worksheet
        if worksheet.get_busy_cell_count() > 0:
            self.main_window.headerbar.activate_stop_button()
        else:
            self.main_window.headerbar.deactivate_stop_button()
            
    def update_save_button(self):
        worksheet = self.notebook.get_active_worksheet()
        if worksheet.get_save_state() == 'modified':
            self.main_window.headerbar.activate_save_button()
            self.main_window.headerbar.activate_revert_button()
        else:
            self.main_window.headerbar.deactivate_save_button()
            self.main_window.headerbar.deactivate_revert_button()
            
        if isinstance(worksheet, model_worksheet.NormalWorksheet):
            self.main_window.headerbar.activate_documentation_mode()
        else:
            self.main_window.headerbar.deactivate_documentation_mode()
            
    def update_hamburger_menu(self):
        worksheet = self.notebook.get_active_worksheet()
        if isinstance(worksheet, model_worksheet.NormalWorksheet):
            self.delete_ws_action.set_enabled(True)
        elif isinstance(worksheet, model_worksheet.DocumentationWorksheet):
            self.delete_ws_action.set_enabled(False)
            
    def update_up_down_buttons(self):
        worksheet = self.notebook.get_active_worksheet()
        if worksheet != None:
            active_cell = worksheet.get_active_cell()
            if active_cell != None:
                cell_position = active_cell.get_worksheet_position()
                cell_count = worksheet.get_cell_count()
                if cell_position == cell_count - 1:
                    self.main_window.headerbar.deactivate_down_button()
                else:
                    self.main_window.headerbar.activate_down_button()
                if cell_position == 0:
                    self.main_window.headerbar.deactivate_up_button()
                else:
                    self.main_window.headerbar.activate_up_button()

    def update_subtitle(self, worksheet):
        busy_cell_count = worksheet.get_busy_cell_count()
        if busy_cell_count > 0:
            plural = 's' if busy_cell_count > 1 else ''
            subtitle = 'evaluating ' + str(busy_cell_count) + ' cell' + plural + '.'
        elif worksheet.get_kernel_state() == 'starting':
            subtitle = 'starting kernel.'
        else:
            subtitle = 'idle.'

        for widget in [self.main_window.sidebar, self.main_window.headerbar.hb_right.worksheet_chooser]:
            if isinstance(worksheet, model_worksheet.NormalWorksheet):
                item = widget.open_worksheets_list_view.get_item_by_worksheet(worksheet)
            else:
                item = widget.documentation_list_view.get_item_by_worksheet(worksheet)
            item.set_state(subtitle)
        if worksheet == self.notebook.get_active_worksheet():
            if self.main_window.headerbar.get_subtitle() != subtitle:
                self.main_window.headerbar.set_subtitle(subtitle)

    def update_title(self, worksheet):
        if isinstance(worksheet, model_worksheet.NormalWorksheet):
            save_state = '*' if worksheet.get_save_state() == 'modified' else ''
            for widget in [self.main_window.sidebar, self.main_window.headerbar.hb_right.worksheet_chooser]:
                item = widget.open_worksheets_list_view.get_item_by_worksheet(worksheet)
                if item != None:
                    item.set_name(save_state + worksheet.get_name())
        if worksheet == self.notebook.active_worksheet:
            self.main_window.headerbar.set_title(save_state + worksheet.get_name())
        
    '''
    *** signal handlers: main window
    '''
    
    def on_create_ws_button_click(self, button_object=None):
        self.cws_dialog_controller.show()

    def on_open_ws_button_click(self, button_object=None):
        dialog = viewgtk_dialogs_open_worksheet.OpenWorksheet(self.main_window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename.split('.')[-1] == 'ipynb':
                worksheet = model_worksheet.NormalWorksheet(filename)
                self.activate_worksheet(worksheet)
            else: pass
        dialog.destroy()

    def activate_worksheet_by_pathname(self, pathname):
        for worksheet in self.notebook.open_worksheets:
            if worksheet.pathname == pathname:
                self.notebook.set_active_worksheet(worksheet)
                self.wslists_controller.select_row_by_worksheet(worksheet)
                return
        worksheet = model_worksheet.NormalWorksheet(pathname)
        try:
            worksheet.load_from_disk()
        except FileNotFoundError:
            self.notebook.recently_opened_worksheets.remove_worksheet_by_pathname(pathname)
        else:
            self.notebook.add_worksheet(worksheet)
            self.wslists_controller.select_row_by_worksheet(worksheet)

    def activate_worksheet(self, worksheet):
        if not worksheet in self.notebook.open_worksheets:
            self.notebook.add_worksheet(worksheet)
            worksheet.load_from_disk()
        self.notebook.set_active_worksheet(worksheet)
        self.wslists_controller.select_row_by_worksheet(worksheet)

    def on_add_codecell_button_click(self, button_object=None):
        ''' signal handler, add codecell below active cell '''
        
        worksheet = self.notebook.get_active_worksheet()
        position = worksheet.get_active_cell().get_worksheet_position() + 1
        worksheet.create_cell(position, '', activate=True, set_unmodified=False)
                
    def on_add_markdowncell_button_click(self, button_object=None):
        ''' signal handler, add markdown cell below active cell '''
        
        worksheet = self.notebook.get_active_worksheet()
        position = worksheet.get_active_cell().get_worksheet_position() + 1
        worksheet.create_markdowncell(position, '', activate=True, set_unmodified=False)
                
    def on_down_button_click(self, button_object=None):
        ''' signal handler, move active cell down '''
        
        worksheet = self.notebook.get_active_worksheet()
        position = worksheet.get_active_cell().get_worksheet_position()
        cell_count = worksheet.get_cell_count()
        if position < cell_count:
            worksheet.move_cell(position, position + 1)

    def on_up_button_click(self, button_object=None):
        ''' signal handler, move active cell up '''
        
        worksheet = self.notebook.get_active_worksheet()
        position = worksheet.get_active_cell().get_worksheet_position()
        cell_count = worksheet.get_cell_count()
        if position > 0:
            worksheet.move_cell(position, position - 1)
            
    def on_delete_button_click(self, button_object=None):
        ''' signal handler, delete active cell '''
        
        worksheet = self.notebook.get_active_worksheet()
        cell = worksheet.get_active_cell()
        prev_cell = worksheet.get_prev_cell(cell)
        if prev_cell != None: 
            cell.remove_result()
            worksheet.set_active_cell(prev_cell)
            #prev_cell.place_cursor(prev_cell.get_iter_at_line(prev_cell.get_line_count() - 1))
            prev_cell.place_cursor(prev_cell.get_start_iter())
            worksheet.remove_cell(cell)
        else:
            next_cell = worksheet.get_next_cell(cell)
            if next_cell != None:
                cell.remove_result()
                worksheet.set_active_cell(next_cell)
                next_cell.place_cursor(next_cell.get_start_iter())
                worksheet.remove_cell(cell)
            else:
                cell.remove_result()
                worksheet.remove_cell(cell)
                worksheet.create_cell('last', '', activate=True)
            
    def on_eval_button_click(self, button_object=None):
        ''' signal handler, evaluate active cell '''

        active_cell = self.notebook.active_worksheet.active_cell
        if not (isinstance(active_cell, model_cell.MarkdownCell) and active_cell.get_result() != None):
            active_cell.evaluate()
        
    def on_eval_nc_button_click(self, button_object=None):
        ''' signal handler, evaluate active cell, go to next cell '''

        worksheet = self.notebook.active_worksheet
        active_cell = worksheet.active_cell

        if not (isinstance(active_cell, model_cell.MarkdownCell) and active_cell.get_result() != None):
            active_cell.evaluate()
        new_active_cell = worksheet.get_next_visible_cell(active_cell)
        if not new_active_cell == None:
            worksheet.set_active_cell(new_active_cell)
            new_active_cell.place_cursor(new_active_cell.get_start_iter())
        else:
            worksheet.create_cell()
            new_active_cell = worksheet.get_next_visible_cell(active_cell)
            worksheet.set_active_cell(new_active_cell)
            new_active_cell.place_cursor(new_active_cell.get_start_iter())
            
    def on_stop_button_click(self, button_object=None):
        ''' signal handler, stop evaluation '''

        self.notebook.active_worksheet.stop_evaluation()

    def on_save_ws_button_click(self, button_object=None):
        ''' signal handler, save active worksheet to disk '''
        
        worksheet = self.notebook.get_active_worksheet()
        if isinstance(worksheet, model_worksheet.NormalWorksheet):
            worksheet.save_to_disk()
        
    def on_revert_ws_button_click(self, button_object=None):
        ''' signal handler, save active worksheet to disk '''
        
        worksheet = self.notebook.get_active_worksheet()
        if isinstance(worksheet, model_worksheet.DocumentationWorksheet):
            worksheet.remove_all_cells()
            worksheet.populate_cells()
            self.update_save_button()
        
    def on_window_size_allocate(self, main_window, window_size):
        ''' signal handler, update window size variables '''
        
        if not(main_window.is_maximized) and not(main_window.is_fullscreen):
            main_window.current_width, main_window.current_height = main_window.get_size()
            main_window.set_default_size(main_window.current_width, main_window.current_height)

    def on_ws_view_size_allocate(self, paned, paned_size):
        ''' signal handler, update worksheet/ws_list seperator position.
            called on worksheet list size allocation. '''
        
        self.main_window.paned_position = self.main_window.paned.get_position()
            
    def on_window_state_event(self, main_window, state_event):
        ''' signal handler, update window state variables '''
    
        main_window.is_maximized = not((state_event.new_window_state & Gdk.WindowState.MAXIMIZED) == 0)
        main_window.is_fullscreen = not((state_event.new_window_state & Gdk.WindowState.FULLSCREEN) == 0)
        return False
        
    def save_window_state(self):
        ''' save window state variables '''

        main_window = self.main_window
        self.settings.set_value('window_state', 'width', main_window.current_width)
        self.settings.set_value('window_state', 'height', main_window.current_height)
        self.settings.set_value('window_state', 'is_maximized', main_window.is_maximized)
        self.settings.set_value('window_state', 'is_fullscreen', main_window.is_fullscreen)
        self.settings.set_value('window_state', 'paned_position', main_window.paned_position)
        self.settings.pickle()
        
    def on_window_close(self, main_window, event=None):
        ''' signal handler, ask user to save unsaved worksheets or discard changes '''
        
        worksheets = self.notebook.get_unsaved_worksheets()
        if len(worksheets) == 0: 
            self.save_window_state()
            return False

        self.save_changes_dialog = viewgtk_dialogs_close_confirmation.CloseConfirmation(self.main_window, worksheets)
        response = self.save_changes_dialog.run()
        if response == Gtk.ResponseType.NO:
            self.save_changes_dialog.destroy()
            self.save_window_state()
            return False
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
            self.save_window_state()
            return False
        else:
            self.save_changes_dialog.destroy()
            return True

    '''
    *** application menu
    '''

    def on_appmenu_show_preferences_dialog(self, action, parameter=''):
        ''' show preferences dialog. '''
        
        def on_button_toggle(button, preference_name):
            self.settings.set_value('preferences', preference_name, button.get_active())
            
            if preference_name == 'pretty_print':
                self.notebook.set_pretty_print(self.settings.get_value('preferences', 'pretty_print'))
        
        worksheet = self.notebook.get_active_worksheet()
        dialog = view_dialogs_preferences.Preferences(self.main_window)
        
        dialog.option_pretty_print.set_active(self.settings.get_value('preferences', 'pretty_print'))
        dialog.option_pretty_print.connect('toggled', on_button_toggle, 'pretty_print')

        response = dialog.run()
        del(dialog)

    def on_appmenu_show_shortcuts_window(self, action, parameter=''):
        ''' show popup with a list of keyboard shortcuts. '''
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file('./resources/shortcuts_window.ui')
        self.shortcuts_window = self.builder.get_object('shortcuts-window')
        self.shortcuts_window.set_transient_for(self.main_window)
        self.shortcuts_window.show_all()
        
    def on_appmenu_show_about_dialog(self, action, parameter=''):
        ''' show popup with some information about the app. '''
        
        self.about_dialog = Gtk.AboutDialog()
        self.about_dialog.set_transient_for(self.main_window)
        self.about_dialog.set_modal(True)
        self.about_dialog.set_program_name('Porto')
        self.about_dialog.set_version('0.0.1')
        self.about_dialog.set_copyright('Copyright © 2017-2019 - the Porto developers')
        self.about_dialog.set_comments('Porto is a notebook type interface to Python and SageMath. It is designed to make exploring mathematics easy and fun.')
        self.about_dialog.set_license_type(Gtk.License.GPL_3_0)
        self.about_dialog.set_website('https://www.cvfosammmm.org/porto')
        self.about_dialog.set_website_label('https://www.cvfosammmm.org/porto')
        self.about_dialog.set_authors(('Robert Griesel',))
        self.about_dialog.show_all()
        
    def on_appmenu_quit(self, action=None, parameter=''):
        ''' quit application, show save dialog if unsaved worksheets present. '''
        
        if not self.on_window_close(self.main_window):
            self.quit()
        
    '''
    *** worksheet menu
    '''
    
    def construct_worksheet_menu(self):
        self.restart_kernel_action = Gio.SimpleAction.new('restart_kernel', None)
        self.restart_kernel_action.connect('activate', self.on_wsmenu_restart_kernel)
        self.add_action(self.restart_kernel_action)
        default = GLib.Variant.new_string('python3')
        self.change_kernel_action = Gio.SimpleAction.new_stateful('change_kernel', GLib.VariantType('s'), default)
        self.change_kernel_action.connect('activate', self.on_wsmenu_change_kernel)
        self.add_action(self.change_kernel_action)
        self.delete_ws_action = Gio.SimpleAction.new('delete_worksheet', None)
        self.delete_ws_action.connect('activate', self.on_wsmenu_delete)
        self.add_action(self.delete_ws_action)
        self.save_as_action = Gio.SimpleAction.new('save_as', None)
        self.save_as_action.connect('activate', self.on_wsmenu_save_as)
        self.add_action(self.save_as_action)
        self.save_all_action = Gio.SimpleAction.new('save_all', None)
        self.save_all_action.connect('activate', self.on_wsmenu_save_all)
        self.add_action(self.save_all_action)
        self.close_action = Gio.SimpleAction.new('close_worksheet', None)
        self.close_action.connect('activate', self.on_wsmenu_close)
        self.add_action(self.close_action)
        self.close_all_action = Gio.SimpleAction.new('close_all_worksheets', None)
        self.close_all_action.connect('activate', self.on_wsmenu_close_all)
        self.add_action(self.close_all_action)

        sv_default = GLib.Variant.new_boolean(self.settings.get_value('window_state', 'sidebar_visible'))
        self.toggle_sidebar_action = Gio.SimpleAction.new_stateful('toggle-sidebar', None, sv_default)
        self.toggle_sidebar_action.connect('activate', self.toggle_sidebar)
        self.add_action(self.toggle_sidebar_action)
        preferences_action = Gio.SimpleAction.new('show_preferences_dialog', None)
        preferences_action.connect('activate', self.on_appmenu_show_preferences_dialog)
        self.add_action(preferences_action)
        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self.on_appmenu_quit)
        self.add_action(quit_action)
        show_about_dialog_action = Gio.SimpleAction.new('show_about_dialog', None)
        show_about_dialog_action.connect('activate', self.on_appmenu_show_about_dialog)
        self.add_action(show_about_dialog_action)
        show_shortcuts_window_action = Gio.SimpleAction.new('show_shortcuts_window', None)
        show_shortcuts_window_action.connect('activate', self.on_appmenu_show_shortcuts_window)
        self.add_action(show_shortcuts_window_action)
        
    def on_wsmenu_restart_kernel(self, action=None, parameter=None):
        self.notebook.active_worksheet.restart_kernel()
        
    def on_wsmenu_change_kernel(self, action=None, parameter=None):
        if parameter != None:
            self.change_kernel_action.set_state(parameter)
            worksheet = self.notebook.active_worksheet
            if worksheet.get_kernelname() != parameter.get_string():
                worksheet.set_kernelname(parameter.get_string())
                for widget in [self.main_window.sidebar, self.main_window.headerbar.hb_right.worksheet_chooser]:
                    item = widget.open_worksheets_list_view.get_item_by_worksheet(worksheet)
                    icon_normal = self.kernelspecs.get_normal_sidebar_icon(parameter.get_string())
                    icon_active = self.kernelspecs.get_active_sidebar_icon(parameter.get_string())
                    item.update_kernel_icons(icon_normal, icon_active)
                worksheet.restart_kernel()

    def on_wsmenu_save_as(self, action=None, parameter=None):
        worksheet = self.notebook.get_active_worksheet()
        if worksheet != None:
            self.sa_dialog_controller.show(worksheet)

    def on_wsmenu_save_all(self, action=None, parameter=None):
        for worksheet in self.notebook.open_worksheets:
            worksheet.save_to_disk()

    def on_wsmenu_close(self, action=None, parameter=None):
        worksheet = self.notebook.get_active_worksheet()
        if worksheet != None:
            self.notebook_controller.close_worksheet_after_modified_check(worksheet)

    def on_wsmenu_close_all(self, action=None, parameter=None):
        self.notebook_controller.close_all_worksheets_after_modified_check()

    def on_wsmenu_delete(self, action, parameter=None):
        self.notebook_controller.delete_worksheet(self.notebook.get_active_worksheet())

    '''
    *** automatic scrolling
    '''
    
    def scroll_to_cursor(self, cell, check_if_position_changed=True):
        worksheet = self.notebook.get_active_worksheet()
        if worksheet == None: return
        if not worksheet.active_cell == cell: return
        current_cell = cell
        current_cell_position = cell.get_worksheet_position()
        current_position = cell.get_property('cursor-position')
        worksheet_view = self.main_window.active_worksheet_view
        cell_view_position = cell.get_worksheet_position()
        cell_view = worksheet_view.get_child_by_position(cell_view_position)
        result_view = cell_view.result_view_revealer
        current_cell_size = cell_view.get_allocation().height
        current_cell_size = cell_view.get_allocation().height + result_view.get_allocation().height

        # check if cursor has changed
        position_changed = False
        if worksheet.cursor_position['cell'] != current_cell: position_changed = True
        if worksheet.cursor_position['cell_position'] != current_cell_position: position_changed = True
        if worksheet.cursor_position['cell_size'] != current_cell_size and (self.cursor_position['position'] != 0 or cell.get_char_count() == 0): 
            position_changed = True
        if worksheet.cursor_position['position'] != current_position: position_changed = True
        if check_if_position_changed == False:
            position_changed = True
            if cell_view.has_changed_size():
                cell_view.update_size()
        
        first_run = True
        if position_changed:
            if worksheet.cursor_position['cell'] != None: first_run = False
            worksheet.cursor_position['cell'] = current_cell
            worksheet.cursor_position['cell_position'] = current_cell_position
            worksheet.cursor_position['cell_size'] = current_cell_size
            worksheet.cursor_position['position'] = current_position
            
        if first_run == False and position_changed:
            
            # scroll to markdown cell with result
            if isinstance(current_cell, model_cell.MarkdownCell) and current_cell.get_result() != None:

                # get line number, calculate offset
                scroll_position = worksheet_view.get_vadjustment()
                x, cell_position = cell_view.translate_coordinates(worksheet_view.box, 0, 0)
                line_position = cell_view.text_entry.get_iter_location(cell.get_iter_at_mark(cell.get_insert())).y
                last_line_position = cell_view.text_entry.get_iter_location(cell.get_end_iter()).y
                
                if cell_position >= 0:
                    new_position = cell_position
                else:
                    new_position = 0
                
                window_height = worksheet_view.get_allocated_height()
                if current_cell_size < window_height:
                    if new_position >= scroll_position.get_value():
                        if new_position + current_cell_size >= scroll_position.get_value() + window_height:
                            new_position += current_cell_size - window_height
                            scroll_position.set_value(new_position)
                    else:
                        scroll_position.set_value(new_position)
                else:    
                    scroll_position.set_value(new_position)

            # scroll to codecell or md cell without result
            if not isinstance(current_cell, model_cell.MarkdownCell) or current_cell.get_result() == None:

                # get line number, calculate offset
                scroll_position = worksheet_view.get_vadjustment()
                x, cell_position = cell_view.translate_coordinates(worksheet_view.box, 0, 0)
                it = cell.get_iter_at_mark(cell.get_insert())
                line_position = cell_view.text_entry.get_iter_location(it).y
                last_line_position = cell_view.text_entry.get_iter_location(cell.get_end_iter()).y
                
                if cell_position >= 0:
                    offset = -scroll_position.get_value() + cell_position + line_position + 15
                else:
                    offset = 0

                if line_position == 0 and scroll_position.get_value() >= cell_position:
                    offset -= 15
                elif line_position >= last_line_position and scroll_position.get_value() <= (cell_position + 15 + line_position + 0):
                    offset += 15
                    
                # calculate movement
                window_height = worksheet_view.get_allocated_height()
                if offset > window_height - cell_view.line_height:
                    movement = offset - window_height + cell_view.line_height
                elif offset < 0:
                    movement = offset
                else:
                    movement = 0
                if movement > 0 and line_position == 0:
                    if current_cell_size < round(window_height / 3.5):
                        movement += current_cell_size
                        if current_cell.get_line_count() == 1:
                            movement -= 50
                        else:
                            movement -= 35
                    else:
                        movement += min(60, current_cell_size - 35)
                    if isinstance(current_cell, model_cell.MarkdownCell):
                        movement -= 1

                if movement < 0 and line_position >= last_line_position:
                    if current_cell_size < round(window_height / 3.5):
                        movement -= current_cell_size
                        if current_cell.get_line_count() == 1:
                            movement += 50
                        else:
                            movement += 35
                    else:
                        movement -= min(60, current_cell_size - 35)
                    if isinstance(current_cell, model_cell.MarkdownCell):
                        movement -= 1
                        
                scroll_position.set_value(scroll_position.get_value() + movement)

    def do_startup(self):
        Gtk.Application.do_startup(self)


main_controller = MainApplicationController()
exit_status = main_controller.run(sys.argv)
main_controller.backend_controller_code.backend_code.shutdown_all()
sys.exit(exit_status)
