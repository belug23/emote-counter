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
        self.yester_date = self.current_date - datetime.timedelta(1)
        self.today_file = os.path.join(self.data_path, '{}.txt'.format(self.current_date.isoformat()))
        self.yesterday_file = os.path.join(self.data_path, '{}.txt'.format(self.yester_date.isoformat()))
        self.max_file = os.path.join(self.data_path, 'max.txt')
        self.current_count = 0
        self.last_count = 0
        self.max_count = 0
        self.init_count_file()
    
    def init_count_file(self):
        try:
            os.makedirs(self.data_path)
        except Exception:
            pass

        try:
            with open(self.today_file, 'r') as c:
                content = c.read()
                if content:
                    self.current_count = int(content)
        except Exception:
            self.current_count = 0

        try:
            with open(self.yesterday_file, 'r') as c:
                content = c.read()
                if content:
                    self.last_count = int(content)
        except Exception:
            self.last_count = 0

        try:
            with open(self.max_file, 'r') as c:
                content = c.read()
                if content:
                    self.max_count = int(content)
        except Exception:
            self.max_count = 0

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
                "command": "!gotMilk",
                "permission": "Everyone",
                "useCooldown": True,
                "useCooldownMessages": False,
                "cooldown": 60,
                "onCooldown": "{user}, {command} is still on cooldown for {cd} minutes!",
                "userCooldown": 180,
                "onUserCooldown": "{user}, {command} is still on user cooldown for {cd} minutes!",
                "outputMessage": "Today's cryptCalcium counter is at: {current}, yesterday it was at: {yesterday} and the maximum recoreded is at: {max}"
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
            command = self.settings["command"].lower()
            if data.GetParam(0).lower() == command:
                if not self.isOnCoolDown(data, command):
                    return self.publish_stats(data, command)
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
        if self.current_count > self.max_count:
            self.max_count = self.current_count
            self.write_max_count()

    def write_count(self):
        with open(self.today_file, 'w') as c:
            c.write(str(self.current_count))

    def write_max_count(self):
        with open(self.max_file, 'w') as c:
            c.write(str(self.max_count))

    def isOnCoolDown(self, data, command):
        if (
            self.settings["useCooldown"] and
            (self.parent.IsOnCooldown(self.script_name, command) or
            self.parent.IsOnUserCooldown(self.script_name, command, data.User))
        ):
            self.sendOnCoolDownMessage(data, command)
            return True
        else:
            return False
    
    def sendOnCoolDownMessage(self, data, command):
        if self.settings["useCooldownMessages"]:
            commandCoolDownDuration = self.parent.GetCooldownDuration(self.script_name, command)
            userCoolDownDuration = self.parent.GetUserCooldownDuration(self.script_name, command, data.User)

            if commandCoolDownDuration > userCoolDownDuration:
                cdi = commandCoolDownDuration
                message = self.settings["onCooldown"]
            else:
                cdi = userCoolDownDuration
                message = self.settings["onUserCooldown"]
            
            cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
            self.sendMessage(data, message, command=command, cd=cd)
    
    def setCoolDown(self, data, command):
        if self.settings["useCooldown"]:
            self.parent.AddUserCooldown(self.script_name, command, data.User, self.settings["userCooldown"])
            self.parent.AddCooldown(self.script_name, command, self.settings["cooldown"])
    
    def publish_stats(self, data, command):
        self.sendMessage(data, self.settings['outputMessage'], command)
    
    def sendMessage(self, data, message, command=None, cd="0"):
        if command is None:
            command = self.settings["command"]

        outputMessage = message.format(
            user=data.UserName,
            cost=str(None),  # not used
            currency=self.parent.GetCurrencyName(),
            command=command,
            cd=cd,
            current=str(self.current_count),
            yesterday=str(self.last_count),
            max=str(self.max_count),
        )
        self.parent.SendStreamMessage(outputMessage)

    def tick(self):
        if datetime.date.today() != self.current_date:
            self.write_count()
            self.yester_date = self.current_date
            self.current_date = datetime.date.today()
            self.today_file = os.path.join(self.data_path, '{}.txt'.format(self.current_date.isoformat()))
            self.yesterday_file = os.path.join(self.data_path, '{}.txt'.format(self.yester_date.isoformat()))
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
