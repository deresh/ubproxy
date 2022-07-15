from gi.repository import Gtk, Adw
import sys

from data import ProxyData;

class AuthDialog(Gtk.Dialog):
    def __init__(self, base):
        super().__init__(title="Authentification", transient_for=base,modal=True)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button(      
             "Ok", Gtk.ResponseType.OK
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
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_margin_start(20)
        grid.set_margin_end(20)

        grid.attach(self.label1, 0,0,1,1)
        grid.attach(self.entry1, 1,0,1,1)
        grid.attach(self.label2, 0,1,1,1)
        grid.attach(self.entry2, 1,1,1,1)

        box = self.get_content_area()
        box.append(grid)

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.set_default_size(500,250)
        self.set_title("UBProxy")

        self.checkbox = Gtk.CheckButton.new_with_label("Authentication?")
        self.label1 = Gtk.Label(label="Host")
        self.label2 = Gtk.Label(label="Port")
        self.entry = Gtk.Entry()
        self.entry2 = Gtk.Entry()
        self.button1 = Gtk.Button.new_with_label("Set")
        self.button2 = Gtk.Button.new_with_label("Remove")
        

        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_margin_start(20)
        grid.set_margin_end(20)

        grid.attach(self.label1,0,0,1,1)
        grid.attach(self.entry, 1,0,1,1)
        grid.attach(self.label2, 0,1,1,1)
        grid.attach(self.entry2, 1,1,1,1)
        grid.attach(self.checkbox, 0,2,2,1)
        grid.attach(self.button1, 0,3,1,1)
        grid.attach(self.button2, 1,3,1,1)
        grid.set_row_homogeneous(False)
        grid.set_column_homogeneous(False)

        self.set_child(grid)

        # connect actions


        self.checkbox.connect("toggled", self.tog, None)
        self.button1.connect("clicked", self.set, None)
        self.button2.connect("clicked", self.remove, None)
        self.connect("destroy", self.destroy)

        self.data = ProxyData.from_gsettings()

    def destroy(self, widget, data=None):
        if (self.flog != None):
            self.flog.close()
        Gtk.main_quit()
        sys.exit(0)

    def fin(self):
        self.data.hostname = self.entry.get_text()
        self.port = self.entry2.get_text()
        self.auth = self.checkbox.get_active()

    def tog(self, widget, data=None):
        if (widget.get_active()):
            dialog = AuthDialog(self)
            dialog.connect('response', self.toggle_response)
            response = dialog.show()

    def toggle_response(self, dialog, response):
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



