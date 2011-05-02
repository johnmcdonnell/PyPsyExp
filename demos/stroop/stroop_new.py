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
from random import random, randrange, choice
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
    # place_text_image_invert
    ###########################################################
    def place_text_image_invert(self, mysurf=None, prompt="", size=None, xoff=0, yoff=0, txtcolor=None, bgcolor=None, font=None, fontname=None ):
        """
        Identical to ``pypsyexp.place_text_image``, except it inverts the text.
        """
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
    def do_stroop_trial(self, word, wordcolor, correct_resp, rotate="normal"):
        # clear the screen
        background = self.clear_screen(black)
        
        # show word
        if rotate=="normal":
            self.place_text_image(prompt=word, txtcolor=wordcolor)
        elif rotate=="inverted":
            self.place_text_image_invert(prompt=word, txtcolor=wordcolor)
        else:
            msg = "ERROR: Invalid value for rotate: %s" % rotate
            self.on_exit( msg )
        self.place_text_image( prompt="Press 'r' for red,   Press 'g' for green,  Press 'y' for yellow,   Press 'b' for blue", size=26, xoff=0, yoff=350)
        self.update_display()
        
        # wait for response
        rt, res = self.get_response_and_rt( ['r', 'g', 'y', 'b'] )
        
        # decide if it was correct
        if res == correct_resp:
            hit = True
        else:
            hit = False
        
        # display feedback for 1000ms
        background = self.clear_screen(black)
        if hit==False:
            self.place_text_image(prompt="Sorry that was incorrect!")
        else:
            self.place_text_image(prompt="Great!  That was correct!")
        self.update_display()
        self.escapable_sleep(pause=1000)
        
        # Enforce an inter-trial interval of 800ms
        self.clear_screen()
        self.update_display()
        self.escapable_sleep(800)
        
        self.current_trial += 1
        return [res,rt,hit]
    
    ###########################################################
    # do_trial_block
    ###########################################################
    def do_trial_block(self, nonwords, words, colors, resp, respondto, n, allow_inverted=False):
        for i in range(n):
            if allow_inverted:
                orientation = choice( ["normal", "inverted"] )
            else:
                orientation = "normal"
            
            if respondto=="color":
                trialtype = choice( ["congruent", "incongruent",
                                     "control"] )
            else:
                trialtype = choice( ["congruent", "incongruent"] )
            
            if trialtype == "control":
                ri = randrange(len(nonwords))
                rc = randrange(len(colors))
                thisword = nonwords[ri]
                thiscolor = colors[rc]
                correct_resp = resp[rc]
            elif trialtype == "congruent":
                ri = randrange(len(words))
                thisword = words[ri]
                thiscolor = colors[ri]
                correct_resp = resp[ri]
            elif trialtype == "incongruent":
                ri=randrange(len(words))
                rc=randrange(len(words))
                while ri==rc:
                    rc=randrange(len(words))
                thisword = words[ri]
                thiscolor = colors[rc]
                correct_resp = resp[rc]
            else:
                msg = "ERROR: %s is not a valid trialtype." \
                        % trialtype
                self.on_exit(msg)
            
            res, rt, hit = self.do_stroop_trial(thisword, thiscolor,
                                                correct_resp,
                                                rotate=orientation)
            # Make a list of trial information to be output:
            trialinfo = [self.subj, self.cond, self.current_trial, thisword,
                         respondto, trialtype, orientation, correct_resp,
                         res, hit, rt]
            self.output_trial( trialinfo )
    
    ###########################################################
    # do_experiment
    ###########################################################
    def do_experiment(self):
        self.current_trial =0
        
        # show initial instructions
        self.show_instructions('maininstruction.jpg')
        
        # Basic parameters
        words=["BLUE","GREEN","RED","YELLOW"]
        colors=["blue","green","red","yellow"]
        resp = ['b','g','r','y']
        
        # Practice nonwords
        nonwords=["KWLA","EXTM","BUTTER","FAST"]
        
        # 5 practice trials responding to word
        respondto = "word"
        self.show_instructions('practiceword.jpg')
        self.do_trial_block( nonwords, words, colors, resp, respondto, 5, allow_inverted=False )
        
        # 5 practice trials responding to color
        respondto = "color"
        self.show_instructions('practicecolor.jpg')
        self.do_trial_block( nonwords, words, colors, resp, respondto, 5, allow_inverted=False )
        
        # The real experiment
        self.show_instructions('begin.jpg')
        
        # Different nonwords for the actual experiment:
        nonwords=["CAR","HUNT","JXJT","PLXE"]
        
        blockorder=["color","color","color","word","word"]
        shuffle(blockorder)
        for respondto in blockorder:
            if respondto == "color":
                self.show_instructions('respondtocolor.jpg')
            else:
                self.show_instructions('respondtoword.jpg')
        
            self.do_trial_block( nonwords, words, colors, resp, respondto, 100, allow_inverted=True )
        
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

