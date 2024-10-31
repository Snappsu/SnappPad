#TODO:
#Per-profile colors
#Per-layer aux display

# SPDX-FileCopyrightText: 2021 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT
# Minecraft Turbopad for Adafruit Macropad RP2040
import time
import asyncio
import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font
from displayio import Bitmap
from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_macropad import MacroPad

# Init
# Macropad Vars
macropad = MacroPad()
macropad.display.auto_refresh = True
macropad.pixels.brightness = .25

# Encode Vars
encoderValue = 0
encoderDelta = 0

# Display Vars
custom_font = bitmap_font.load_font("font.bdf", Bitmap)
text_lines = macropad.display_text(title="Smallest Boi",font =custom_font)

#Layer Vars
profileCurrent = 0
layerCurrent = 0
profileLabel = [
["Profile Select",["Page 1","Page 2"]],
["Clip Studio P",["Tools","Animation","Menus"]],
["Discord",["Savak Emotes"]],
["Fidget",["Piano"]]
]
layerColors = [
["fill",["#f00"]],
["fill",["#ff0"]],
["fill",["#0f0"]],
["fill",["#0ff"]]
]
layerMax = len(profileLabel[profileCurrent][1]);
#layerSwitch(layer):
#    if layer==1:

# Cause I like typing wait more
def wait(t):
    time.sleep(t)


# Turns hex colors to macropad usuable format
def hex2dec(hexCode):
    if len(hexCode) == 7:
        return (int(hexCode[1:2], 16), int(hexCode[3:4], 16), int(hexCode[5:6], 16))
    if len(hexCode) == 4:
        return (int(hexCode[1], 16), int(hexCode[2], 16), int(hexCode[3], 16))

#Changes backlight color of one key
def changeBacklightSingle(keyId,color):
    macropad.pixels[keyId] = hex2dec(color)

# Changes backlight color
def changeBacklight(patternType, args):
    if patternType == "fill":
        macropad.pixels.fill(hex2dec(args[0]))
    elif patternType == "custom":
        for i in range(12):
            macropad.pixels[i] = hex2dec(args[i])

# Checks for encoder changes
def didEncoderChange(currentValue, lastValue):
    encoderChanged = False
    if currentValue != lastValue:
        encoderChanged = True
    return encoderChanged


logText = ""; # Last (documented) action
# Updates the display to most up-to-dated values
def updateDisplay():
        text_lines[0].text = "Profile: {}".format(profileLabel[profileCurrent][0])
        text_lines[1].text = "Layer: {} ({}/{})".format(profileLabel[profileCurrent][1][layerCurrent],layerCurrent+1,layerMax)
        text_lines[2].text = "Log: {}".format(logText)
        text_lines.show()

# Little tone to play when some goes wrong
def beepDeny():
    macropad.play_tone(400, 0.1)
    macropad.play_tone(400, 0.1)

# Little tone to play when some goes right! :)
def beepForward():
    macropad.play_tone(400, 0.1)
    macropad.play_tone(800, 0.1)

def beepUndo():
    macropad.play_tone(800, 0.1)
    macropad.play_tone(400, 0.1)

# For going directly to profiles
def gotoProfile(profileIndex):
    global profileCurrent
    global layerCurrent
    global layerMax
    global logText
    try:
        layerMax = len(profileLabel[profileIndex][1])
        profileCurrent = profileIndex
        layerCurrent = 0
        logText = "Profile Changed!"
        updateDisplay()
        beepForward()
    except:
        logText = "Invalid Profile!"
        updateDisplay()
        beepDeny()

# For going directly to layers
def gotoLayer(layerIndex):
    global layerCurrent
    global logText
    layerCurrent = layerIndex
    updateDisplay()
    changeBacklight(layerColors[layerCurrent][0],layerColors[layerCurrent][1])
    macropad.play_tone((layerCurrent+1)/layerMax*1600, 0.075)

# For scrolling between laters
def scrollLayer(delta):
    global layerCurrent
    global logText

    layerCurrent = layerCurrent+delta
    if layerCurrent <0:
        layerCurrent = 0
        logText = "No previous page!"
        updateDisplay()
        beepDeny()
    elif layerCurrent >=layerMax:
        layerCurrent=layerMax-1
        logText = "No next page!"
        updateDisplay()
        beepDeny()
    else:
        updateDisplay()
        changeBacklight(layerColors[layerCurrent][0],layerColors[layerCurrent][1])
        macropad.play_tone((layerCurrent+1)/layerMax*1600, 0.075)

keyStates = [False,False,False,False,False,False,False,False,False,False,False,False]
discordReactToggle = False

# Where inputs gets processed
# Bulk of the programming
def processKey(keyEvent):
    global layerCurrent, discordReactToggle, logText, keyStates
    keyStates[keyEvent.key_number]=keyEvent.pressed

    # Profile: Profile Select
    if profileCurrent == 0:
        # Page 1
        if layerCurrent == 0:
            if keyStates[keyEvent.key_number]:
                gotoProfile(keyEvent.key_number+1)

    # Profile: Clip Studio Paint
    elif profileCurrent == 1:
        # Page 1
        if layerCurrent == 0:
            if keyStates[keyEvent.key_number]:
                print(keyEvent)

    # Profile: Discord
    elif profileCurrent == 2:
        # Emotes 1
        if layerCurrent == 0:
            if keyStates[11]:
                if discordReactToggle == False:
                    discordReactToggle = True
                    changeBacklightSingle(11,"#fff")
                    logText = "React mode enabled!"
                    beepForward()
                else:
                    discordReactToggle = False
                    changeBacklightSingle(11,"#000")
                    logText = "React mode disabled!"
                    beepUndo()
                updateDisplay()

            if keyStates[0]:
                macropad.keyboard_layout.write("{react}:marketableSavak:\n"
                .format(react = "+" if discordReactToggle else ""))

            if keyStates[1]:
                macropad.keyboard_layout.write("{react}:veryMarketableSavak:\n"
                .format(react = "+" if discordReactToggle else ""))

            if keyStates[2]:
                macropad.keyboard_layout.write("{react}:uberMarketableSavak:\n"
                .format(react = "+" if discordReactToggle else ""))

            if keyStates[3]:
                macropad.keyboard_layout.write("{react}:hyperMarketableSavak:\n"
                .format(react = "+" if discordReactToggle else ""))

# Startup Stuffs
print("MacroPad starting up!")
changeBacklight(layerColors[layerCurrent][0],layerColors[layerCurrent][1])
macropad.play_tone(400, 0.1)
macropad.play_tone(600, 0.1)
macropad.play_tone(800, 0.2)
logText = "Startup complete!"
updateDisplay()

while True:
    # Check For Encoder Changes
    if didEncoderChange(macropad.encoder, encoderValue):
        encoderDelta = macropad.encoder - encoderValue
        scrollLayer(encoderDelta)
        # Scrolled Left
        if encoderDelta == -1:
            print()
        # Scrolled Right
        elif encoderDelta == 1:
            print()


        print(layerCurrent)  # Debug

        # Sets new encoder Value
        encoderValue = macropad.encoder
    # Check For Key Events
    key_event = macropad.keys.events.get()
    if key_event:
        processKey(key_event)

    # Update enccode switch
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        gotoProfile(0)


