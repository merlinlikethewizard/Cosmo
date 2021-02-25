#!/usr/bin/python
# -*- coding=UTF-8 -*-
'''
========================================================================================================
    //////  //////  //////  //  //  //////        //////  /////   //////  //////  //////  //////  //////
   //      //  //  //      /\ ///  //  //        //  //  //  //    //    //      //        //    //
  //      //  //  //////  //\///  //  //        //  //  /////     //    //////  //        //    //////
 //      //  //      //  //  //  //  //        //  //  //  //  / //    //      //        //        //
//////  //////  //////  //  //  //////        //////  /////    //     //////  //////    //    //////.py
========================================================================================================
Merlin Wizard ||
Zoë Wizard ||
=============

A master file of objects in Cosmo
'''

import os
import time
import types
from math import ceil, floor

class Block(object):
    '''
    The Cosmo super class for all Blocks.
    Initialize an Block with a dict of proporties.
    '''
    def __init__(self, args, extraArgs=[]):
        neededArgs = extraArgs + ['name']
        
        for key in args:
            exec('self.' + str(key) + ' = args["' + str(key) + '"]')
        self.args = args.keys()
        
        for arg in neededArgs:
            if not arg in self.args:
                raise Exception("CosmoObject needs '" + arg + "' argument.")
                
        if not 'solid' in args:
            self.solid = False
        if not 'text' in args:
            self.text = ''
    
    def collide(self, player, direction):
        ''' Returns <True/False>, <alert>. True means object is not solid. '''
#        self.char = 'k'   # Great for testing types of blocks
        return not self.solid, None
    
    def getInfo(self, player):
        return self.name, self.text
    
    def interact(self, player):
        return False, "There's nothing to do to this " + self.name
    
class Entity(Block):
    def __init__(self, args, extraArgs=[]):
        extraArgs += ['loaded', 'area', 'x', 'y', 'char']
        super(Entity, self).__init__(args, extraArgs)
        if not 'maxHealth' in args:
            self.maxHealth = 5
        if not 'health' in args:
            self.health = self.maxHealth
        if not 'maxMana' in args:
            self.maxMana = 5
        if not 'mana' in args:
            self.mana = self.maxMana
        if not 'items' in args:
            self.items = []
        if not 'visible' in args:
            self.visible = True
        if not 'equipt' in args:
            self.equipt = None
                
    def update(self):
        return True
            
    def doToBlock(self, action, direction=None, setx=None, sety=None, area=None):
        if area == None:
            area = self.area
        
        x = self.x
        y = self.y
            
        exec({'up':'y -= 1', 'down':'y += 1', 'right':'x += 1', 'left':'x -= 1', None:'pass'}[direction])
        
        if not None in [setx,sety]:
            x = setx
            y = sety
        
        warp = False
        if x < 0 or y < 0 or x > area.width-1 or y > area.height-1:
            warp = True
            edge = area.getBlock(self, self.x, self.y, edge=True)
            warpArea, x, y = area.getBlockBeyondWarp(edge)
            block = warpArea.getBlock(self, x, y)
        else:
            block = area.getBlock(self, x, y)
            if isinstance(block, Exit) and action == 'move':
                warp = True
                warpArea, x, y = area.getBlockBeyondWarp(block)
                block = warpArea.getBlock(self, x, y)
        
        if action == 'move':
            notSolid, alert = block.collide(self, direction)
            if notSolid:
                self.x = x
                self.y = y
                if warp:
                    self.switchArea(warpArea)
            return notSolid, alert

        elif action == 'inspect':
            name, text = block.getInfo(self)
            return True, u'-{}- {}'.format(name, text)

        elif action == 'interact':
            return block.interact(self)
        
        return None, None
    
    def switchArea(self, area):
        self.area.delEntity(self)
        self.area = area
        if isinstance(self, Player):
            self.area.entities.insert(0,self)
        else:
            self.area.entities += [self]

class Player(Entity):
    def __init__(self, args, extraArgs=[]):
        extraArgs += []
        super(Player, self).__init__(args, extraArgs)
        
        self.area.entities.insert(0,self)
    
class NPC(Entity):
    def __init__(self, args, extraArgs=[]):
        extraArgs += []
        super(NPC, self).__init__(args, extraArgs)
        if not 'solid' in args:
            self.solid = True
        if 'imageName' in args:
            self.initImage()
        if 'textNames' in args:
            self.interactions = 0
            self.maxInteractions = len(self.textNames) - 1
            self.initTexts()
            if not 'paths' in args:
                self.paths = [None]*len(self.texts)
        
    def interact(self, player):
        if isinstance(player, Player):
            return self, None
        return False, "There's nothing to do to this " + self.name
    
    def openConversation(self):
        self.currentText = self.texts[self.interactions]
        if self.interactions < len(self.texts) - 1:
            self.interactions += 1
        self.path = [0]
            
    def talk(self, answer=None):
        text = self.currentText
        for n in self.path[:-1]:
            text = text[n]
        
        if answer != None:
            text = text[self.path[-1]][answer]
            self.path += [answer, 0]
            
        keepTalking = True
        traceback = False
        dialogue = ''
        responses = []
        if len(text) > self.path[-1]:
            dialogue = text[self.path[-1]]
            self.path[-1] += 1
            n = self.path[-1]
            if len(text) > n:
                if type(text[n]) is types.DictType:
                    responses = text[n].keys()
        else:
            if len(self.path) > 2:
                del self.path[-1]
                del self.path[-1]
                self.path[-1] += 1
                dialogue, responses, keepTalking = self.talk()
            else:
                keepTalking = False
                self.paths[self.interactions] = self.path
                
        return dialogue, responses, keepTalking
        
    def initImage(self):
        image = open(self.imageName + '.txt', 'r')
        self.image = unicode(image.read(), 'utf-8')
            
    def initTexts(self):
        self.texts = []
        for textName in self.textNames:
            text = open(textName + '.txt', 'r')
            text = unicode(text.read(), 'utf-8')
            text = text.split('\n')
            text = self.branchList(text)
            self.texts += [text]
        
    def branchList(self, lines, layer=0):
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
                lineList += [self.branchDict(lines, layer+1)]
        return lineList

    def branchDict(self, lines, layer):
        lineDict = {}
        while len(lines) > 0:
            line = lines[0]
            spacenum = len(line) - len(line.lstrip(' '))
            line = line.lstrip(' ')
            if spacenum == layer:
                del lines[0]
                lineDict[line] = self.branchList(lines, layer+1)
            if spacenum < layer:
                return lineDict
            if spacenum > layer:
                raise Exception('Improper conversation indentation')
        return lineDict
    
class Box(Entity):
    def __init__(self, args, extraArgs=[]):
        extraArgs += []
        super(Box, self).__init__(args, extraArgs)
        
    def collide(self, player, direction):
        result, alert = self.doToBlock('move', direction)
        return result, None
    
class Exit(Entity):
    def __init__(self, args, extraArgs=[]):
        extraArgs += ['warpTo', 'warpName']
        super(Exit, self).__init__(args, extraArgs)
        
    def collide(self, player, direction):
        return True, None
    
class Enter(Entity):
    def __init__(self, args, extraArgs=[]):
        extraArgs += ['warpFrom']
        super(Enter, self).__init__(args, extraArgs)
        if not 'visible' in args:
            self.visible = False
    
class Edge(Entity):
    def __init__(self, args, extraArgs=[]):
        extraArgs += ['warpTo', 'warpFrom', 'warpName']
        super(Edge, self).__init__(args, extraArgs)
        if not 'visible' in args:
            self.visible = False
        
    def collide(self, player, direction):
        return True, None
    
class Item(Entity):
    def __init__(self, args, extraArgs=[]):
        super(Item, self).__init__(args, extraArgs)
        if not 'value' in args:
            self.value = None
        if not 'qty' in args:
            self.qty = 1
        if not 'stackable' in args:
            self.stackable = True
        if not 'held' in args:
            self.held = False
        
    def collide(self, player, direction):
        return self.giveItem(player)
    
    def interact(self, player):
        return self.giveItem(player)
        
    def giveItem(self, player):
        if isinstance(player, Player):
            player.area.delEntity(self)
            found = False
            if self.stackable:
                for item in player.items:
                    if item.name == self.name:
                        item.qty += 1
                        found = True
                        break
            if not found:
                player.items.insert(0, self)
            return True, 'Obtained -' + self.name + '-'
        else:
            return True, 'Only cosmo can obtain this item.'
        
    def getPrintName(self):
        name = self.name
        if self.qty > 1:
            name += ' x ' + str(self.qty) + ' '
        if self.held:
            name += '[EQUIPT]'
            
        return name
        
class Well(Block):
    def __init__(self, args):
        super(Well, self).__init__(args)
        
    def collide(self, player, direction):
        if direction == 'up':
            return True, None
        else:
            return False, None
    
class Weapon(Item):
    def __init__(self, args, extraArgs=[]):
        super(Weapon, self).__init__(args, extraArgs)
        if not 'stackable' in args:
            self.stackable = False
    
class PortalGun(Weapon):
    def __init__(self, args, extraArgs=[]):
        super(PortalGun, self).__init__(args, extraArgs)