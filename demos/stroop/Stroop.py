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
from time import sleep
from lib.pypsyexp import *

###########################################################
# defines 
###########################################################
experimentname = 'stroop experiment'
experimentversion = '1.0'
laptop = True
white = (255, 255, 255)
grey = (175,175,175)
black = (0, 0, 0)

LAPTOPRES = (800, 800)
FULLSCREENRES = (1024, 768)
SINGLE = 0
DOUBLE = 1

# colors for stroop
red = (255,0,0)
blue = (0,0,255)
yellow = (228, 241, 20)
green = (0, 255, 0)


###########################################################
# StroopExperiment Class
###########################################################
class StroopExperiment(Experiment):
    def __init__(self, laptop, experimentname, experimentversion):
        
        global criteria, highprobside
        
        pygame.init()
        if laptop:
            screenres = LAPTOPRES
        else:
            screenres = FULLSCREENRES
        
        Experiment.__init__(self, laptop, screenres, experimentname)
        self.sd = -1
        self.seqtype = -1
        pygame.display.set_caption(experimentname)
        
        self.load_all_resources('images', 'sounds') ## this is from lib
        
        [self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode.txt')
        
        self.filename = "data/%s.dat" % self.subj ## have to change this to have the latest
        self.datafile = open(self.filename, 'w')  ## library function
        
        startline = "I am subject %s in condition %s using version %s of the %s project" % (self.subj, self.cond, experimentversion, experimentname)
        self.output_trial([startline])
        # to keep track of past responses
        self.responses = []
    
    ###########################################################
    # show_instructions
    ###########################################################
    def show_instructions(self, filename):
        background = self.show_centered_image(filename, white)
        self.update_display(background)
        
        ## below keeps it in a loop until the correct button is pressed
        rt, res = self.get_response_and_rt(keys=["n"])
    
    #------------------------------------------------------------
    # place_text_image
    #------------------------------------------------------------
    def place_text_image_rotate(self, mysurf, prompt, size, xoff, yoff, txtcolor, bgcolor, angle):
        text = self.get_text_image(pygame.font.Font(None, size), prompt, txtcolor, bgcolor)
        text=pygame.transform.rotate(text,180)
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
            self.place_text_image(background, word, 64, 0, 0, wordcolor, black)
        else:
            self.place_text_image_rotate(background, word, 64, 0, 0, wordcolor, black, 180)
        self.place_text_image(background, "Press 'r' for red,   Press 'g' for green,  Press 'y' for yellow,   Press 'b' for blue", 26, 0, 350, white, black)
        # show color
        
        self.update_display(background)
        
        # measure reaction time
        time_stamp = pygame.time.get_ticks()
        while 1:
            res = self.get_response()
            if res == 'r' or res == 'g' or res == 'y' or res == 'b':
                break
        rt = pygame.time.get_ticks() - time_stamp
        
        if res == correct_resp:
            hit = True
        else:
            hit = False
        
        # display feedback
        background = self.clear_screen(black)
        if hit==False:
            self.place_text_image(background, "Sorry that was incorrect!", 64, 0, 0, white, black)
        else:
            self.place_text_image(background, "Great!  That was correct!", 64, 0, 0, white, black)
        
        # display feedback
        self.update_display(background)
        sleep(1.0)
        
        background = self.clear_screen(black)
        self.update_display(background)
        sleep(0.8)
        
        self.current_trial += 1
        return [res,rt,hit]
    
    ###########################################################
    # show_thanks
    ###########################################################
    def show_thanks(self):
        
        global experimentname
        background = self.show_centered_image('thanks.jpg', white)
        
        # show subject number and experment name
        exp_text = "EXPERIMENT NAME: %s" % experimentname
        text = self.get_text_image(pygame.font.Font(None, 32), exp_text, black, white)
        textpos = self.placing_text(text, 0, 200, background)
        background.blit(text, textpos)
        
        subj_text = "SUBJECT NUMBER: %s" % self.subj
        text = self.get_text_image(pygame.font.Font(None, 32), subj_text, black, white)
        textpos = self.placing_text(text, 0, 250, background)
        background.blit(text, textpos)
        
        self.screen.blit(background, (0,0))
        pygame.display.flip()
        
        while 1:
            res = self.get_response()
    
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
        self.show_instructions('practiceword.jpg')
        
        nonwords=["KWLA","EXTM","BUTTER","FAST"]
        words=["BLUE","GREEN","RED","YELLOW"]
        colors=[blue,green,red,yellow]
        resp = ['b','g','r','y']
        
        
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
            [res,rt,hit]=self.do_stroop_trial(myword, mycolor, correct_resp, rotate=orientation)
        
        
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
        
        self.show_instructions('begin.jpg')
        
        
        nonwords=["CAR","HUNT","JXJT","PLXE"]
        words=["BLUE","GREEN","RED","YELLOW"]
        colors=[blue,green,red,yellow]
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
    global laptop, experimentname, experimentversion;
    experiment = StroopExperiment(laptop, experimentname, experimentversion)
    experiment.do_experiment()
    

###########################################################
# let's start
###########################################################

if __name__ == '__main__':
    main()

