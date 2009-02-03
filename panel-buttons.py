#    Gedit panel buttons plugin
#    Copyright (C) 2009  Oliver Gerlich <oliver.gerlich@gmx.de>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import os
import gedit
import gtk


class PBWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        self._panels = [] # keep references to Panel objects, to prevent GC from deleting them

        # set special (lean) style for panel buttons
        gtk.rc_parse_string("""
            style "panel-buttons-toggle-button-style" {
              GtkWidget::focus-padding = 0
              GtkWidget::focus-line-width = 0
              ythickness = 0
          }
          widget "*.panel-buttons-toggle-button" style "panel-buttons-toggle-button-style"
          """)

        statusbar = window.get_children()[0].get_children()[3]

        self.btnSide = self._add_panel_button(statusbar, self._window.get_side_panel(), "side panel", 0)
        self.btnBottom = self._add_panel_button(statusbar, self._window.get_bottom_panel(), "bottom panel", 1)

    def _add_panel_button (self, statusbar, panel, title, pos):
        label = gtk.Label()
        label.set_markup("<small>%s</small>" % title)
        label.show()

        button = gtk.ToggleButton()
        button.add(label)
        button.set_focus_on_click(False)
        button.connect_object("toggled", PBWindowHelper.onButtonToggled, self, button, panel)
        button.show()
        button.set_name("panel-buttons-toggle-button")

        statusbar.pack_start(button, expand=False)
        statusbar.reorder_child(button, pos)

        button.set_active(panel.get_property("visible"))
        panel.connect_object("notify", PBWindowHelper.onPanelPropertyChanged, self, panel, button)
        self._panels.append(panel)
        return button

    def onButtonToggled (self, button, panel):
        panel.set_property("visible", button.get_active())

    def onPanelPropertyChanged (self, property, panel, button):
        if property.name == "visible":
            vis = panel.get_property("visible")
            button.set_active(vis)

    def deactivate(self):
        self.btnSide.destroy()
        self.btnBottom.destroy()
        self._panels = []

    def update_ui(self):
        pass


class PanelButtonsPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = PBWindowHelper(self, window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]

    def update_ui(self, window):
        self._instances[window].update_ui()
