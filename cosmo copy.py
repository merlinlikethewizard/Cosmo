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
Merlin Wizard
Zoë Wizard

Started 4/20/16
'''

import os
import time
from time import sleep
from math import ceil, floor

from cosmoObjects import *

####################################
import curses, locale              #
from curses import wrapper         # getch
                                   #
locale.setlocale(locale.LC_ALL,'') #
####################################

class Frame:
    def __init__(self, player, loaded):
        self.player = player
        self.loaded = loaded
        
        self.ratioAdjust = 1
        self.lockEdges = True
        self.mapWidth = 41
        self.mapHeight = 21
        
        self.upKey = 'UP'
        self.downKey = 'DOWN'
        self.rightKey = 'RIGHT'
        self.leftKey = 'LEFT'
    
    def update(self, alert='', title='', show='map', properties={}, showCoordinates=False):
        string = ''
        
        #TITLE
        string += boxString(title, '=', '', ' |', '| ')
        
        #MAIN BOX (MAP)
        string += '\n'
        if show == 'map':
            mainString = self.mapString(properties)
        elif show == 'inv':
            mainString = self.invString(properties)
        boxMain = boxString(mainString, '=', '=', '|', '|', forceWidth=self.mapWidth, forceHeight=self.mapHeight)
        string += boxMain
        
        #ALERT BOX
        string += '\n'
        string += boxString(makeFit(alert, self.mapWidth - 2), '', '=', ' |', '| ', forceWidth=self.mapWidth - 2, forceHeight=4)
        
        #HEALTH / MANA
        string += '\n'
        string += barString('', '=', ' |', '| ', ' | ', [13, -1, 13], ['HEALTH: ' + unichr(9829)*self.player.health, '<space>', ' MANA: ' + unichr(10209)*self.player.mana], self.mapWidth+2)
        
        #COORDS
        if showCoordinates:
            string += '\n'
            string += barString('=', '=', ' |', '| ', ' | ', [1, 1], ['x: ' + str(self.player.x), 'y: ' + str(self.player.y)])
        
        
        stdscr.clear()
        stdscr.addstr(string.encode('utf-8')) #main program draw fn
        stdscr.refresh()
    
    def mainLoop(self):
        self.gameOver = False
        
        self.alert = ''
        self.alertTime = time.time()
        self.inspect = False
        self.interact = False
        
        doUpdate = True
        
        while not self.gameOver:
            if self.playerAction():
                doUpdate = True
                
            if len(self.alert) > 0 and time.time()-self.alertTime > 5:
                self.alert = ''
                doUpdate = True

            if doUpdate:
                self.update(alert=self.alert, title=self.player.area.name)
                doUpdate = False
            
    def playerAction(self, update=False):
        doUpdate = False
        ch = getch()
        if ch in [self.upKey, self.downKey, self.leftKey, self.rightKey]:
            direction = {self.upKey:'up', self.downKey:'down', self.rightKey:'right', self.leftKey:'left'}[ch]
            if self.inspect:
                self.alert = self.player.doToBlock('inspect', direction)
                self.alertTime = time.time()
                self.inspect = False
            elif self.interact:
                val = self.player.doToBlock('interact', direction)
                if val != None:
                    self.alert = val
                    self.alertTime = time.time()
                self.interact = False
            else:
                val = self.player.doToBlock('move', direction)
                if val != None:
                    self.alert = val
                    self.alertTime = time.time()
            doUpdate = True

        if ch == ord(unicode('i')):
            self.interact = False
            if self.inspect:
                self.alert = self.player.doToBlock('inspect')
                self.alertTime = time.time()
                doUpdate = True
            self.inspect = not self.inspect

        if ch == ord(unicode(' ')):
            self.inspect = False
            if self.interact:
                val = self.player.doToBlock('interact')
                if val != None:
                    self.alert = val
                    self.alertTime = time.time()
                    doUpdate = True
            self.interact = not self.interact

        if ch == ord(unicode('o')):
            self.interact = False
            self.inspect = False
            self.openInv()
            doUpdate = True

        if ch == ord(unicode('q')):
            self.gameOver = True
            
        return doUpdate

    def openInv(self):
        selected = 0
        while True:
            value = '?'
            if self.player.items[selected].has_key('value'):
                value = self.player.items[selected]['value']
            self.update(title='Inventory', show='inv', properties={'selected':selected}, alert=('-' + self.player.items[selected]['name'] + '-\n' + makeFit(self.player.items[selected]['text'] + ' Value: ' + str(value), self.mapWidth - 2)))
            ch = getch()
            if len(self.player.items) > 0:
                if ch == 'UP':
                    selected = (selected - 1) % len(self.player.items)
                if ch == 'DOWN':
                    selected = (selected + 1) % len(self.player.items)
            if ch == ord(unicode(' ')) or ch == 'RETURN':
                return selected
            if ch == ord(unicode('o')):
                return None
            if ch == ord(unicode('q')):
                return None
                
    def mapString(self, properties):
        nullChar = ' '
        
        area = self.player.area
        x = self.player.x
        y = self.player.y
        
        positionx, positiony = x - int(floor(self.mapWidth/2.0)), y - int(floor(self.mapHeight/2.0))
        
        if self.lockEdges:
            if positionx < 0:
                positionx = 0
            if positiony < 0:
                positiony = 0
            if positionx > 0-(self.mapWidth - area.width):
                positionx = 0-(self.mapWidth - area.width)
            if positiony > 0-(self.mapHeight - area.height):
                positiony = 0-(self.mapHeight - area.height)
        
            if area.width <= self.mapWidth:
                positionx = int(floor((self.mapWidth - area.width)/-2.0))
            if area.height <= self.mapHeight:
                positiony = int(floor((self.mapHeight - area.height)/-2.0))
        
        grid = map(list,zip(*area.grid))
        string = ''
        
        for i in range(self.mapHeight):
            for j in range(self.mapWidth):
                if j > 0:
                    string += ' '*(self.ratioAdjust - 1)
                drawi, drawj = i + positiony, j + positionx
                if x == drawj and y == drawi:
                    string += self.player.playerChar
                elif drawi < 0 or drawj < 0 or drawi > area.height-1 or drawj > area.width-1:
                    string += nullChar
                else:
                    string += grid[drawi][drawj]
            string += '\n'
            
        string = string[:-1]
        
        return string

#        self.player.area.drawSelf(self.player, message=alert)
            
    def invString(self, properties):
        
        if not properties.has_key('selected'):
            properties['selected'] = 0
            
        items = self.player.items
        string = '\n'
        cursorPos = 0
        
        for i in range(len(items)):
            item = items[i]
            if i == properties['selected']:
                string += ' >'
            else:
                string += '  '
                
            string += item['name']
            
            if item['qty'] > 1:
                string += ' x ' + str(item['qty'])
                
            string += '\n'
            
#            name = item['name']
#            if i == properties['selected']:
#                name = '> ' + name
#            name = makeFit(name, 15)
#            if len(name[0]) > 19:
#                raise Excpetion('wtf?')
#            text = makeFit(item['text'], 15)
#            string += ' '*self.mapWidth + '\n' + barString('-', '-', ' |', '| ', ' | ', [1, 10, 3, 15, -1], ['<space>', name, '<space>', text, '<space>'], self.mapWidth) + '\n'
            if i == properties['selected']:
                cursorPos = len(string.split('\n'))
                
        for i in range(self.mapHeight - len(string.split('\n'))):
            string += '\n' + ' '*self.mapWidth
                
        if cursorPos > self.mapHeight:
            splitString = string.split('\n')[(cursorPos - self.mapHeight):]
            string = ''
            for line in splitString:
                string += line + '\n'
            string = string[:-1]
        
        return string

class Player:
    def __init__(self, loaded):
        self.playerChar = unichr(186)#9879       #186
        self.loaded = loaded
        self.items = []
        self.health = 5
        self.mana = 5
        
    def placeInArea(self, areaName, enterFrom=None, x=None, y=None):
        if not self.loaded.has_key(areaName):
            if not os.path.exists(areaName + '.txt'):
                return False
            self.loaded[areaName] = Area(areaName)
        self.area = self.loaded[areaName]
        if enterFrom != None:
            self.x, self.y = self.area.findEntrance(enterFrom)
        elif x > 0 and y > 0 and x < self.area.width and y < self.area.height:
            self.x, self.y = x, y
        else:
            raise Exception('Player not placed in a proper location (Off map or coordinates not given)')
        return True
    
    def doToBlock(self, action, direction=None):
        alert = None
        x = self.x
        y = self.y
            
        exec({'up':'y -= 1', 'down':'y += 1', 'right':'x += 1', 'left':'x -= 1', None:'pass'}[direction])
        
        edge = False
        if x < 0 or y < 0 or x > self.area.width-1 or y > self.area.height-1:
            edge = True
            x = self.x
            y = self.y
        
        block = self.area.attributes[self.area.blockingGrid[x][y]]
        blockType = block['type']
        
        warp = False
        item = False
        
        if action == 'move':
            if blockType in ['BLOCK', 'OBJECT', 'NPC']:
                return None
            elif edge and blockType == 'EDGE':
                warp = True
            elif blockType == 'EXIT':
                warp = True
            else:
                self.x = x
                self.y = y
                if blockType == 'ITEM':
                    item = True
        
        if action == 'inspect':
            return u'-{}- {}'.format(block['name'], block['text'])
        
        if action == 'interact':
            if blockType == 'NPC':
                if not block.has_key('interactions'):
                    block['interactions'] = 0
                name = block['name']
                imageName = block['imageName']
                textName = block['textNames'][block['interactions']]
                
                conversation(name, imageName, textName)
                
                if len(block['textNames']) - 1 > block['interactions']:
                    block['interactions'] += 1
            if blockType == 'ITEM':
                item = True
            else:
                alert = "There's nothing to do to this " + block['name']
                
        if item:
            firstOfThisType = True
            for item in self.items:
                if item['name'] == block['name']:
                    item['qty'] += 1
                    firstOfThisType = False
                    break
                    
            if firstOfThisType:
                block['qty'] = 1
                self.items += [block]
            
            alert = u'Obtained -{}-'.format(block['name'])
            self.area.blockingGrid[x][y] = ' '
            self.area.grid[x][y] = ' '
        
        if warp:
            self.placeInArea(block['warpto'], block['warpname'])
        
        return alert
        

class Area:
    def __init__(self, areaName):
        self.areaName = areaName
        
        area = open(areaName + '.txt','r')
        area = area.read()
        
        splitter = area.split('\n<splitter>\n')
        
        self.name =       splitter[0]
        self.area =       splitter[1].split('\n')
        self.blocking =   splitter[2].split('\n')
        self.attributes = splitter[3]
        self.chars =      splitter[4]
        
        self.area = map(list, zip(*self.area))
        self.blocking = map(list, zip(*self.blocking))
        
        exec('self.attributes = ' + self.attributes)
        exec('self.chars = ' + self.chars)
        
        self.grid = []
        for i in self.area:
            self.grid += [list(i)]
            
        self.blockingGrid = []
        for i in self.blocking:
            self.blockingGrid += [list(i)]
            
        self.width = len(self.grid)
        self.height = len(self.grid[0])
        
        self.initChars()
        
    def initChars(self):
        for key in self.chars:
            char = self.chars[key]
            for i in range(self.width):
                for j in range(self.height):
                    if self.grid[i][j] == key:
                        self.grid[i][j] = unichr(char)
    
    def findEntrance(self, entranceName):
        for key in self.attributes:
            att = self.attributes[key]
            if att['type'] == 'ENTER' or att['type'] == 'EDGE':
                if att['warpfrom'] == entranceName:
                    for i in range(self.width):
                        for j in range(self.height):
                            if self.blockingGrid[i][j] == key:
                                return i,j
                        
    # Old draw function, not used anymore.
    def drawSelf(self, player, message=None):
        grid = zip(*self.grid)
        grid = map(list,grid)
        grid[player.y][player.x] = player.playerChar
        string = ''
        for i in grid:
            line = ''
            for j in i:
                line += j
            string += line + '\n'
        stdscr.clear()
        if message != None:
            string += '\n' + str(message)
        stdscr.addstr(string.encode('utf-8'))
        stdscr.refresh()
        
def boxString(content, top, bottom, right, left, alert='', forceWidth=None, forceHeight=None):
    content = content.split('\n')

    if forceWidth != None:
        for i in range(len(content)):
            content[i] += ' '*(forceWidth - len(content[i]))
            if len(content[i]) > forceWidth:
                content[i] = content[i][:forceWidth]

    if forceHeight != None:
        content = content[:forceHeight]
        content += ['']*(forceHeight-len(content))

    maxlen = 0
    for line in content:
        maxlen = max(maxlen, realLen(line))
    for i in range(len(content)):
        content[i] += ' '*(maxlen - realLen(content[i]))

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
                testBar = barString(top, bottom, right, left, middle, tempSpacing, info)
                spacing[i] = fit - len(testBar.split('\n')[0])
        boxRight = right
        boxLeft = left
        if i != 0:
            if info[i-1] != '<space>':
                boxLeft = middle
        if i != len(info) - 1:
            if info[i+1] != '<space>':
                boxRight = ''
        if info[i] == '<space>':
            boxes += [boxString(' ' *spacing[i], ' '*realLen(top), ' '*realLen(bottom), '', '')]
        else:
            boxes += [boxString((u'{:' + str(spacing[i]) + u'}').format(info[i]), top, bottom, boxRight, boxLeft)]

    boxes = [x.split('\n') for x in boxes]
    maxlen = max(len(x) for x in boxes)
    boxes = [box + [(' '*len(box[0]))]*(maxlen - len(box)) for box in boxes]
    barString = boxes[0]
    del boxes[0]
    for box in boxes:
        for i in range(len(box)):
            barString[i] += box[i]

    string = ''
    for line in barString:
        string += line + '\n'
    string = string[:-1]

    return string
    
def getch():
    curses.flushinp()
    ch = stdscr.getch()
    if ch == -1:
        ch = None
    if ch == 27:
        ch = stdscr.getch()
        ch = stdscr.getch()
        if ch == 65:
            ch = 'UP'
        if ch == 66:
            ch = 'DOWN'
        if ch == 67:
            ch = 'RIGHT'
        if ch == 68:
            ch = 'LEFT'
    if ch == 10:
        ch = 'RETURN'
    return ch

def realLen(string):
    n = 0
    for s in string:
        if s == '\xc3':
            n += 1
        if s == '\xe2':
            n += 2
    return len(string) - n
    
def branchList(lines, layer=0):
    lineList = []
    while len(lines) > 0:
        line = lines[0]
        spacenum = len(line) - len(line.lstrip(' '))
        line = line.lstrip(' ')
        if spacenum == layer:
            del lines[0]
            lineList += [line]
        if spacenum < layer:
            return lineList
        if spacenum > layer:
            lineList += [branchDict(lines, layer+1)]
    return lineList

def branchDict(lines, layer):
    lineDict = {}
    while len(lines) > 0:
        line = lines[0]
        spacenum = len(line) - len(line.lstrip(' '))
        line = line.lstrip(' ')
        if spacenum == layer:
            del lines[0]
            lineDict[line] = branchList(lines, layer+1)
        if spacenum < layer:
            return lineDict
        if spacenum > layer:
            raise Exception('Improper conversation indentation')
    return lineDict

def say(text, attributes, conditions=None):
    image = open(attributes['imageName'] + '.txt','r')
    image = image.read()
    
    if attributes['flip']:
        flipimage = ''
        image = image.split('\n')
        for i in range(len(image)-1):
            flipimage += (image[i] + ' '*(attributes['bubbleWidth']-len(image[i])))[::-1].replace('/','<forward slash>').replace('\\','/').replace('<forward slash>','\\') + '\n'
        image = flipimage
        
    string = ''
    string += image
    string += bubble(text, attributes, 1)
    
    if conditions != None:
        topstring = string
        selected = 0
        while True:
            string = topstring
            string += '\n'
            for i in range(len(conditions)):
                pointer = i == selected
                string += bubble(conditions[i], attributes, 0, pointer, False)
            stdscr.clear()
            stdscr.addstr(string)
            stdscr.refresh()
            
            ch = getch()
            if ch == 'UP':
                if selected > 0:
                    selected -= 1
                else:
                    selected = len(conditions)-1
            if ch == 'DOWN':
                if selected < len(conditions)-1:
                    selected += 1
                else:
                    selected = 0
            if ch == ord(unicode(' ')) or ch == 'RETURN':
                return conditions[selected]
    
    stdscr.clear()
    stdscr.addstr(string)
    stdscr.refresh()
    
    ch = getch()
    while ch != ord(unicode(' ')) and ch != 'RETURN':
        ch = getch()

def branchRead(lines, attributes):
    while len(lines) > 0:
        if type(lines[0]) == type({}):
            raise Exception('Used dictionary before prompt')
        if len(lines) >= 2:
            if type(lines[1]) == type({}):
                response = say(lines[0], attributes, lines[1].keys())
                branchRead(lines[1][response], attributes)
                del lines[0:2]
            else:
                say(lines[0], attributes)
                del lines[0]
        else:
            say(lines[0], attributes)
            del lines[0]
            
def makeFit(text, space):
    text = text.split(' ')
#    raise Exception(text)
    newtext = []
    n = 0
    for word in text:
        if realLen(word) + n > space:
            newtext += ['<new line>', word]
            n = realLen(word) + 1
        else:
            newtext += [word]
            n += realLen(word) + 1
    text = ''
    for word in newtext:
        text += word + ' '
    text = text.replace(' <new line> ', '\n')
    return text[:-1]

def bubble(text, attributes, bubbleSpace, pointer=False, sayName=True):
    text = makeFit(text.strip(' '), attributes['bubbleWidth']-6)
    string = ''
    if sayName: #Put attributes['name'] at top of text bubble.
        string += '/' + '='*((attributes['bubbleWidth']-4)/2 - int(ceil(float(realLen(attributes['name']))/2))) + ' ' + attributes['name'] + ' ' + '='*((attributes['bubbleWidth']-4)/2 - int(floor(float(realLen(attributes['name']))/2))) + '\\\n'
    else:
        string += '/' + '='*(attributes['bubbleWidth']-2) + '\\\n'
        
    for i in range(bubbleSpace):
        string += '|' + ' '*(attributes['bubbleWidth']-2) + '|\n'

    firstline = True
    for line in text.split('\n'):
        if pointer and firstline:
            firstline = False
            string += '| > ' + line + ' '*(attributes['bubbleWidth']-(realLen(line)+5)) + '|\n'
        else:
            string += '| ' + line + ' '*(attributes['bubbleWidth']-(realLen(line)+3)) + '|\n'

    for i in range(bubbleSpace):
        string += '|' + ' '*(attributes['bubbleWidth']-2) + '|\n'
        
    string += '\\' + '='*(attributes['bubbleWidth']-2) + '/\n'
    return string
        
def conversation(name, imageName, textName, flip=False):
    imagetext = open(textName + '.txt','r')
    imagetext = imagetext.read()
    bubbleWidth = 50
    
    attributes = {'imageName':imageName, 'flip':flip, 'name':name, 'bubbleWidth':bubbleWidth}
                
    lines = branchList(imagetext.split('\n'))
    
    branchRead(lines, attributes)
    
#    first = True
#    while len(lines) > 0:
#        
#        
#        if first:
#            sleep(0.5)
#            first = False
#        curses.flushinp()
#        while not stdscr.getch() == ord(' '):
#            pass
        
def main(stdscr):
    curses.noecho()
    curses.curs_set(0)
    curses.halfdelay(1)
    
    
    
    
    loaded = {'area1':Area('area1')}
    player = Player(loaded)
    player.placeInArea('area1', enterFrom='house1Exit1')
    frame = Frame(player, loaded)
    frame.mainLoop()
    stdscr.clear()
    stdscr.addstr('Thanks for playing! Screw yourself sideways!')
    stdscr.refresh()
    while stdscr.getch() == -1:
        pass
    
    
    
    
#    while True:
#        stdscr.addstr(str(getch()))

#    conversation('Mom', 'mom', 'zoemomtext', True)

#    conversation('Mom', 'mom', 'momtext1')
#    stdscr.clear()
#    stdscr.refresh()
#    sleep(1)
#    conversation('Mommy', 'mom', 'momtext2',flip=True)
#    stdscr.clear()
#    stdscr.refresh()
#    sleep(1)
#    conversation('Mama', 'mom', 'momtext3')
#    stdscr.clear()
#    stdscr.refresh()
#    sleep(1)
#    conversation('Mother', 'mom', 'momtext4',flip=True)

    

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