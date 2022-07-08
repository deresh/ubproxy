#!/usr/bin/env python3
#
#   "Ubproxy"
#   with GTK Interface 
#
#   Ubuntu and derivatives proxy setting tool.
#   This sets the apt,bash and profile config-files.
#
#   An inevitable tool to configure proxy-settings in universities and office environmment.
#   Eliminates the need of repetitive editing of system files that is prone to frequent manual errors.  
#   Atleast 3 different individual config files needs to be edited to configure proxy settings,
#   This can be used in an environment where all the Three - ("http","https" and the "ftp") proxies
#   have the same settings.
#
#   Forked from  https://code.google.com/p/ubproxy/
#
# Changelog:
#

import gi
gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')

import os
import sys

from gui import AppWindow

from app import App

# pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY
if __name__ == "__main__":
#    if os.geteuid() == 0:
    app = App(application_id="apps.ubproxy")
    app.run(sys.argv)
    print("You must run this as root user!");
        
