#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

from emote_counter import EmoteCounter # pylint: disable=all; noqa
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = EmoteCounter.script_name
Website = "https://github.com/belug23/"
Description = "Allow you to monitor daily usage of an emote."
Creator = "Belug"
Version = EmoteCounter.version


chad_bot = EmoteCounter()
# Ugly StreamLab part, just map functions to the class
def ScriptToggled(state):
    return chad_bot.scriptToggled(state)

def Init():
    chad_bot.setParent(Parent)  #  noqa injected by streamlabs chatbot
    return chad_bot.setConfigs()

def Execute(data):
    return chad_bot.execute(data)

def ReloadSettings(jsonData):
    return chad_bot.setConfigs()

def OpenReadMe():
    return chad_bot.openReadMe()

def Tick():
    return chad_bot.tick()
