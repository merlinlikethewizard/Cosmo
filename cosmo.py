#!/usr/bin/python
# -*- coding=UTF-8 -*-
'''
==========================================
    //////  //////  //////  //  //  //////
   //      //  //  //      /\ ///  //  //
  //      //  //  //////  //\///  //  //
 //      //  //      //  //  //  //  //
//////  //////  //////  //  //  //////.py
==========================================
Merlin Wizard ||
Zoë Wizard ||
=============

Started 4/20/16
'''

import os
import time
import types
from math import ceil, floor

from cosmoObjects import *

####################################
import curses, locale              #
from curses import wrapper         # getch
                                   #
locale.setlocale(locale.LC_ALL,'') #
####################################

class Frame:
    def __init__(self):
        
        #### OPTIONS ####
        self.ratioAdjust = 1
        self.mainWidth = 41
        self.mainHeight = 21
        self.alertHeight = 4
        self.nullChar = ' '
        self.keyBindings = {'up':'UP', 'down':'DOWN', 'right':'RIGHT', 'left':'LEFT', 'inspect':'i', 'interact':'SPACE', 'openInv':'o', 'attack':'z', 'attack2':'x', 'quit':'ESCAPE', 'select':'SPACE', 'select2':'RETURN'}
        
    def mainLoop(self, player, loaded):
        self.player = player
        self.loaded = loaded
        self.gameOver = False
        alert = ''
        alertTime = time.time()
        self.inspect = False
        self.interact = False
        self.attack = False
        self.attack1or2 = 1
        self.doUpdate = True
        self.numberOfUpdates = 0
        
        while not self.gameOver:
            #### Reset Alert
            if len(alert) > 0 and time.time()-alertTime > 5:
                alert = ''
                self.doUpdate = True
            
            #### Player Action
            tempAlert = self.playerAction()
            
            #### Entities Action
            for entity in player.area.entities:
                entity.update()
            
            #### Set Alert
            if len(tempAlert) > 0:
                alert = tempAlert
                tempAlert = ''
                alertTime = time.time()
                
            #### Update
            if self.doUpdate:
                self.update(alert=alert, mainString=self.mapString(), title=self.player.area.name)
                self.doUpdate = False
                
                # Make sure there aren't any pesky duplicates of the loaded dictionary
                self.checkForLoadedCopies(self.loaded)
    
    def update(self, title='', mainString='', alert='', properties={}, debug=True):
        self.numberOfUpdates += 1
        
        if type(title) is types.StringType:
            title = unicode(title, 'utf-8')
        if type(mainString) is types.StringType:
            mainString = unicode(mainString, 'utf-8')
        if type(alert) is types.StringType:
            alert = unicode(alert, 'utf-8')
        
        string = ''
        
        #TITLE
        string += boxString(title, '=', '', ' |', '| ')
        
        #MAIN BOX (MAP)
        string += '\n'
        boxMain = boxString(mainString, '=', '=', '|', '|', forceWidth=self.mainWidth, forceHeight=self.mainHeight)
        string += boxMain
        
        #ALERT BOX
        string += '\n'
        string += boxString(makeFit(alert, self.mainWidth - 2), '', '=', ' |', '| ', forceWidth=self.mainWidth - 2, forceHeight=self.alertHeight)
        
        #HEALTH / MANA BAR    --still for show
        string += '\n'
        string += barString('', '=', ' |', '| ', ' | ', [self.player.maxHealth, -1, self.player.maxMana], [unichr(9825)*self.player.health, '<space>', unichr(10209)*self.player.mana], self.mainWidth+2)
        
        #DEBUG
        if debug:
            string += '\n'
            string += barString('', '', ' -', '- [DEBUG] ', ' / ', [1, 1, 1], ['updates=' + str(self.numberOfUpdates), 'x=' + str(self.player.x), 'y=' + str(self.player.y)])
        
        
        stdscr.clear()
        
        try:
            stdscr.addstr(string.encode('utf-8')) #main program draw fn
        except curses.error:
            raise Exception('\n\n===== COSMO =====\nWindow too small.\n=================\n')
            
        stdscr.refresh()
                
    def playerAction(self):
        alert = ''
        ch = getch()
        
        direction = None
        inspect = False
        interact = False
        attack = False
        
        directions = {self.keyBindings['up']:'up', self.keyBindings['down']:'down', self.keyBindings['right']:'right', self.keyBindings['left']:'left'}
        
        if ch != None:
            if ch in directions:
                direction = directions[ch]
                if self.inspect:
                    inspect = True
                elif self.interact:
                    interact = True
                elif self.attack:
                    attack = True
                else:
                    result, alert = self.player.doToBlock('move', direction)
                self.doUpdate = True

            if ch == self.keyBindings['inspect']:
                if self.inspect:
                    inspect = True
                self.inspect = not self.inspect

            else:
                self.inspect = False

            if ch == self.keyBindings['interact']:
                if self.interact:
                    interact = True
                self.interact = not self.interact

            else:
                self.interact = False
                
            if ch == self.keyBindings['attack']:
                self.attack = True
                self.doUpdate = True
            else:
                self.attack = False

            if ch == self.keyBindings['openInv']:
                self.openInv()
                self.doUpdate = True

            if ch == self.keyBindings['quit']:
                self.openMainMenu()
                self.doUpdate = True
                
        if inspect:
            result, alert = self.player.doToBlock('inspect', direction)

        if interact:
            result, alert = self.player.doToBlock('interact', direction)
            if isinstance(result, NPC):
                self.openConversation(result)

        if attack:
            result, alert = self.player.doToBlock('attack', direction)
            
            
        if alert == None:
            alert = ''
        if alert != '':
            self.doUpdate = True
        return str(alert)
    
    def mapString(self):
        ratioAdjust = self.ratioAdjust
        mainHeight = self.mainHeight
        mainWidth = int(ceil(self.mainWidth/float(ratioAdjust)))
        nullChar = self.nullChar
        
        area = self.player.area
        x = self.player.x
        y = self.player.y
        
        positionx, positiony = x - int(floor(mainWidth/2.0)), y - int(floor(mainHeight/2.0))
        
        if area.lockX:
            if positionx < 0:
                positionx = 0
            if positionx > 0-(mainWidth - area.width):
                positionx = 0-(mainWidth - area.width)
        
            if area.width <= mainWidth:
                positionx = int(floor((mainWidth - area.width)/-2.0))
                
        if area.lockY:
            if positiony < 0:
                positiony = 0
            if positiony > 0-(mainHeight - area.height):
                positiony = 0-(mainHeight - area.height)
                
            if area.height <= mainHeight:
                positiony = int(floor((mainHeight - area.height)/-2.0))
        
        grid = map(list,zip(*area.getGrid()))
        string = ''
        
        for i in range(mainHeight):
            for j in range(mainWidth):
                if j > 0:
                    string += ' '*(ratioAdjust - 1)
                drawi, drawj = i + positiony, j + positionx
#                if x == drawj and y == drawi:
#                    string += self.player.char
                if drawi < 0 or drawj < 0 or drawi > area.height-1 or drawj > area.width-1:
                    string += nullChar
                else:
                    string += grid[drawi][drawj]
            string += '\n'
            
        string = string[:-1]
        
        return string

    def openInv(self):
        menu = Menu(self.player.items)
        doUpdate = True
        while True:
            if doUpdate:
                doUpdate = False
                
                mainString = menu.getListing(self.mainWidth, self.mainHeight, margin=1)
                
                value = 'UNKNOWN' #unknown value
                alert = ''
                if len(self.player.items) > 0:
                    item = menu.items[menu.selected]
                    if item.value != None:
                        value = item.value
                    alert = ('-' + item.name + '-\n' + item.text + ' Value: ' + str(value))
                
                self.update(title='Inventory', mainString=mainString, alert=alert)
                
            result = menu.getInput(self.keyBindings)
            if result != None:
                doUpdate = True
                if isinstance(result, Item):
                    return result
                if result == False:
                    return None
    
    def openConversation(self, npc):
        speechBubbleHeight = 3
#        text = "We don't have bacon, hon, but we do have all-natural no-preservatives gluten-free Puckered Grains cereal."
        npc.openConversation()
        answer = None
        keepTalking = True
        while keepTalking:
            dialogue, responses, keepTalking = npc.talk(answer)
            if keepTalking:
                menu = Menu(responses)
                answer = None
                doUpdate = True
                while True:
                    if doUpdate:
                        doUpdate = False

                        bubble = barString('-', '-', ' ]', '[ ', '', [1, 1], ['<space>', \
                            boxString(makeFit(dialogue, self.mainWidth-6), '', '', '', '', forceWidth=self.mainWidth-6, forceHeight=speechBubbleHeight)])

                        mainString = boxString(npc.image, '', '', '', '', forceHeight=self.mainHeight-speechBubbleHeight-2, stickVertical='bottom') + '\n' + bubble
                        alert = menu.getListing(self.mainWidth-4, self.alertHeight, cushion=0)
                        self.update(title=npc.name, mainString=mainString, alert=alert)

                    result = menu.getInput(self.keyBindings)
                    if result != None:
                        doUpdate = True
                        if type(result) is type('') or type(result) is type(u''):
                            if result != '':
                                answer = result
                            break
                        
    def openMainMenu(self):
        options = []
        menus = [Menu(['Resume', 'Options...', 'Save', 'Quit...'])]
        titles = ['Paused']
        messages = ['']
        doUpdate = True
        exit = False
        setKey = False
        alert = ''
        while True:
            if doUpdate:
                doUpdate = False
                
                fitMessage = makeFit(messages[-1], self.mainWidth-2, indent=1)
                messageHeight = len(fitMessage.split('\n'))
                if messages[-1] == '':
                    messageHeight = 0
                else:
                    fitMessage = ' ' + fitMessage + '\n'
                mainString = fitMessage + menus[-1].getListing(self.mainWidth, self.mainHeight - messageHeight, margin=1)
                self.update(title=titles[-1], mainString=mainString, alert=makeFit(alert, self.mainWidth-2))
                alert = ''
                        
            if setKey:
                setKey = False
                doUpdate = True
                ch = None
                while ch == None:
                    ch = getch()
                if ch != 'ESCAPE':
                    self.keyBindings[key] = ch
                    menus[-1].items[menus[-1].items.index(keyName + '_')] = keyName + self.keyBindings[key]
                
            result = menus[-1].getInput(self.keyBindings)
            if result != None:
                doUpdate = True
                if result == False or result == 'Resume':
                    exit = True
                elif titles[-1] == 'Paused':
                    if result == 'Options...':
                        titles += ['Options']
                        messages += ['']
                        ratioAdjust = 'Ratio Adjust: True'
                        if self.ratioAdjust == 1:
                            ratioAdjust = 'Ratio Adjust: False'
                        menus += [Menu(['Controls...', ratioAdjust])]
                    elif result == 'Save':
                        writeSave(self.player.x, self.player.y, self.player.area.areaName)
                        alert = 'Game saved.'
                    elif result == 'Quit...':
                        titles += ['Quit']
                        messages += ['Do you really want to quit? Unsaved changes will be lost.']
                        menus += [Menu(['no', 'yes'])]
                elif titles[-1] == 'Quit':
                    if result == 'yes':
                        self.gameOver = True
                        return
                    elif result == 'no':
                        exit = True
                elif titles[-1] == 'Options':
                    if result == 'Ratio Adjust: True':
                        menus[-1].items[menus[-1].items.index('Ratio Adjust: True')] = 'Ratio Adjust: False'
                        self.ratioAdjust = 1
                    if result == 'Ratio Adjust: False':
                        menus[-1].items[menus[-1].items.index('Ratio Adjust: False')] = 'Ratio Adjust: True'
                        self.ratioAdjust = 2
                    if result == 'Controls...':
                        titles += ['Controls']
                        messages += ['']
                        menus += [Menu(['Up: ' + self.keyBindings['up'], 'Down: ' + self.keyBindings['down'], 'Right: ' + self.keyBindings['right'],\
                                        'Left: ' + self.keyBindings['left'], 'Primary Attack: ' + self.keyBindings['attack'],\
                                        'Secondary Attack: ' + self.keyBindings['attack2'], 'Inspect: ' + self.keyBindings['inspect'],\
                                        'Interact: ' + self.keyBindings['interact'], 'Inventory: ' + self.keyBindings['openInv'], 'Pause: ESCAPE'])]
                elif titles[-1] == 'Controls':
                    setKey = True
                    
                    if result == 'Up: ' + self.keyBindings['up']:
                        keyName = 'Up: '
                        key = 'up'
                    elif result == 'Down: ' + self.keyBindings['down']:
                        keyName = 'Down: '
                        key = 'down'
                    elif result == 'Right: ' + self.keyBindings['right']:
                        keyName = 'Right: '
                        key = 'right'
                    elif result == 'Left: ' + self.keyBindings['left']:
                        keyName = 'Left: '
                        key = 'left'
                    elif result == 'Inspect: ' + self.keyBindings['inspect']:
                        keyName = 'Inspect: '
                        key = 'inspect'
                    elif result == 'Interact: ' + self.keyBindings['interact']:
                        keyName = 'Interact: '
                        key = 'interact'
                    elif result == 'Inventory: ' + self.keyBindings['openInv']:
                        keyName = 'Inventory: '
                        key = 'openInv'
                    elif result == 'Primary Attack: ' + self.keyBindings['attack']:
                        keyName = 'Primary Attack: '
                        key = 'attack'
                    elif result == 'Secondary Attack: ' + self.keyBindings['attack2']:
                        keyName = 'Secondary Attack: '
                        key = 'attack2'
                    else:
                        setKey = False
                        
                    if setKey:
                        menus[-1].items[menus[-1].items.index(result)] = keyName + '_'
                    
                if exit:
                    exit = False
                    if len(menus) > 1:
                        del menus[-1]
                        del messages[-1]
                        del titles[-1]
                    else:
                        break
                        
    
    def checkForLoadedCopies(self, loaded):
        for thing in globals():
            if type(thing) is types.InstanceType:
                if 'loaded' in dir(thing):
                    if not thing.loaded is loaded:
                        raise Exception(str(thing) + " has a 'loaded' dict duplicate")

class Area:
    def __init__(self, areaName, loaded):
        self.areaName = areaName
        self.loaded = loaded
        
        area = open(areaName + '.txt','r')
        area = unicode(area.read(), 'utf-8')
        
        splitter = area.split('\n<splitter>\n')
        
        self.name =       splitter[0]
        self.area =       splitter[1].split('\n')
        self.attributes = splitter[2]
        self.chars =      splitter[3]
        
        self.lockX = True
        self.lockY = True
        
        if len(splitter) > 4:
            args = eval(splitter[4])
            for key in args:
                exec('self.' + str(key) + ' = args["' + str(key) + '"]')
        
        self.area = map(list, zip(*self.area)) # I'm quite proud of this
        
        self.attributes = eval(self.attributes) # string to dict, i.e. '{}' to {}
        self.chars = eval(self.chars)
        
        self.grid = []
        for i in self.area:
            self.grid += [list(i)]
            
        self.width = len(self.grid)
        self.height = len(self.grid[0])
        
        self.initGrid()
    
    def findEntranceOld(self, entranceName): ### MARKED FOR DELETION ###
        for key in self.attributes:
            att = self.attributes[key]
            if att['type'] == 'ENTER' or att['type'] == 'EDGE':
                if att['warpFrom'] == entranceName:
                    for i in range(self.width):
                        for j in range(self.height):
                            if self.grid[i][j] == key:
                                return i,j
                            
    def findEntrance(self, entranceName):
        for entity in self.entities:
            if isinstance(entity, Enter) or isinstance(entity, Edge):
                if entity.warpFrom == entranceName:
                    return entity.x, entity.y
                            
    def getGrid(self):
        tempGrid = []
        for line in self.grid:
            tempLine = []
            for char in line:
                if 'char' in dir(self.pointers[char]):
                    tempLine += [self.pointers[char].char]
                elif char in self.chars:
                    tempLine += [self.chars[char]]
                else:
                    tempLine += [char]
                
            tempGrid += [tempLine]
        for entity in self.entities[::-1]:
            if entity.visible:
                tempGrid[entity.x][entity.y] = entity.char
        return tempGrid
    
    def initGrid(self):
        self.entities = []
        self.pointers = {}
        for x in range(self.width):
            for y in range(self.height):
                self.initBlock(x, y)
                
    def initBlock(self, x, y):
        char = self.grid[x][y]
        if not char in self.attributes:
            self.attributes[char] = self.attributes[' ']
            self.attributes[char]['pointsTo'] = ' '
            
        block = self.attributes[char]
            
        if type(block) is types.StringType: #So I can set '[' to act like ']' with '[':']'
            pointsTo = block
            block = self.attributes[block]
            block['pointsTo'] = pointsTo
            
        if issubclass(eval(block['type']), Entity): # if there should be one object representing all of this char or not.
            if not 'char' in block:
                if char in self.chars:
                    block['char'] = self.chars[char]
                else:
                    block['char'] = char
            block['x'] = x
            block['y'] = y
            block['area'] = self
            block['loaded'] = self.loaded
            self.entities += [self.getObject(block)]
            if 'underChar' in block:
                self.grid[x][y] = block['underChar']
            else:
                self.grid[x][y] = ' '
            self.initBlock(x, y)
        else:
            if 'pointsTo' in block:
                realChar = block['pointsTo']
                realBlock = self.attributes[realChar]
                if not realChar in self.pointers:
                    self.pointers[realChar] = self.getObject(realBlock)
                else:
                    self.pointers[char] = self.pointers[realChar]
            else:
                if not char in self.pointers:
                    self.pointers[char] = self.getObject(block)
                        
    def getObject(self, block):
        objectName = block['type']
        if objectName in globals():
            if type(eval(objectName)) is types.TypeType: # Here's where I learned that
                return eval(objectName)(block)           # eval is the best thing ever
        else:
            return Block(block)

    def delEntity(self, entity):
        for i in range(len(self.entities)):
            if self.entities[i] is entity:
                del self.entities[i]
                return True
    
    def getBlock(self, player, x, y, edge=False):
        for entity in self.entities:
            if entity.x == x and entity.y == y:
                if edge:
                    if isinstance(entity, Edge):
                        return entity
                elif entity.visible and not entity is player:
                    return entity
        return self.pointers[self.grid[x][y]]
    
    def getBlockBeyondWarp(self, warp):
        areaName = warp.warpTo
        if not makeNewArea(areaName, self.loaded):
            return False
        area = self.loaded[areaName]
        x, y = area.findEntrance(warp.warpName)
        return area, x, y
    
class Menu:
    def __init__(self, items):
        self.items = items
        self.selected = 0
        self.scrollPosition = 0
        
    def getListing(self, width, height, cushion=0, margin=0):
        if len(self.items) < 1:
            return (' '*width + '\n')*height
        
        lines = []
        
        for i in range(len(self.items)):
            line = ''
            item = self.items[i]
            if i == self.selected:
                line += ' '*margin + '>'
                selectedLineUpperPosition = len(lines)
            else:
                line += ' '*margin + '-'
            
            if isinstance(item, Item):
                line += item.getPrintName()
            else:
                line += item
                
            lines += makeFit(line, width-1, indent=margin+1).split('\n')
            
            if i == self.selected:
                selectedLineLowerPosition = len(lines)-1
                
        while selectedLineLowerPosition - self.scrollPosition >= height - cushion and len(lines) - self.scrollPosition > height:
            self.scrollPosition += 1
        while selectedLineUpperPosition - self.scrollPosition < cushion and self.scrollPosition > 0:
            self.scrollPosition -= 1
            
        printLines = lines[self.scrollPosition:self.scrollPosition + height]
        
        if self.scrollPosition > 0:
            printLines[0] += ' '*(width-len(printLines[0])) + '^'
            
        if self.scrollPosition < len(lines) - height:
            printLines[-1] += ' '*(width-len(printLines[-1])) + unichr(8964)
            
        string = u''
        for line in printLines:
            try:
                string += line + '\n'
            except UnicodeDecodeError:
                string += line + '\n'
        string = string.rstrip()
        
        for i in range(height - len(lines)):
            string += '\n' + ' '*width
        
        return string
    
    def moveCursor(self, direction):
        if direction == 'up':
            self.selected = (self.selected - 1) % len(self.items)
        else:
            self.selected = (self.selected + 1) % len(self.items)
            
    def getInput(self, keyBindings):
        ch = getch()
        if ch == keyBindings['quit']:
            return False
        elif ch == keyBindings['up']:
            self.moveCursor('up')
            return True
        elif ch == keyBindings['down']:
            self.moveCursor('down')
            return True
        elif ch == keyBindings['select'] or ch == keyBindings['select2']:
            if len(self.items) > 0:
                return self.getSelected()
            else:
                return ''
            
    def getSelected(self):
        return self.items[self.selected]
            
    
############################################# CLASSES ############################################
##################################################################################################
##################################################################################################
############################################ FUNCTIONS ###########################################
    
def makeNewArea(areaName, loaded):
    if not loaded.has_key(areaName):
        if not os.path.exists(areaName + '.txt'):
            return False
        loaded[areaName] = Area(areaName, loaded)
    return True
        
def boxString(content, top, bottom, right, left, forceWidth=None, forceHeight=None, alert='', stickVertical='top', stickHorizontal='left'):
    content = content.split('\n')

    if forceWidth != None:
        for i in range(len(content)):
            if stickHorizontal == 'left':
                content[i] += ' '*(forceWidth - len(content[i]))
                if len(content[i]) > forceWidth:
                    content[i] = content[i][:forceWidth]
            else:
                content[i] = ' '*(forceWidth - len(content[i])) + content[i]
                if len(content[i]) > forceWidth:
                    content[i] = content[i][0-forceWidth:]

    if forceHeight != None:
        if stickVertical == 'top':
            content = content[:forceHeight]
            content += ['']*(forceHeight-len(content))
        else:
            content = content[0-forceHeight:]
            content = ['']*(forceHeight-len(content)) + content

    maxlen = 0
    for line in content:
        maxlen = max(maxlen, len(line))
    for i in range(len(content)):
        content[i] += ' '*(maxlen - len(content[i]))

    framed = []

    for char in top:
        if char == ' ':
            framed += [left + char*len(content[0]) + right]
        else:
            framed += [char*(len(content[0]) + len(right + left))]

    for i in range(len(content)):
        framed += [left + content[i] + right]

    for char in bottom:
        if char == ' ':
            framed += [left + char*len(content[0]) + right]
        else:
            framed += [char*(len(content[0]) + len(right + left))]

    string = ''
    for line in framed:
        string += line + '\n'

    if alert != '':
        string += '\n' + alert + '\n'

    string = string[:-1]

    return string
    
def barString(top, bottom, right, left, middle, spacing, info, fit=0): # '<space>' for empty space, -1 for fit space
    if len(info) != len(spacing):
        raise Exception('info and spacing must be same length')
    boxes = []

    for i in range(len(info)):
        if spacing[i] == -1:
            if info[i] == '<space>':
                tempSpacing = spacing
                tempSpacing[i] = 0
                spacing[i] = fit - len(barString(top, bottom, right, left, middle, tempSpacing, info).split('\n')[0])
        boxRight = right
        boxLeft = left
        if i != 0:
            if info[i-1] != '<space>':
                boxLeft = middle
        if i != len(info) - 1:
            if info[i+1] != '<space>':
                boxRight = ''
        if info[i] == '<space>':
            boxes += [boxString(' ' *spacing[i], ' '*len(top), ' '*len(bottom), '', '')]
        else:
            boxes += [boxString((u'{:' + str(spacing[i]) + u'}').format(info[i]), top, bottom, boxRight, boxLeft)]

    boxes = [x.split('\n') for x in boxes]
    maxlen = max(len(x) for x in boxes)
    boxes = [box + [(' '*len(box[0]))]*(maxlen - len(box)) for box in boxes]
    barList = boxes[0]
    del boxes[0]
    for box in boxes:
        for i in range(len(box)):
            barList[i] += box[i]

    string = ''
    for line in barList:
        string += line + '\n'
    string = string[:-1]

    return string
    
def getch():
    curses.flushinp()
    ch = stdscr.getch()
    if ch == -1:
        ch = None
    elif ch == 27:
        ch = stdscr.getch()
        if ch == -1:
            ch = 'ESCAPE'
        else:
            ch = stdscr.getch()
            if ch == 65:
                ch = 'UP'
            if ch == 66:
                ch = 'DOWN'
            if ch == 67:
                ch = 'RIGHT'
            if ch == 68:
                ch = 'LEFT'
    elif ch == 10:
        ch = 'RETURN'
    elif ch == ord(unicode(' ')):
        ch = 'SPACE'
    else:
        ch = unichr(ch)
    return ch
            
def makeFit(text, space, indent=0):
    text = text.replace('\n', ' \n ')
    text = text.split(' ')
    newText = []
    
    indent = ' '*indent
    n = 0
    for word in text:
        if word == '\n':
            newText += [word]
            n = 0
        elif len(word) + n > space:
            newText += ['\n', indent + word]
            n = len(word + indent) + 1
        else:
            newText += [word]
            n += len(word) + 1
    text = ''
    for word in newText:
        text += word
        if word != '\n':
            text += ' '
    text = text.rstrip()
        
    return text
    
def findVar(varname, string):
    try:
        start = string.index(varname + ':') + len(varname + ':')
        end = string[start:].index('\n') + start
        return string[start:end]
    except ValueError:
        return None

def readSave():
    xpos = None
    ypos = None
    area = None
    if os.path.isfile('cosmoSave.txt'):
        save = open('cosmoSave.txt','rw')
        save = unicode(save.read(), 'utf-8')
        xpos = findVar('xpos', save)
        ypos = findVar('ypos', save)
        area = findVar('area', save)
        xpos = xpos.strip()
        ypos = ypos.strip()
        area = area.strip()
    return xpos, ypos, area

def writeSave(xpos, ypos, area):
    save = open('cosmoSave.txt','w')
    string = ''
    
    string += 'xpos: ' + str(xpos) + '\n'
    string += 'ypos: ' + str(ypos) + '\n'
    string += 'area: ' + str(area) + '\n'
    
    save.write(string)
        
def main(stdscr):
    
    ########################
    # Boring curses stuff
    curses.noecho()
    curses.curs_set(0)
    curses.halfdelay(1)
    
    ########################
    # Getting save data if 'loadSave' is True
    playerProperties = {}
    
    loadSave = True
    
    enterFrom = None
    xpos, ypos, areaName = None, None, None
    if loadSave:
        xpos, ypos, areaName = readSave()
    if None in [xpos, ypos, areaName]:
        areaName = 'area1'
        enterFrom = 'house1Exit1'
    else:
        playerProperties['x'] = int(xpos)
        playerProperties['y'] = int(ypos)
    
    ########################
    # Loadin'
    loaded = {}
        
    makeNewArea(areaName, loaded)
    
    if not loaded is loaded[areaName].loaded:
        raise Exception("'loaded' duplicate created")
        # Just making sure.
        
    if enterFrom != None:
        playerProperties['x'], playerProperties['y'] = loaded[areaName].findEntrance(enterFrom)
        
    playerProperties['name'] = 'Cosmo' # Damn right it does.
    playerProperties['loaded'] = loaded
    playerProperties['area'] = loaded[areaName]
    playerProperties['areaName'] = areaName
    playerProperties['char'] = unichr(186)
    
    player = Player(playerProperties)
    
    ########################
    # THE WHOLE SHIBANG
    frame = Frame()
    frame.mainLoop(player, loaded)
    
    ########################
    # Friendly end of game message
    stdscr.clear()
    stdscr.addstr('Thanks for playing! Remember to always eat your oats!')
    stdscr.refresh()
    
    ########################
    # Wait for keypress
    while stdscr.getch() == -1:
        pass

    

if __name__ == '__main__':
    try:
        stdscr = curses.initscr()
        main(stdscr)
        curses.endwin()
    finally:
        if 'stdscr' in locals():
            stdscr.keypad(0)
            curses.flushinp()
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    
#184 = poop
#186 = cosmo
#8770 = bacon0
#8771 = bacon1