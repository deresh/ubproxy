


class ProxyData:
    SETTINGS_KEY = "apps.ubproxy"
    def __init__(self,host = '',port = '',username = '',password = ''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def has_auth():
        return self.username != ''

    def from_gsettings():
        settings = Gio.Settings.new(self.SETTINGS_KEY)
        settings.get_text()
        return ProxyData()
