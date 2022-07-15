
from gi.repository import Gio

class ProxyData:
    def __init__(self,host = '',port = '',username = '',password = ''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def has_auth(self):
        return self.username != ''

    def from_gsettings(self, settings):
        
        settings.get_text()
        return ProxyData()
