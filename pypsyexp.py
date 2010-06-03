#!/usr/bin/env python
# encoding: utf-8
"""
pypsyexp.py

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
import numpy as np
import numpy.numarray as na
from scipy import ndimage
from array import *
from wave import open as W
import struct

#------------------------------------------------------------
# Useful RGB values
#------------------------------------------------------------
white = (255, 255, 255)
blue = (0, 0, 255)
black = (0, 0, 0)
red = (255, 0, 0)

#------------------------------------------------------------
# MouseButton Class
# Creates a Rect objects on initialization. Supports for 
# collidepoint method
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
    """The experiment class is a general purpose class."""
    
    #------------------------------------------------------------
    # __init__
    #
    #------------------------------------------------------------    
    def __init__(self, laptop, screenres, experimentname):
        """  Init takes three values:
                laptop - boolean
                    if laptop is True, the display created will be windowed. If false, the display will be
                    fullscreen.
                screenres - 2-value tuple or list representing pixel dimensions
                experimentname - string that will be displayed as the title of the new window """
        
        pygame.init()
        if laptop:
            self.screen = pygame.display.set_mode(screenres, HWSURFACE|DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode(screenres, HWSURFACE|DOUBLEBUF|FULLSCREEN) 
        pygame.display.set_caption(experimentname)

        self.trial = 0
        self.resources = {}

    #------------------------------------------------------------
    # load_all_resources
    #------------------------------------------------------------
    def set_filename(self, name=None):
        """ Sets and opens file to be written. If the name field is not passed, the datafile 
            opened is named the current subject number. """
        
        if name==None:
        	name = self.subj
        
        self.filename = "data/%s.dat" % name
        
        self.datafile = open(self.filename, 'w')

    #------------------------------------------------------------
    # load_all_resources
    #------------------------------------------------------------        
    def load_all_resources(self, img_directory, snd_directory=""):
        """ Accepts one or two values:
                img_directory - path to the folder containing images
                calls load_all_images
                snd_directory - path to the folder containing sounds. empty by default. 
                calls load_all_sounds if a path is passed. """
        self.load_all_images(img_directory)
        if snd_directory != "":
            self.load_all_sounds(snd_directory)

    #------------------------------------------------------------
    # load_all_images
    #------------------------------------------------------------
    def load_all_images(self, directory):
        """load_all_images takes 1 value, the path to the folder containing images.
           The function filters out 'Thumbs.db' files (in the case of Mac's) and
           hidden system files. All images are placed in a list called 'self.resources'. 
           All images must be referenced by name, i.e. self.resources['image1.gif']. """
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
        """load_all_sounds takes one value, the path to the folder containing sound files. 
            The function filters out 'Thumbs.db' files (in the case of Mac's and hidden 
            system files. All sounds are placed in a list called 'self.resources'. All
            sounds must be referenced by name, i.e. self.resources['sound1.wav'].play """
        files = filter(lambda x: x[0] != '.', os.listdir(os.path.join(os.curdir, directory)))
        files = filter(lambda x: x != 'Thumbs.db', files)
        full_path_files = map( lambda x: os.path.join(os.curdir, directory, x), files)
        sounds = map(lambda x: pygame.mixer.Sound(x), full_path_files)
        for i in range(len(files)): self.resources[files[i]]=sounds[i]
        
    #------------------------------------------------------------
    # load_image
    #------------------------------------------------------------
    def load_image(self, fullname, colorkey=None):
        """load_image attempts to load an image from the path passed to it in 
        'fullname', else an error is generated and the system exits. If colorkey 
        is not None, then the color passed will be made transparent. If colorkey = -1, 
        then the RGB value in the top left-most pixel of the image will be set as the colorkey"""
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
        """get_cond_and_subj_number reads a 'filename' that must contain at least 3 values:
           1) Condition current subject will be in
           2) Number of conditions
           3) Current subject number (automatically updated)
           
           After reading the textfile, the condition number and subject number are 
           automatically updated and written back into the file for subsequent runnings """
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
        self.subj = c[2]#for use in set_filename
        return c
 
    #------------------------------------------------------------
    # get_cond_and_subj_number_ftp
    #------------------------------------------------------------
    def get_cond_and_subj_number_ftp(self, host, username, password, filename):
        """Similar functionallity to get_cond_and_subj_number. get_cond_and_subj_number_ftp
           reads data from a remote ftp client in order to set up participant numbers and 
           conditions. 
           host - web address of file hosting site
           username - account name on the host site
           password - password for the account """
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
        """Uploads data to a file storage site."""
        myfile = open(filename)
        ftp = FTP(host, username, password) # connect to ftp host
        ftp.storlines('STOR ' + netfilename, myfile)
        myfile.close() # close

    #------------------------------------------------------------
    # update_display
    #------------------------------------------------------------
    def update_display(self, mysurf):
        """Blits the surface passed to the default display screen created by 
        the experiment class. Then flips it. """
        self.screen.blit(mysurf, (0,0))
        pygame.display.flip()

    #------------------------------------------------------------
    # place_text_image
    #------------------------------------------------------------
    def place_text_image(self, mysurf, prompt, size, xoff, yoff, txtcolor, bgcolor):
        """Blits a Text object to the surface passed.
            mysurf - Surface object to be blitted to
            prompt - String to be displayed
            size - text size
            xoff/yoff - center offsets
            txtcolor - color of the test (RGB)
            bgcolor - color of the background (RGB) """
        text = self.get_text_image(pygame.font.Font(None, size), prompt, txtcolor, bgcolor)
        textpos = self.placing_rect(mysurf, text, xoff, yoff)
        mysurf.blit(text, textpos)

    #------------------------------------------------------------
    # get_text_image
    #------------------------------------------------------------
    def get_text_image(self, font, message, fontcolor, bg):
        """ Creates a Surface with anti-aliased text written on it, and returns it.
            font - Font object
            message - string to be displayed
            fontcolor - color for text (RGB)
            bg - color for the background """
        base = font.render(message, 1, fontcolor, bg)
        size = base.get_width(), base.get_height()
        img = pygame.Surface(size, 16)
        img = img.convert()
        img.blit(base, (0, 0))
        return img
    
    #------------------------------------------------------------
    # placing_text
    # I revised this to work with place_text_image
    #------------------------------------------------------------
    def placing_rect(self, bkgd_surf, inner_surf, xoff, yoff):
        """ Creates a Rect from Surface 'inner_surf' and centers it based
            on Surface 'bkgd_surf'. Returns the Rect made """
        rect = inner_surf.get_rect()
        rect.centerx = bkgd_surf.get_rect().centerx + xoff
        rect.centery = bkgd_surf.get_rect().centery + yoff
        return rect
        
    #------------------------------------------------------------
    # play_sound
    #------------------------------------------------------------
    # Do we want it to return the "play time"? - yes
    def play_sound(self, sndname, pause):
        """ Plays a sound file for its length plus and length 'pause' in milliseconds.
            This function works with .wav files only. This pauses the timer as well
            sndname - String with the sound name (omit the .wav extension)
            pause - time in milliseconds to pause the pygame timer (added to the length of
            time of the sound file)  """
        time_stamp = pygame.time.get_ticks()
        self.resources[sndname].play()
        pygame.time.wait(int(self.resources[sndname].get_length()*1000+pause))
        rt = pygame.time.get_ticks() - time_stamp
        filelen = int(self.resources[sndname].get_length()*1000)
        print "PLAY TIME  =", rt - filelen
 
    #------------------------------------------------------------
    # show_centered_image
    #------------------------------------------------------------
    def show_centered_image(self, imagename, bgcolor, alpha=None):
        """Centers an image in the screen with a given bgcolor (RGB) """
        return self.show_image(imagename, bgcolor, 0, 0, alpha)

    #------------------------------------------------------------
    # show_image (for backward compatiblilty)
    #------------------------------------------------------------
    def show_image(self, imagename, bgcolor, xoffset, yoffset, alpha=None):
        """ Creates Surface object with the dimensions of the display screen. Then 
        blits an image to the center of the Surface plus any offseting height/width. 
        The Surface is then returned. 
        
        imagename - name of the image file loaded by load_image (or load_all_images)
        bgcolor - color of the surface
        xoffset/offset - offsets relative to the center of the Surface
        alpha - alpha value of the image
        
        Note: This CREATES a Surface object, whereas show_image_add is passed a Surface
        to be blitted on"""
        size = self.screen.get_size()
        background = pygame.Surface(size)
        background = background.convert()
        background.fill(bgcolor)

        image = self.resources[imagename]
        image_rect = image.get_rect()
        if alpha != None:
            image.set_alpha(alpha)
        image_rect.centerx = background.get_rect().centerx + xoffset
        image_rect.centery = background.get_rect().centery + yoffset
        
        background.blit(image,image_rect)
        return background
    
    #------------------------------------------------------------
    # show_centered_image_add
    #------------------------------------------------------------
    def show_centered_image_add(self, mysurf, imagename, bgcolor, alpha=None):
        """Centers an image in the Surface passed with a given bgcolor (RGB) """
        return self.show_image_add(mysurf, imagename, 0, 0, alpha)     
        
    #------------------------------------------------------------
    # show_image_add
    #------------------------------------------------------------
    def show_image_add(self, mysurf, imagename, xoffset, yoffset, alpha=None):
        """ Places an image onto a passed Surface with given offsets relative
        to the center of the Surface. Returns the drawn-on Surface.
        
        mysurf - Surface to be blitted to
        imagename - name of the image file loaded by load_image (or load_all_images)
        xoffset/offset - offsets relative to the center of the Surface
        alpha - alpha value of the image
        
        Note: This REQUIRES a Surface object to be passed, whereas show_image creates a Surface
        to be blitted on  """
        
        image = self.resources[imagename]
        image_rect = image.get_rect()
        if alpha != None:
            image.set_alpha(alpha)
        image_rect.centerx = mysurf.get_rect().centerx + xoffset
        image_rect.centery = mysurf.get_rect().centery + yoffset
        
        mysurf.blit(image,image_rect)
        return mysurf
 
    #------------------------------------------------------------
    # clear_screen
    # This may be more accurate if you pass the actual screen that
    # need to be cleared and flip it after filling it with a given color
    #------------------------------------------------------------
    def clear_screen(self, color):
        """ Creates a Surface with the dimensions of the display screen, fills
        it with a given color, and returns the Surface.  """
        size = self.screen.get_size()
        background = pygame.Surface(size)
        background = background.convert()
        background.fill(color)
        return background    
               
    #------------------------------------------------------------
    # get_response_and_rt_pq
    #------------------------------------------------------------
    def get_response_and_rt_pq(self, val):
        """ Monitors keyboard Events for the 'Q' and 'P' keys. Returns 
            the time it took from the call to the function to the end of the
            function (reaction time; rt) and the response made (res).
            val - list or tuple with coded values, e.g. ['Left', 'Right'] or 
            (0, 1) """
        
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
        """ Monitors keyboard Events. Converts lowercase input into uppercase
            based on ASCII codes. Pressing the left Shift and Tilde key (~/`) at the same time 
            will exit the program. Returns the key pressed. """
        pygame.event.clear()
        if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
            self.on_exit()
        while 1:
            event = pygame.event.poll()
            if event.type == KEYDOWN:
                resp = pygame.key.name(event.key)
                if (resp > 96 and resp < 123):
                    resp -= 40
                if (resp == '[1]' or resp=='[2]' or resp=='[3]' or resp=='[4]' or resp=='[5]' or resp == '[6]' or resp=='[7]' or resp=='[8]' or resp=='[9]' or resp=='[0]'):
                    resp = resp[1]
                return resp 
    #------------------------------------------------------------
    # prompt_text
    #------------------------------------------------------------
    def prompt_text(self, background, x, y, timelimit = None, prompt = '', fontsize = 32, maxlength = 40, color=black, centered = False):
        """
        Makes an onscreen prompt for users to enter a single line of text.
        
        Required arguments: 
            background -- the screen as it will be refreshed.
            x, y       -- These are upper-left coordinates of the textbox, unless 'centered' is set to True. 
                          When centered is True, x is the x offset from the center; y is unchanged.
        Optional keyword arguments:
            timelimit -- In ms. Default is None.
            prompt    -- To be printed in front of the typed text. Default is a null string.
            fontsize  -- Size of text printed on screen. Default is 32.
            maxlength -- Maximum number of characters allowed to be typed. Default is 40. 0 means unlimited.
            color     -- Color of text; tuple in (R, G, B). Default is black.
            centered  -- Maintain a centered alignment. x becomes offset of center if True. Default is False.
        
        Returns the typed text as it appeared on the screen.
        
        Possible future options:
            Restrictions on possible characters.
            Control over typeface.
        """
        pygame.event.clear()
        txtbx = TextPrompt(maxlength=maxlength, color=color, x=x, y=y, prompt = '', font = pygame.font.Font(None, fontsize))
        # create the pygame clock
        clock = pygame.time.Clock()
        
        timestamp = pygame.time.get_ticks()
        while 1:
            # make sure the program is running at 30 fps
            clock.tick(40)
            
            # events for txtbx
            events = pygame.event.get()
            # process other events
            if timelimit and pygame.time.get_ticks()-timestamp > timelimit:
                break
            if txtbx.value and pygame.key.get_pressed()[K_RETURN]:
                break
            if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                self.on_exit()

            # clear the screen
            screen = background
            self.screen.blit(screen, (0,0))
            
            # update txtbx
            txtbx.update(events)
            
            # blit txtbx on the sceen
            if centered:
                txtbx.center(screen, offset = x)
            txtbx.draw(self.screen)
            # refresh the display
            pygame.display.flip()
        return txtbx.value


    #------------------------------------------------------------
    # escapable_sleep
    #------------------------------------------------------------
    def escapable_sleep(self, pause):
        """ Pauses the program for 'pause'-number of milliseconds. Can be exited at any time
            by pressing the left Shift and Tilde key (~/`) at the same time  """
        
        waittime = 0    
        time_stamp = pygame.time.get_ticks()
        while waittime < pause:
            pygame.event.clear()
            if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                self.on_exit()
            waittime = pygame.time.get_ticks() - time_stamp

    #------------------------------------------------------------
    # output_trial
    # not currently in use
    #------------------------------------------------------------
    def output_trial(self, myline):  
        """ Writes a line a of data to a file, which each value seperated by a space. """   
        for i in myline:
            self.datafile.write(str(i)+' ')

        self.datafile.write('\n')
        self.datafile.flush()
        
    #------------------------------------------------------------
    # setup_gabor
    #------------------------------------------------------------
    def setup_gabor(self, grid_w, grid_h, windowsd):
        """ Sets up initial values for a gabor patch and its gaussian blur
            grid_w = width
            grid_h = height 
            windowsd = standard deviation  """
        
        self.gabor_w = grid_w
        self.gabor_h = grid_h
        self.windowsd = windowsd
        self.centerx= self.gabor_w/2
        self.centery = self.gabor_h/2        
        normalization=self.bivariate_normpdf(self.centerx,self.centery,self.windowsd,self.windowsd,self.centerx,self.centery,1.0)
        self.gabor_window = np.array([[ [self.bivariate_normpdf(i,j,self.windowsd,self.windowsd,self.centerx,self.centery,1.0)/normalization]*3 for j in range(self.gabor_w)] for i in range(self.gabor_h)],na.Float64)

    #------------------------------------------------------------
    # draw_gabor
    #------------------------------------------------------------
    def draw_gabor(self, freq, angle, scale):
        """ Draws the gabor patch set by 'setup_gabor' 
            freq - the frequency of the gabor patch
            angle - value to determine rotation on the patch
            scale - enlarges the gabor patch by a given factor
            
            * For faster blitting it is recommended to set the grid_w and grid_h 
            in 'setup_gabor' to be smaller than the actual patch desired. To offset 
            this, use the scale value to blow up the image. 
            ** Due to the nature of rotating a Surface, the size of the Surface the gabor patch
            changes based on the value of the rotation angle. This function re-centers the patch
            after each rotation, but it should be noted as it will make the area of the Surface
            larger. """

        
        gabor_surface = pygame.Surface([self.gabor_w,self.gabor_h], SRCALPHA)
        gabor_surface.fill(white)
        
        pixarray = pygame.surfarray.pixels3d(gabor_surface)
        pixrgb = np.array(pixarray)
        pixrgb[:,:,:]=0
        sinewavematrix = np.array([[ [((sin(degrees(j)/freq)+1)/2) * 255.0]  for j in range(self.gabor_w)]] * self.gabor_h) # to run faster, only compute the sine wave once
        finalimg = self.gabor_window * sinewavematrix
        finalimg = [[array('I', item) for item in line] for line in finalimg.tolist()]
        pixarray[:] = finalimg[:]
        # rotate
        gabor_surface.unlock()
        gabor_surface = pygame.transform.rotozoom(gabor_surface, angle, scale)
        # adjusts for the increase in size do to rotation
        gabor_rect = gabor_surface.get_rect()
        surf = pygame.Surface([gabor_rect.w, gabor_rect.h])
        surf_rect = surf.get_rect()
        surf.blit(gabor_surface, surf_rect) # returns a larger surface
        return surf
        
    #------------------------------------------------------------
    # bivariate_normpdf
    #------------------------------------------------------------   
    def bivariate_normpdf(self, x, y, sigma_x, sigma_y, mu_x, mu_y, mul):
        """ Formula used to set the gaussion blur 
            x,y - current position in the grid
            sigma_x/y - variance in each plane of the grid
            mu_x/y - mean
            mul - scales by this amplitude factor """ 
        return mul / (2.0*pi*sigma_x*sigma_y) * exp(-1.0/2.0*((x-mu_x)**2.0/sigma_x**2.0 + (y-mu_y)**2/sigma_y**2.0)) 
        
    #------------------------------------------------------------
    # on_exit
    # Not currently working due to self.datafile being commented out
    #------------------------------------------------------------
    def on_exit(self):
        """ Clears all data that remains on queue and closes the datafile set in set_filename """
        self.datafile.flush()
        self.datafile.close()
        exit()
        raise SystemExit
        
class Audio:
    def __init__(self, audio_path, data_path, abs_val, rel_val, sample_window):
        self.sample_window = sample_window
        self.audio_path = audio_path
        self.data_path = data_path
        self.abs_val = abs_val
        self.rel_val = rel_val
        
    def do_exp(self):
        splits, runtime, length = self.readwav(self.audio_path) # splits is a numpy array
        pc_data = self.read_data(self.data_path)
        self.cond = pc_data[0][6]
    
        [absolute_l, relative_l, windows_l] = self.histog(splits[0],length, self.sample_window) # beeps from computer
        print absolute_l, relative_l
    
        l_list = self.parsewav(splits[0], length, absolute_l, relative_l, self.sample_window, windows_l) # beeps from computer
        self.start = l_list[0][0] # every running of the experiment starts with a click noise to signal the start		
        l_list.pop(0) # takes out the start click out of analysis
        self.add_data(l_list)
        self.analyze(pc_data, l_list)
    
    def read_data(self, data):
        a = []
        dat = open(data, "rb")
        lines = dat.readlines()
        for i in lines:
            line =  i.split()
            a.append(line)
        return a
        
    def readwav(self, wavfilename): # reads the wave into 2 arrays of values
        w= W(wavfilename,'rb')
        (nchannel, width, rate, length, comptype, compname) = w.getparams()
        runtime = float(length)/rate
        frames = w.readframes(length)
        data = np.array(struct.unpack("%sh" %length*nchannel, frames), dtype=float).reshape(length,nchannel)
        splits = hsplit(abs(data), nchannel) # splits into left and right channels
        return splits, runtime, length	

    def histog(self, audio, length, window):
        absolute = relative = 0.0
        place_holder = window # need window again after some subtraction
        [values, bins] = np.histogram(audio, bins=(audio.max()-audio.min()),normed=True) # numpy

        absolute = where( cumsum(values) >= self.abs_val)[0][0]

        a = audio[0:] # start values
        b = append(audio[window+1:length], resize(np.array(0), window+1)).reshape(length,1) #end values	
        # next line adds neg(a) and b, and appends the sum of the first window to the start of the array		
        offsets = append( sum( audio[0 : window] ), sum( hstack( ( negative(a) , b ) ), axis = 1) )
        windows = cumsum( offsets )
        
        [values, bins] = histogram(windows, bins=(windows.max()-windows.min()), normed=True)
        relative = where ( cumsum( values ) >= self.rel_val )[0][0]

        return [absolute, relative, windows]	
        
    def parsewav(self, audio, length, absolute, relative, sample_window, windows_l): # gets sound points
        
        d = greater( audio, absolute ) #list of True/False based on whether indiv. samples are greater than absolute
        e = greater( windows_l[0:length].reshape(length,1), relative) # same, but for windows list
        f = logical_and( d, e )  # true = where both are true for both absolute and relative
        g = where( f == True )[0] # array where both absolute and relative are true
        h = g[1:len(g)].reshape(len(g)-1, 1) # new array from 1:len
        i = g[0:len(g)-1].reshape(len(g)-1, 1)  # new arrary from 0:len-1
        j = abs(sum( hstack( (negative(h), i) ), axis =1 )) # difference between g+h, stacked, sumed across and abs'd 	
        vals = append( 0, asarray(where( j > 8000 ))) # indices of where the correct points are	
        ms = (g[vals[:]+1]/44100.0).reshape(len(vals), 1).tolist()	# ms... somewhere 1 value is missing, so had to add it in		
        return ms
        
    def analyze(self, pc_data, l_channel):
        # pc_data = [  [trial, time since start, time since last click/press, RT, wait_time, response, cond] ]
        # l_channel =  [ [time(ms), time since start(ms), time since last ], ... [], [] ]
        new_array = []
        choice = pc_data
        if len(pc_data) <= len(l_channel):
            choice = pc_data
        else:
            choice = l_channel
        
        for i in range(len(choice)):
            new_array.append( [ pc_data[i][0], pc_data[i][1], (l_channel[i][1]*1000), ( float(pc_data[i][1]) - (l_channel[i][1]*1000) ), pc_data[i][2], l_channel[i][2], (float(pc_data[i][2])-l_channel[i][2]), pc_data[i][6] ] )

        print "[trial, since_start_PC, since_start_MIC, DIFF, since_click_PC, since_click_MIC, DIFF, COND]"
        for i in new_array:
            print i

    def add_data(self, l_channel):
        
        previous = self.start
        for i in range(len(l_channel)): # i here are lists
            time_since_last = l_channel[i][0] - previous
            l_channel[i].extend( [ l_channel[i][0] - self.start, (time_since_last*1000) ] )
            previous = l_channel[i][0]		    
    
class TextPrompt:
    """A text input prompt."""
    def __init__(self, **options):
        """ Options: x, y, font, color, restricted, maxlength, prompt. """
        
        defaults = dict(( ['x', 0], ['y', 0], ['font', pygame.font.Font(None, 32)],
                    ['color', (0,0,0)], ['restricted', '\'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\\\'()*+,-./:;<=>?@[\]^_`{|}~\''],
                    ['maxlength', -1], ['prompt', ''] ))
        
        self.options = {}
        for item in defaults.keys():
            if item in options:
                self.options[item] = options[item]
            else:
                self.options[item] = defaults[item]
        for item in options.keys():
            if item not in defaults.keys():
                raise Exception, "Keyword argument %s was not expected.", `item`
        
        self.x = self.options['x']
        self.y = self.options['y']
        self.font = self.options['font']
        self.color = self.options['color']
        self.restricted = self.options['restricted']
        self.maxlength = self.options['maxlength']
        self.prompt = self.options['prompt']; 
        self.value = ''
        self.shifted = False
    
    def center(self, background, offset = 0):
        self.x = background.get_rect().centerx + offset - (self.font.render(self.prompt+self.value, 1, self.color).get_width()/2)
    
    def set_pos(self, x, y):
        """ Set the position to x, y """
        self.x = x
        self.y = y

    def set_font(self, font):
        """ Set the font for the input """
        self.font = font

    def draw(self, surface):
        """ Draw the text input to a surface """
        text = self.font.render(self.prompt+self.value, 1, self.color)
        surface.blit(text, (self.x, self.y))

    def update(self, events):
        """ Update the input based on passed events """
        for event in events:
            if event.type == KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT: self.shifted = False
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE: self.value = self.value[:-1]
                elif event.key == K_LSHIFT or event.key == K_RSHIFT: self.shifted = True
                elif event.key == K_SPACE: self.value += ' '
                keydown = pygame.key.name( event.key )
                if self.shifted:
                    keydown = keydown.upper()
                    # This makes shifted symbols impossible. Manual fix:
                    conversion = dict( zip( "`1234567890-=[]\;',./", '~!@#$%^&*()_+{}|:"<>?' ) )
                    if keydown in conversion.keys():
                        keydown = conversion[ keydown ]
                if keydown in self.restricted:
                    self.value += keydown
        if self.maxlength >= 0: self.value = self.value[:self.maxlength]

def main():
    pass

if __name__ == '__main__':
    main()

