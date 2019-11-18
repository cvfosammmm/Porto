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
import viewgtk.viewgtk_welcome_page as viewgtk_welcome_page
import controller.controller_notebook as notebookcontroller
import controller.controller_worksheet_lists as wslistscontroller
import controller.controller_shortcuts as shortcutscontroller
import backend.backend_controller as backendcontroller
from workspace.workspace import Workspace
from app.service_locator import ServiceLocator


class MainApplicationController(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        
    def do_activate(self):
        ''' Everything starts here. '''
        
        # load settings
        self.settings = ServiceLocator.get_settings()
        
        # init compute queue
        self.backend_controller_markdown = backendcontroller.BackendControllerMarkdown()
        self.backend_controller_code = backendcontroller.BackendControllerCode()
        self.kernelspecs = model_kernelspecs.Kernelspecs()
        
        # init view
        self.main_window = view.MainWindow(self)
        ServiceLocator.init_main_window(self.main_window)
        self.main_window.set_default_size(self.settings.get_value('window_state', 'width'), 
                                          self.settings.get_value('window_state', 'height'))
        if self.settings.get_value('window_state', 'is_maximized'): self.main_window.maximize()
        else: self.main_window.unmaximize()
        if self.settings.get_value('window_state', 'is_fullscreen'): self.main_window.fullscreen()
        else: self.main_window.unfullscreen()
        self.main_window.show_all()

        self.main_window.welcome_page_view.create_ws_link.connect('clicked', self.on_create_ws_button_click)
        self.main_window.welcome_page_view.open_ws_link.connect('clicked', self.on_open_ws_button_click)
        self.setup_kernel_changer()

        self.notebook = model_notebook.Notebook()
        self.workspace = Workspace()
        ServiceLocator.init_dialogs(self.main_window, self.notebook, self)

        # controllers
        self.worksheet_controllers = dict()
        self.notebook_controller = notebookcontroller.NotebookController(self.notebook, self.main_window, self)
        self.wslists_controller = wslistscontroller.WSListsController(self.main_window.sidebar, self.main_window.headerbar.hb_right.worksheet_chooser, self)
        self.shortcuts_controller = shortcutscontroller.ShortcutsController(self.notebook, self.main_window, self)
        self.construct_worksheet_menu()

        # to watch for cursor movements
        self.cursor_position = {'cell': None, 'cell_position': None, 'cell_size': None, 'position': None}

        # watch changes in view
        self.observe_main_window()

    '''
    *** main observer functions
    '''

    def observe_main_window(self):
        hb_left = self.main_window.headerbar.hb_left
        hb_left.create_ws_button.connect('clicked', self.on_create_ws_button_click)
        hb_left.open_ws_button.connect('clicked', self.on_open_ws_button_click)
        
        hb_right = self.main_window.headerbar.hb_right
        hb_right.save_button.connect('clicked', self.on_save_ws_button_click)
        hb_right.revert_button.connect('clicked', self.on_revert_ws_button_click)
        hb_right.worksheet_chooser.create_button.connect('clicked', self.on_create_ws_button_click)
        hb_right.worksheet_chooser.open_button.connect('clicked', self.on_open_ws_button_click)

        self.main_window.connect('size-allocate', self.on_window_size_allocate)
        self.main_window.connect('window-state-event', self.on_window_state_event)
        self.main_window.connect('delete-event', self.on_window_close)
    
    '''
    *** reconstruct window when worksheet is open / no worksheet present
    '''

    def setup_kernel_changer(self):
        menu = self.main_window.headerbar.hb_right.change_kernel_menu
        for name in self.kernelspecs.get_list_of_names():
            item = Gio.MenuItem.new(self.kernelspecs.get_displayname(name), 'win.change_kernel::' + name)
            menu.append_item(item)

    '''
    *** evaluation / save state indicators
    '''
    
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
            self.main_window.delete_ws_action.set_enabled(True)
        elif isinstance(worksheet, model_worksheet.DocumentationWorksheet):
            self.main_window.delete_ws_action.set_enabled(False)
            
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
        parameters = ServiceLocator.get_dialog('create_worksheet').run()
        if parameters != None:
            pathname, kernelname = parameters
            self.notebook_controller.create_worksheet(pathname, kernelname)

    def on_open_ws_button_click(self, button_object=None):
        filename = ServiceLocator.get_dialog('open_worksheet').run()
        if filename != None:
            if filename.split('.')[-1] == 'ipynb':
                worksheet = model_worksheet.NormalWorksheet(filename)
                self.activate_worksheet(worksheet)

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

    def on_window_state_event(self, main_window, state_event):
        ''' signal handler, update window state variables '''
    
        main_window.is_maximized = not((state_event.new_window_state & Gdk.WindowState.MAXIMIZED) == 0)
        main_window.is_fullscreen = not((state_event.new_window_state & Gdk.WindowState.FULLSCREEN) == 0)
        return False
        
    def save_window_state(self):
        main_window = self.main_window
        self.settings.set_value('window_state', 'width', main_window.current_width)
        self.settings.set_value('window_state', 'height', main_window.current_height)
        self.settings.set_value('window_state', 'is_maximized', main_window.is_maximized)
        self.settings.set_value('window_state', 'is_fullscreen', main_window.is_fullscreen)
        self.settings.set_value('window_state', 'sidebar_visible', self.workspace.show_sidebar)
        self.settings.set_value('window_state', 'paned_position', self.workspace.sidebar_position)
        self.settings.pickle()
        
    def on_window_close(self, window=None, parameter=None):
        self.save_quit()
        return True

    def on_quit_action(self, action=None, parameter=None):
        self.save_quit()

    def save_quit(self, accel_group=None, window=None, key=None, mask=None):
        ''' signal handler, ask user to save unsaved worksheets or discard changes '''
        
        worksheets = self.notebook.get_unsaved_worksheets()
        active_worksheet = self.notebook.get_active_worksheet()

        if len(worksheets) == 0 or active_worksheet == None or ServiceLocator.get_dialog('close_confirmation').run(worksheets)['all_save_to_close']: 
            self.save_window_state()
            self.quit()

    '''
    *** worksheet menu
    '''
    
    def construct_worksheet_menu(self):
        self.main_window.restart_kernel_action.connect('activate', self.on_wsmenu_restart_kernel)
        self.main_window.change_kernel_action.connect('activate', self.on_wsmenu_change_kernel)
        self.main_window.delete_ws_action.connect('activate', self.on_wsmenu_delete)
        self.main_window.save_as_action.connect('activate', self.on_wsmenu_save_as)
        self.main_window.save_all_action.connect('activate', self.on_wsmenu_save_all)
        self.main_window.close_action.connect('activate', self.on_wsmenu_close)
        self.main_window.close_all_action.connect('activate', self.on_wsmenu_close_all)
        self.main_window.quit_action.connect('activate', self.on_quit_action)
        self.shortcuts_controller.accel_group.connect(Gdk.keyval_from_name('q'), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.MASK, self.save_quit)
        
    def on_wsmenu_restart_kernel(self, action=None, parameter=None):
        self.notebook.active_worksheet.restart_kernel()
        
    def on_wsmenu_change_kernel(self, action=None, parameter=None):
        if parameter != None:
            self.main_window.change_kernel_action.set_state(parameter)
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
            ServiceLocator.get_dialog('save_as').run(worksheet)

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
