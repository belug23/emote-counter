import clr # pylint: disable=all; noqa .net system
import codecs
import json
import os
import sys
import datetime
import re


class EmoteCounter(object):
    """ 
    Because I hate coding with only functions and using Global variables.
    Here is the EmoteCounter, the daily counter for an emote usage.
    """
    script_name = "Emote counter"
    config_file = "config.json"
    application_name = 'Frog Tips TTS reader'
    version = '1.0.1'

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.data_path = os.path.join(self.base_path, '..', 'data')
        self.settings = {}
        self.parent = None
        self.current_date = datetime.date.today()
        self.file_name = os.path.join(self.data_path, '{}.txt'.format(self.current_date.isoformat()))
        self.current_count = 0
        self.init_count_file()
    
    def init_count_file(self):
        try:
            os.makedirs(self.data_path)
        except Exception:
            pass

        try:
            with open(self.file_name, 'r') as c:
                content = c.read()
                if content:
                    self.current_count = int(content)
        except Exception:
            self.current_count = 0

    def setParent(self, parent):
        self.parent = parent

    def setConfigs(self):
        self.loadSettings()
        self.pattern = r'{}'.format(self.settings['emote'])

    def loadSettings(self):
        """
            This will parse the config file if present.
            If not present, set the settings to some default values
        """
        try:
            with codecs.open(os.path.join(self.base_path, '..', self.config_file), encoding='utf-8-sig', mode='r') as file:
                self.settings = json.load(file, encoding='utf-8-sig')
        except Exception:
            self.settings = {
                "liveOnly": False,
                "emote": "cryptCalcium",
            }

    def scriptToggled(self, state):
        """
            Do an action if the state change. Like sending an announcement message
        """
        return

    def execute(self, data):
        """
            Parse the data sent from the bot to see if we need to do something.
        """
        # If it's from chat and the live setting correspond to the live status
        if self.canParseData(data):
            count = len(re.findall(self.pattern, data.Message))
            if count:
                self.add_count(count)
        return
    
    def canParseData(self, data):
        return (data.IsChatMessage() and self.is_live())

    def is_live(self):
        return (
            (self.settings["liveOnly"] and self.parent.IsLive()) or 
            (not self.settings["liveOnly"])
        )
    
    def add_count(self, count):
        self.current_count += count
        self.write_count()

    def write_count(self):
        with open(self.file_name, 'w') as c:
            c.write(str(self.current_count))

    def tick(self):
        if datetime.date.today() != self.current_date:
            self.write_count()
            self.current_date = datetime.date.today()
            self.file_name = os.path.join(self.data_path, '{}.txt'.format(self.current_date.isoformat()))
            self.init_count_file()
        return
    
    def openReadMe(self):
        location = os.path.join(os.path.dirname(__file__), "README.txt")
        if sys.platform == "win32":
            os.startfile(location)  # noqa windows only
        else:
            import subprocess
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, location])
        return
