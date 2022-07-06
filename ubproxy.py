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
#
#   Author:
#
#   E-mail:
#
#   Date:
#
#   Profile:
#
#   Forked from  https://code.google.com/p/ubproxy/
#
# Changelog:
# >  GTK support enabled
# >  Removed profile saving option
#


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

import os
import re
import sys
from datetime import datetime

from pprint import pprint

filenames = ["/etc/bash.bashrc", "/etc/environment", "/etc/zsh/zshrc"]
filename2 = "/etc/apt/apt.conf.d/81_proxy"
logs = "/var/log/proxychangerlog"


class AuthDialog(Gtk.Dialog):
    def __init__(self, base):
        super().__init__(title="Authentification", transient_for=base.window,modal=True, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.label1 = Gtk.Label(label="Username")
        self.label2 = Gtk.Label(label="Password")
        self.entry1 = Gtk.Entry()
        self.entry2 = Gtk.Entry()
        self.entry2.set_visibility(False)

        self.entry1.set_text(base.data.username)
        self.entry2.set_text(base.data.password)

        grid = Gtk.Grid.new()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)

        grid.attach(self.label1, 0,0,1,1)
        grid.attach(self.entry1, 1,0,1,1)
        grid.attach(self.label2, 0,1,1,1)
        grid.attach(self.entry2, 1,1,1,1)

        box = self.get_content_area()
        box.add(grid)

        self.show_all()

class ProxyData:
    def __init__(self,host = '',port = '',username = '',password = ''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def has_auth():
        return self.username != ''


class Base:
    SETTINGS_KEY = "apps.ubproxy"
    def __init__(self):

        self.checkbox = Gtk.CheckButton.new_with_label("Authentication?")
        self.entry = Gtk.Entry()
        self.button1 = Gtk.Button.new_with_label("Set")
        self.button2 = Gtk.Button.new_with_label("Remove")
        
        self.label1 = Gtk.Label(label="Host")
        self.label2 = Gtk.Label(label="Port")

        self.button1.show()
        self.button2.show()
        self.entry2 = Gtk.Entry()

        self.entry.connect("activate", self.act, self.entry)
        self.entry2.connect("activate", self.act, self.entry2)
        

        self.entry2.show()
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.set_border_width(20)

        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)

        grid.add(self.label1)
        grid.attach(self.entry, 1,0,1,1)
        grid.attach(self.label2, 0,1,1,1)
        grid.attach(self.entry2, 1,1,1,1)
        grid.attach(self.checkbox, 0,2,2,1)
        grid.attach(self.button1, 0,3,1,1)
        grid.attach(self.button2, 1,3,1,1)

        self.window.add(grid)
        self.window.show_all()
        self.window.set_title("Ubproxy")


        # prepare logging
        self.prepare_logger()


        # connect actions
        self.checkbox.connect("toggled", self.tog, None)
        self.button1.connect("clicked", self.set, None)
        self.button2.connect("clicked", self.remove, None)
        self.button1.connect_object("clicked", Gtk.Widget.destroy, self.window)
        self.button2.connect_object("clicked", Gtk.Widget.destroy, self.window)
        self.window.connect("destroy", self.destroy)

        retrieve_proxy_data()

        self.data = ProxyData()

    def destroy(self, widget, data=None):
        if (self.flog != None):
            self.flog.close()
        Gtk.main_quit()
        sys.exit(0)

    def act(self, widget, data=None):
        print(data.get_text())

    def fin(self):
        self.data.hostname = self.entry.get_text()
        self.port = self.entry2.get_text()
        self.auth = self.checkbox.get_active()

    def tog(self, widget, data=None):
        if (widget.get_active()):
            dialog = AuthDialog(self)
            response = dialog.run()
            if response == Gtk.ResponseType.CANCEL:
                self.checkbox.set_active(False)
                dialog.hide()

            if response == Gtk.ResponseType.OK:
                self.data.username = dialog.entry1.get_text()
                self.data.password = dialog.entry2.get_text()
                dialog.hide()


    def set(self, widget, data=None):
        backup([filenames[0], filenames[1], filename2])
        self.flog.write("Files have been backed up in '~/.Ubuntu-Proxy/'  with .backup extension \n")
        clean(filename2, filenames)
        self.fin()
        if (self.auth):
            filewrite_with_auth(self.host, self.port, self.uname, self.passw)
            self.flog.write("4 var proxy changed \n")
        else:
            filewrite(self.host, self.port)
            self.flog.write("2 var proxy changed \n")
        self.mbx = Gtk.MessageDialog(self.window, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                     "SUCCESSFULLY SET")
        self.mbx.run()
        self.mbx.destroy()

    def delete_event(self, widget, event, data=None):
        return False

    def remove(self, widget, data=None):
        backup([filenames[0], filenames[1], filename2])
        self.flog.write("Files have been backed up in '~/.Ubuntu-Proxy/' with .backup extension \n")
        clean(filename2, filenames)
        self.flog.write("Old Proxy-Settings removed \n")
        self.mbx = Gtk.MessageDialog(self.window, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                     "SUCCESSFULLY REMOVED")
        self.mbx.run()
        self.mbx.destroy()

    def prepare_logger(self):
        try:
            self.flog = open(logs, "a")
            self.flog.write(str(datetime.now()) + "\n")
        except:
            self.flog = None
            md = Gtk.MessageDialog(self.window, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
                                   "You are not a Root user --Run This as 'sudo'")
            md.run()
            md.destroy()
            sys.exit(0)


def filewrite(srv, port):
    lin = []
    typ0 = ("http", "ftp", "https")
    for filenam in filenames:
        fil = open(filenam, "a")
        fil.write("\n")
        for x in typ0:
            if (filenam.find("bash") != -1):
                lin.append("export %s_proxy='%s://%s:%s\'\n" % (x, x, srv, port))
                lin.append("export %s_PROXY='%s://%s:%s\'\n" % (x.upper(), x.upper(), srv, port))
            else:
                lin.append("%s_proxy=\'%s://%s:%s\'\n" % (x, x, srv, port))
                lin.append("%s_PROXY='%s://%s:%s\'\n" % (x.upper(), x.upper(), srv, port))
        for l in lin:
            fil.write(l)
        fil.close()
        lin = []

    lin2 = []
    fil = open(filename2, "w")
    for x1 in typ0:
        lin2.append('Acquire::%s::proxy "%s://%s:%s/";\n' % (x1, x1, srv, port))
    for l1 in lin2:
        fil.write(l1)
    fil.close()


def filewrite_with_auth(srv, port, name, pasw):
    lin = []
    typ0 = ("http", "ftp", "https")
    for filenam in filenames:
        fil = open(filenam, "a")
        for x in typ0:
            if (filenam.find("bash") != -1):
                lin.append("export %s_proxy=\"%s://%s:%s@%s:%s\"\n" % (x, x, name, pasw, srv, port))
            else:
                lin.append("%s_proxy=\"%s://%s:%s@%s:%s\"\n" % (x, x, name, pasw, srv, port))
        pprint(lin)
        lin = []

    lin2 = []
    fil = open(filename2, "w")
    for x1 in typ0:
        lin2.append('Acquire::%s::proxy "%s://%s:%s@%s:%s/";\n' % (x1, x1, name, pasw, srv, port))
    for l1 in lin2:
        fil.write(l1)
    fil.close()


def retrieve_proxy_data():
    settings = Gio.Settings.new(self.SETTINGS_KEY)

    settings.get_text()





def backup(files):
    homefol = os.getenv('HOME')
    folder = homefol + "/.Ubuntu-Proxy/"
    try:
        os.mkdir(folder)
    except:
        pass

    filstr = datetime.now().strftime('%Y%h%d_%H%M%S')
    newfolder = folder + filstr + "/"
    try:
        os.mkdir(newfolder)
    except:
        pass

    for fil in files:
        try:
            f1 = open(fil, "r")
            l = f1.read()
            f1.close()

            if (fil.find(".") == -1):
                newname = fil[fil.rfind('/') + 1:] + ".backup"


            else:
                fil = fil[fil.rfind('/') + 1:]
                newname = fil[:fil.find(".")] + ".backup"
            newname = newfolder + newname
            f2 = open(newname, "w")
            f2.write(l)
            f2.close()
        except:
            pass


def clean(file2, files, para=False):
    if (para):
        for file1 in files:
            try:
                f = open(file1, 'r')
                l = f.read()
                l = re.sub(r'\n?(.*http_proxy\s*=\s*".*")', r'\n# \g<1>', l)
                l = re.sub(r'\n?(.*https_proxy\s*=\s*".*")', r'\n# \g<1>', l)
                l = re.sub(r'\n?(.*ftp_proxy\s*=\s*".*")', r'\n# \g<1>', l)
                l = re.sub(r'\n?(.*HTTP_PROXY\s*=\s*".*")', r'\n# \g<1>', l)
                l = re.sub(r'\n?(.*HTTPS_PROXY\s*=\s*".*")', r'\n# \g<1>', l)
                l = re.sub(r'\n?(.*FTP_PROXY\s*=\s*".*")', r'\n# \g<1>', l)
                f.close()
                f = open(file1, 'w')
                f.write(l)
                f.close()
            except:

                pass
    else:
        for file1 in files:
            try:
                f = open(file1, 'r')
                l = f.read()
                l = re.sub(r'\n?(.*http_proxy\s*=\s*".*")', r'', l)
                l = re.sub(r'\n?(.*https_proxy\s*=\s*".*")', r'', l)
                l = re.sub(r'\n?(.*ftp_proxy\s*=\s*".*")', r'', l)
                l = re.sub(r'\n?(.*HTTP_PROXY\s*=\s*".*")', r'', l)
                l = re.sub(r'\n?(.*HTTPS_PROXY\s*=\s*".*")', r'', l)
                l = re.sub(r'\n?(.*FTP_PROXY\s*=\s*".*")', r'', l)
                f.close()
                f = open(file1, 'w')
                f.write(l)
                f.close()
            except:

                pass
        try:
            f = open(file2, "r")
            l = f.read()
            l = re.sub(r'\n?(.*Acquire.*".*?";)', "", l)
            f.close()
            f = open(file2, 'w')
            f.write(l)
            f.close()
        except:

            pass

# pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY
if __name__ == "__main__":
    if os.geteuid() == 0:
        base = Base()
        Gtk.main()
    print("You must run this as root user!");
        
