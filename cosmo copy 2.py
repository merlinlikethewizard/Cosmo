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
        self.update()
    
    def update(self, alert=''):
        string = ''
        
        string += self.boxStr(self.player.area.name, '=', '', ' |', '| ')
        
        string += '\n'
        mapString = self.mapString()
        boxMap = self.boxStr(mapString, '=', '=', '|', '|')
        string += boxMap
        
        string += '\n'
        string += self.bar('', '', ' |', '| ', ' | ', [13, -1, 13], ['HEALTH: ' + unichr(9829)*self.player.health, '<space>', 'MANA: ' + unichr(11821)*self.player.mana], len(boxMap.split('\n')[0]))
        
        string += '\n'
        string += self.boxStr((u'{:' + str(realLen(mapString.split('\n')[0]) - 2) + u'}').format(alert), '=', '=', ' |', '| ')
        
        stdscr.clear()
        stdscr.addstr(string.encode('utf-8')) #main program draw fn
        stdscr.refresh()
        
    def bar(self, top, bottom, right, left, middle, spacing, info, fit=0):
        if len(info) != len(spacing):
            raise Exception('info and spacing must be same length')
        boxes = []
        
        for i in range(len(info)):
            if spacing[i] == -1:
                if info[i] == '<space>':
                    tempSpacing = spacing
                    tempSpacing[i] = 0
                    spacing[i] = fit - len(self.bar(top, bottom, right, left, middle, tempSpacing, info).split('\n')[0])
            boxRight = right
            boxLeft = left
            if i != 0:
                if info[i-1] != '<space>':
                    boxLeft = middle
            if i != len(info) - 1:
                if info[i+1] != '<space>':
                    boxRight = ''
            if info[i] == '<space>':
                boxes += [self.boxStr(' ' *spacing[i], ' '*realLen(top), ' '*realLen(bottom), '', '')]
            else:
                boxes += [self.boxStr((u'{:' + str(spacing[i]) + u'}').format(info[i]), top, bottom, boxRight, boxLeft)]

        boxes = [x.split('\n') for x in boxes]
        bar = boxes[0]
        del boxes[0]
        for box in boxes:
            for i in range(len(box)):
                bar[i] += box[i]
                
        string = ''
        for line in bar:
            string += line + '\n'
        string = string[:-1]
        
        return string
        
        
    
    def start(self):
        alert = ''
        alertTime = time.time()
        inspect = False
        interact = False
        
        up = 'UP'
        down = 'DOWN'
        right = 'RIGHT'
        left = 'LEFT'
        while True:
            update = False
            if len(alert) > 0 and time.time()-alertTime > 5:
                alert = ''
                update = True
            
            ch = getch()
            if ch in [up, down, left, right]:
                direction = {up:'up', down:'down', right:'right', left:'left'}[ch]
                if inspect:
                    alert = self.player.inspect(direction)
                    alertTime = time.time()
                    inspect = False
                elif interact:
                    val = self.player.interact(direction)
                    if val != None:
                        alert = val
                        alertTime = time.time()
                    interact = False
                else:
                    a = self.player.move(direction)
                    if a != None:
                        alert = a
                        alertTime = time.time()
                update = True
            if ch == ord(unicode('i')):
                interact = False
                if inspect:
                    alert = self.player.inspect()
                    alertTime = time.time()
                    update = True
                inspect = not inspect
            if ch == ord(unicode(' ')):
                inspect = False
                if interact:
                    val = self.player.interact()
                    if val != None:
                        alert = val
                        alertTime = time.time()
                        update = True
                interact = not interact
            if ch == ord(unicode('q')):
                break
                
            if update:
                self.update(alert)
                
    def mapString(self):
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

#       self.player.area.drawSelf(self.player, message=alert)

    def inv(self):
        items = self.player.items
        selected = 0
        while True:
            pass
            
        
    def boxStr(self, content, top, bottom, right, left, alert=''):
        content = content.split('\n')
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
        
    def move(self, direction):
        val = None
        x = self.x
        y = self.y
        exec({'up':'y -= 1', 'down':'y += 1', 'right':'x += 1', 'left':'x -= 1'}[direction])
        collide = self.area.collide(x, y, self.x, self.y)
        
        if collide[0] == 'warp':
            self.placeInArea(collide[1], collide[2])
        elif collide[0] == 'item':
            self.items += collide[1]
            self.x = x
            self.y = y
#            self.area.drawSelf(self, message=(u'Obtained -{}-'.format(collide[1]['name'])))
            val = u'Obtained -{}-'.format(collide[1]['name'])
        elif collide == 'free':
            self.x = x
            self.y = y
        
        return val
            
    def inspect(self, direction=None):
        x = self.x
        y = self.y
        exec({'up':'y -= 1', 'down':'y += 1', 'right':'x += 1', 'left':'x -= 1', None:'pass'}[direction])
        name, text = self.area.inspect(x,y)
#        self.area.drawSelf(self, message=(u'-{}- {}'.format(name, text)))
        return u'-{}- {}'.format(name, text)

    def interact(self, direction=None):
        x = self.x
        y = self.y
        exec({'up':'y -= 1', 'down':'y += 1', 'right':'x += 1', 'left':'x -= 1', None:'pass'}[direction])
        val = self.area.interact(self, x, y)
        if type(val) == type(''):
            return val
        if val == None:
            return None
        if val[0] == 'npc':
            npc = val[1]
            if not npc.has_key('interactions'):
                npc['interactions'] = 0
            name = npc['name']
            imageName = npc['imageName']
            textName = npc['textNames'][npc['interactions']]
            
            conversation(name, imageName, textName)
            
            if len(npc['textNames']) - 1 > npc['interactions']:
                npc['interactions'] += 1
        

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
        
    def collide(self, x, y, oldx, oldy):
        if x < 0 or y < 0 or x > self.width-1 or y > self.height-1:
            block = self.attributes[self.blockingGrid[oldx][oldy]]
            if block['type'] == 'EDGE':
                return ['warp', block['warpto'], block['warpname']]
            else:
                return 'blocked'
        block = self.attributes[self.blockingGrid[x][y]]
        blockType = block['type']
        if blockType == 'BLOCK':
            return 'blocked'
        if blockType == 'OBJECT':
            return 'blocked'
        elif blockType == 'EXIT':
            return ['warp', block['warpto'], block['warpname']]
        elif blockType == 'ITEM':
            self.grid[x][y] = ' '
            self.blockingGrid[x][y] = ' '
            return ['item', block]
        elif blockType == 'NPC':
            return 'blocked'
        else:
            return 'free'
            
    def inspect(self, x, y):
        if x < 0 or y < 0 or x > self.width-1 or y > self.height-1:
            return 'EDGE', 'The edge of this area. Do you continue?'
        blockName = self.attributes[self.blockingGrid[x][y]]['name']
        blockText = self.attributes[self.blockingGrid[x][y]]['text']
        return blockName, blockText
    
    def interact(self, player, x, y):
        if x < 0 or y < 0 or x > self.width-1 or y > self.height-1:
            return None
        block = self.attributes[self.blockingGrid[x][y]]
        blockType = block['type']
        if blockType == 'NPC':
            return ['npc', block]
        else:
            return None
    
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
    for line in text.split(' <new line> '):
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
    frame.start()
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