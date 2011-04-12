#!/usr/bin/pythonw
####
# Stroop Experiment for Lab in Human Cogntion
# programmed: July 30th, 2008 
# data collected july 2008+
####

###########################################################
# import modules 
###########################################################

import os, sys
import math
from random import random, randint
import pygame
from pygame.locals import *
import tempfile
from lib.pypsyexp import *

###########################################################
# defines 
###########################################################
experimentname = 'stroop experiment'
experimentversion = '2.0'
nofullscreen = True

LAPTOPRES = (800, 800)
FULLSCREENRES = (1024, 768)
SINGLE = 0
DOUBLE = 1


###########################################################
# StroopExperiment Class
###########################################################
class StroopExperiment(Experiment):
    def __init__(self, nofullscreen, screenres, experimentname, **options):
        Experiment.__init__(self, nofullscreen, screenres, experimentname, **options)
        
        startline = "I am subject %s in condition %s using version %s of the %s project" % (self.subj, self.cond, experimentversion, experimentname)
        self.output_trial([startline])
        
        # to keep track of past responses
        self.responses = []
    
    ###########################################################
    # show_instructions
    ###########################################################
    def show_instructions(self, filename):
        self.show_centered_image(filename, bgcolor="white" )
        self.update_display()
        
        ## below keeps it in a loop until the correct button is pressed
        rt, val = self.get_response_and_rt( keys=['n'] )
    
    #------------------------------------------------------------
    # place_text_image_rotate
    #------------------------------------------------------------
    def place_text_image_rotate(self, mysurf=None, prompt="", size=None, xoff=0, yoff=0, txtcolor=None, bgcolor=None, font=None, fontname=None ):
        if not mysurf:
            mysurf = self.background
        text = self.get_text_image(font=font, prompt=prompt, txtcolor=txtcolor, bgcolor=bgcolor)
        text = pygame.transform.rotate(text, 180)
        textpos = text.get_rect()
        textpos.centerx = mysurf.get_rect().centerx + xoff
        textpos.centery = mysurf.get_rect().centery + yoff
        mysurf.blit(text, textpos)
    
    ###########################################################
    # do_stroop_trial
    ###########################################################
    def do_stroop_trial(self, word, wordcolor, correct_resp, rotate=False):
        # clear the screen
        background = self.clear_screen(black)
        
        # show word
        if rotate==False:
            self.place_text_image(prompt=word, txtcolor=wordcolor)
        else:
            self.place_text_image_rotate(prompt=word, txtcolor=wordcolor)
        self.place_text_image( prompt="Press 'r' for red,   Press 'g' for green,  Press 'y' for yellow,   Press 'b' for blue", size=26, xoff=0, yoff=350)
        self.update_display()
        
        rt, res = self.get_response_and_rt( ['r', 'g', 'y', 'b'] )
        
        if res == correct_resp:
            hit = True
        else:
            hit = False
        
        # display feedback
        background = self.clear_screen(black)
        if hit==False:
            self.place_text_image(prompt="Sorry that was incorrect!")
        else:
            self.place_text_image(prompt="Great!  That was correct!")
        
        # display feedback
        self.update_display()
        self.escapable_sleep(pause=1000)
        
        self.clear_screen()
        self.update_display()
        self.escapable_sleep(800)
        
        self.current_trial += 1
        return [res,rt,hit]
    
    ###########################################################
    # show_thanks
    ###########################################################
    def show_thanks(self):
        #self.show_centered_image('thanks.jpg', "white")
        
        self.clear_screen('white')
        # show subject number and experment name
        exp_text = "EXPERIMENT NAME: %s" % self.experimentname
        subj_text = "SUBJECT NUMBER: %s" % self.subj
        
        self.place_text_image( prompt=exp_text, size=32, xoff=0, yoff=200, txtcolor="black", bgcolor="white" )
        self.place_text_image( prompt=subj_text, size=32, xoff=0, yoff=250, txtcolor="black", bgcolor="white" )
        self.update_display( )
        
        # Wait for spacebar to exit
        self.get_response_and_rt(keys=["space"])
    
    ###########################################################
    # do_experiment
    ###########################################################
    def do_experiment(self):
        self.current_trial =0
        
        # CODES FOR TRIALS
        # what are you responding to?
        WORD = 1
        COLOR = 2
        
        # what type of trial is it?
        CONTROL = 1
        CONGRUENT = 2
        INCONGRUENT = 3
        
        # is the word upside down?
        NORMAL = False
        INVERTED = True       
        
        # show initial instructions
        self.show_instructions('maininstruction.jpg')
        
        # Practice parameters
        nonwords=["KWLA","EXTM","BUTTER","FAST"]
        words=["BLUE","GREEN","RED","YELLOW"]
        colors=["blue","green","red","yellow"]
        resp = ['b','g','r','y']
        
        # 5 practice trials responding to word
        self.show_instructions('practiceword.jpg')
        
        respondto = WORD
        orientation = NORMAL
        for i in range(5):
            needle = random()
            if needle<.5:
                trialtype = CONGRUENT
                ri=randint(0,len(words)-1)
                myword = words[ri]
                mycolor = colors[ri]
                correct_resp = resp[ri]
            else:
                trialtype = INCONGRUENT
                ri=randint(0,len(words)-1)
                rc=randint(0,len(words)-1)
                while ri==rc:
                    rc=randint(0,len(words)-1)
                myword = words[ri]
                mycolor = colors[rc]
                correct_resp = resp[ri]
            # do trial
            res, rt, hit =self.do_stroop_trial(myword, mycolor, correct_resp, rotate=orientation)
        
        # 5 practice trials responding to color
        self.show_instructions('practicecolor.jpg')
        
        needle = random()
        respondto = COLOR
        for i in range(5):
            needle = random()
            if needle<(1./3.):
                trialtype = CONTROL
                ri=randint(0,len(nonwords)-1)
                rc=randint(0,len(colors)-1)
                myword = nonwords[ri]
                mycolor = colors[rc]
                correct_resp = resp[rc]
            elif (1./3.)<=needle<=(2./3.):
                trialtype = CONGRUENT
                ri=randint(0,len(words)-1)
                myword = words[ri]
                mycolor = colors[ri]
                correct_resp = resp[ri]
            else:
                trialtype = INCONGRUENT
                ri=randint(0,len(words)-1)
                rc=randint(0,len(words)-1)
                while ri==rc:
                    rc=randint(0,len(words)-1)
                myword = words[ri]
                mycolor = colors[rc]
                correct_resp = resp[rc]
            # do trial
            [res,rt,hit]=self.do_stroop_trial(myword, mycolor, correct_resp, rotate=orientation)
        
        # The real experiment
        self.show_instructions('begin.jpg')
        
        nonwords=["CAR","HUNT","JXJT","PLXE"]
        words=["BLUE","GREEN","RED","YELLOW"]
        colors=["blue","green","red","yellow"]
        resp = ['b','g','r','y']
        
        
        blockorder=[COLOR,COLOR,COLOR,WORD,WORD]
        shuffle(blockorder)
        for respondto in blockorder:
            if respondto == COLOR:
                self.show_instructions('respondtocolor.jpg')
            else:
                self.show_instructions('respondtoword.jpg')
        
            # congruent
            for i in range(100):
                # rotate
                if random()<=.5:
                    orientation = NORMAL
                else:
                    orientation = INVERTED
                
                needle = random()
                if respondto==COLOR:
                    if needle<(1./3.):
                        trialtype = CONTROL
                        ri=randint(0,len(nonwords)-1)
                        rc=randint(0,len(colors)-1)
                        myword = nonwords[ri]
                        mycolor = colors[rc]
                        correct_resp = resp[rc]
                    elif (1./3.)<=needle<=(2./3.):
                        trialtype = CONGRUENT
                        ri=randint(0,len(words)-1)
                        myword = words[ri]
                        mycolor = colors[ri]
                        correct_resp = resp[ri]
                    else:
                        trialtype = INCONGRUENT
                        ri=randint(0,len(words)-1)
                        rc=randint(0,len(words)-1)
                        while ri==rc:
                            rc=randint(0,len(words)-1)
                        myword = words[ri]
                        mycolor = colors[rc]
                        correct_resp = resp[rc]
                else: # respond to word
                    if needle<.5:
                        trialtype = CONGRUENT
                        ri=randint(0,len(words)-1)
                        myword = words[ri]
                        mycolor = colors[ri]
                        correct_resp = resp[ri]
                    else:
                        trialtype = INCONGRUENT
                        ri=randint(0,len(words)-1)
                        rc=randint(0,len(words)-1)
                        while ri==rc:
                            rc=randint(0,len(words)-1)
                        myword = words[ri]
                        mycolor = colors[rc]
                        correct_resp = resp[ri]
                
                # do trial
                [res,rt,hit]=self.do_stroop_trial(myword, mycolor, correct_resp, rotate=orientation)
                self.output_trial([self.subj, self.cond, self.current_trial, myword, respondto, trialtype, orientation, correct_resp, res, hit, rt])
        
        
        self.show_thanks()
        

###########################################################
# main
###########################################################

def main():
    #global nofullscreen, experimentname, experimentversion;
    options = dict(
          experimentversion = experimentversion
        , patterncode = "patterncode.txt"
        , imagedir = "images"
        , sounddir = "sounds"
        , fgcolor = "white"
        , bgcolor = "black"
        , fontsize = 64
    )
    if nofullscreen:
        screenres = LAPTOPRES
    else:
        screenres = FULLSCREENRES
    experiment = StroopExperiment(nofullscreen, screenres, experimentname, **options)
    experiment.do_experiment()
    

###########################################################
# let's start
###########################################################

if __name__ == '__main__':
    main()

