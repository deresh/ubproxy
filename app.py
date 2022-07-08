from gi.repository import Gtk, Gio, Adw

import re
import sys
import os
from datetime import datetime
from pprint import pprint
from pathlib import Path

import gui
import data

filenames = ["/etc/bash.bashrc", "/etc/environment", "/etc/zsh/zshrc"]
filename2 = "/etc/apt/apt.conf.d/81_proxy"


class App(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.win = None
        self.flog = None

    def on_activate(self, app):
        if not self.win:  # added this condition
            self.win = gui.AppWindow(application=app)
        self.win.present()  # if window is already created, this will raise it to the front

        # prepare logging
        self.prepare_logger()

        self.retrieve_proxy_data()

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


    def retrieve_proxy_data(self):
        self.data = ProxyData.from_gsettings()

    def backup(files):
        homefol = os.getenv('HOME')
        folder = os.path.join(os.getenv('HOME'), "/.Ubuntu-Proxy/")

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
    def prepare_logger(self):
        folder = os.path.join(os.getenv('HOME'),".Ubuntu-Proxy")

        try:
            Path(folder).mkdir(exist_ok=True)
        except:
            self.error_dialog("Unable to create folder")

        try:
            log_file = os.path.join(folder, "proxychanger.log")
            self.flog = open(log_file, "a")
            self.flog.write(str(datetime.now()) + "\n")
        except:
            self.flog = None
            self.error_dialog("You are not a Root user --Run This as 'sudo'")

    def error_dialog(self, str):
            md = Gtk.MessageDialog(buttons=Gtk.ButtonsType.CLOSE, text=str)
            md.set_transient_for(self.win)
            md.set_modal(self.win)
            md.show()
            md.connect("response", self.close_dialog)

    def close_dialog(self, dialog, response):
            dialog.destroy()
            sys.exit(1)