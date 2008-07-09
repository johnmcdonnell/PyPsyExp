#!/usr/bin/env python
# encoding: utf-8
"""
experiment.py

Created by Todd Gureckis on 2007-03-12.
Copyright (c) 2007 __Todd Gureckis__. All rights reserved.
"""

#------------------------------------------------------------
# import modules
#------------------------------------------------------------
import os, sys, signal
import math
from string import *
from numpy import *
from ftplib import FTP
from random import random, randint, shuffle
#from RandomArray import *
import pygame
from pygame.locals import *
import tempfile
from time import sleep

#------------------------------------------------------------
# MouseButton Class
#------------------------------------------------------------
class MouseButton:
    """Button class based on the
    template method pattern."""
    
    def __init__(self, x, y, w, h):
        self.rect = Rect(x, y, w, h)
    def containsPoint(self, x, y):
        return self.rect.collidepoint(x, y)        
    def do(self):
        print "Implemented in subclasses"


#------------------------------------------------------------
# General purpose Experiment class
#------------------------------------------------------------
class Experiment:
    """docstring for Experiment"""
    
    #------------------------------------------------------------
    # __init__
    #------------------------------------------------------------    
    def __init__(self, laptop, screenres, experimentname):
        pygame.init()
        if laptop:
            self.screen = pygame.display.set_mode(screenres, HWSURFACE|DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode(screenres, HWSURFACE|DOUBLEBUF|FULLSCREEN) 
        pygame.display.set_caption(experimentname)

        #self.filename = "data/%s.dat" % self.subj
        #self.datafile = open(self.filename, 'w')
        self.trial = 0
        self.resources = {}

    #------------------------------------------------------------
    # load_all_resources
    #------------------------------------------------------------    
    def load_all_resources(self, img_directory, snd_directory=""):
        self.load_all_images(img_directory)
        if snd_directory != "":
            self.load_all_sounds(snd_directory)

    #------------------------------------------------------------
    # load_all_images
    #------------------------------------------------------------
    def load_all_images(self, directory):
        """docstring for load_all_images"""
        # drop all . files
        files = filter(lambda x: x[0] != ".", os.listdir(os.path.join(os.curdir, directory)))
        files = filter(lambda x: x != 'Thumbs.db', files)
        full_path_files = map( lambda x: os.path.join(os.curdir, directory, x), files)
        images = map(lambda x: self.load_image(x), full_path_files)
        for i in range(len(files)): self.resources[files[i]]=images[i]
        
    #------------------------------------------------------------
    # load_all_sounds
    #------------------------------------------------------------
    def load_all_sounds(self, directory):
        """docstring for load_all_sounds"""
        files = filter(lambda x: x[0] != '.', os.listdir(os.path.join(os.curdir, directory)))
        files = filter(lambda x: x != 'Thumbs.db', files)
        full_path_files = map( lambda x: os.path.join(os.curdir, directory, x), files)
        sounds = map(lambda x: pygame.mixer.Sound(x), full_path_files)
        for i in range(len(files)): self.resources[files[i]]=sounds[i]
        
    #------------------------------------------------------------
    # load_image
    #------------------------------------------------------------
    def load_image(self, fullname, colorkey=None):
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print "Can't load image:", fullname
            raise SystemExit, message
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    #------------------------------------------------------------
    # get_cond_and_subj_number
    #------------------------------------------------------------
    def get_cond_and_subj_number(self, filename):
        t = []
        myfile = open(filename,'r')
        # read lines into t
        t = myfile.readlines()

        myfile.close()

        c = map(int, t)
        t = map(int, t) # convert to numbers and increment
        t[0] = (t[0]+1)%t[1]
        t[2] = t[2]+1
        f = map(lambda x: str(x) + '\n', t) # convert back to string

        myfile = open(filename,'w')
        myfile.seek(0)
        myfile.writelines(f)
        myfile.flush()
        myfile.close()
        return c

    #------------------------------------------------------------
    # get_cond_and_subj_number_ftp
    #------------------------------------------------------------
    def get_cond_and_subj_number_ftp(self, host, username, password, filename):
        t = []
        ftp = FTP(host, username, password) # connect to ftp host
        ftp.retrlines('RETR ' + filename, t.append) # get lines
        c = t = map(int, t) # convert to numbers and increment
        t[0] = (t[0]+1)%t[1]
        t[2] = t[2]+1
        f = map(lambda x: str(x) + '\n', t) # convert back to string
        myfile = tempfile.TemporaryFile()
        myfile.writelines(f)
        myfile.seek(0) # rewind to the beginning of the file
        ftp.storlines('STOR ' + filename, myfile)
        myfile.close() # close deletes the tmpfile
        return c

    #------------------------------------------------------------
    # upload_data
    #------------------------------------------------------------
    ## check to see if you can set netfilename to filename as a default
    def upload_data(self, host, username, password, filename, netfilename):
        """docstring for upload_data"""
        myfile = open(filename)
        ftp = FTP(host, username, password) # connect to ftp host
        ftp.storlines('STOR ' + netfilename, myfile)
        myfile.close() # close

    #------------------------------------------------------------
    # update_display
    #------------------------------------------------------------
    def update_display(self, mysurf):
        self.screen.blit(mysurf, (0,0))
        pygame.display.flip()

    #------------------------------------------------------------
    # place_text_image
    #------------------------------------------------------------
    def place_text_image(self, mysurf, prompt, size, xoff, yoff, txtcolor, bgcolor):
        text = self.get_text_image(pygame.font.Font(None, size), prompt, txtcolor, bgcolor)
        textpos = text.get_rect()
        textpos.centerx = mysurf.get_rect().centerx + xoff
        textpos.centery = mysurf.get_rect().centery + yoff
        mysurf.blit(text, textpos)

    #------------------------------------------------------------
    # get_text_image
    #------------------------------------------------------------
    def get_text_image(self, font, message, fontcolor, bg):
        base = font.render(message, 1, fontcolor)
        size = base.get_width(), base.get_height()
        img = pygame.Surface(size, 16)
        img = img.convert()
        img.fill(bg)
        img.blit(base, (0, 0))
        return img

    #------------------------------------------------------------
    # play_sound
    #------------------------------------------------------------
    def play_sound(self, sndname, pause):
        fileindex = sndname + ".wav"
        time_stamp = pygame.time.get_ticks()
        self.resources[fileindex].play()
        pygame.time.wait(int(self.resources[fileindex].get_length()*1000+pause))
        rt = pygame.time.get_ticks() - time_stamp
        filelen = int(self.resources[fileindex].get_length()*1000)
        #print "PLAY TIME  =", rt - filelen
 
    #------------------------------------------------------------
    # show_centered_image
    #------------------------------------------------------------
    def show_centered_image(self, imagename, bgcolor):
        return self.show_image(imagename, bgcolor, 0, 0)

    #------------------------------------------------------------
    # show_image
    #------------------------------------------------------------
    def show_image(self, imagename, bgcolor, xoffset, yoffset):
        """docstring for show_image"""
        size = self.screen.get_size()
        print size
        background = pygame.Surface(size)
        background = background.convert()
        background.fill(bgcolor)

        print background.get_rect().center
        
        image = self.resources[imagename]
        image_rect = image.get_rect()
        image_rect.centerx = background.get_rect().centerx + xoffset
        image_rect.centery = background.get_rect().centery + yoffset
        print image_rect.center
        background.blit(image,image_rect)
        return background
 
    #------------------------------------------------------------
    # clear_screen
    #------------------------------------------------------------
    def clear_screen(self, color):
        """docstring for clear_screen"""
        size = self.screen.get_size()
        background = pygame.Surface(size)
        background = background.convert()
        background.fill(color)
        return background

    #------------------------------------------------------------
    # show_centered_image_add
    #------------------------------------------------------------
    def show_centered_image_add(self, background, imagename, bgcolor):
        return self.show_image_add(background, imagename, 0, 0) 

    #------------------------------------------------------------
    # show_image_add
    #------------------------------------------------------------
    def show_image_add(self, background, imagename, xoffset, yoffset):
        """docstring for show_image"""
        image = self.resources[imagename]
        image_rect = image.get_rect()
        image_rect.centerx = background.get_rect().centerx + xoffset
        image_rect.centery = background.get_rect().centery + yoffset
        background.blit(image,image_rect)
        return background
               
    #------------------------------------------------------------
    # get_response_and_rt_pq
    #------------------------------------------------------------
    def get_response_and_rt_pq(self, val):
        time_stamp = pygame.time.get_ticks()
        while 1:
            res = self.get_response()
            if (res == 'Q' or res=='q'):
                res = val[0]
                break
            elif (res == 'P' or res=='p'):
                res = val[1]
                break
        
        rt = pygame.time.get_ticks() - time_stamp
        
        return [res, rt]

    #------------------------------------------------------------
    # get_response
    #------------------------------------------------------------
    def get_response(self):
        pygame.event.clear()
        if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
            self.on_exit()
        while 1:
            event = pygame.event.poll()
            if event.type == KEYDOWN:
                resp = pygame.key.name(event.key)
                if (resp > 96 and resp < 123):
                    resp -= 40
                if (resp == '[1]' or resp=='[2]' or resp=='[3]' or resp=='[4]' or resp=='[5]'):
                    resp = resp[1]
                return resp 

    #------------------------------------------------------------
    # escapable_sleep
    #------------------------------------------------------------
    def escapable_sleep(self, pause):
        waittime = 0    
        time_stamp = pygame.time.get_ticks()
        while waittime < pause:
            pygame.event.clear()
            if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                self.on_exit()
            waittime = pygame.time.get_ticks() - time_stamp

    #------------------------------------------------------------
    # output_trial
    #------------------------------------------------------------
    def output_trial(self, myline):     
        print myline
        for i in myline:
            self.datafile.write(str(i)+' ')

        self.datafile.write('\n')
        self.datafile.flush()

    #------------------------------------------------------------
    # placing_text
    #------------------------------------------------------------
    def placing_text(self, text, xoff, yoff, background):
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx + xoff
            textpos.centery = background.get_rect().centery + yoff
            return textpos

    #------------------------------------------------------------
    # on_exit
    #------------------------------------------------------------
    def on_exit(self):
        self.datafile.flush()
        self.datafile.close()
        exit()
        raise SystemExit

def main():
    pass

if __name__ == '__main__':
    main()

