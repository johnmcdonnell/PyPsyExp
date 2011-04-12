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
#from string import *
import numpy as np
from random import random, randint, shuffle
#from RandomArray import *
from ftplib import FTP
import pygame
import pygame.locals as pglc
#from pygame.locals import *
import tempfile
from time import sleep
import numpy as np
import numpy.numarray as na
from scipy import ndimage
#from array import *
from wave import open as W
import struct
from warnings import warn

# Colors
white = pygame.color.THECOLORS['white']
blue = pygame.color.THECOLORS['blue']
black = pygame.color.THECOLORS['black']
red = pygame.color.THECOLORS['red']

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

def pgColor( colorid ):
    if type( colorid ) == str:
        try:
            return pygame.color.THECOLORS[colorid]
        except KeyError, message:
            warn( "Could not find color %s" % colorid )
            raise SystemExit, message
    # must be an RGB code...
    elif hasattr( colorid, '__contains__' ):
        if len( colorid ) == 3 or len( colorid ) == 4:
            return colorid
        else:
            msg =  "Invalid rgb key: %s" % colorid
            raise SystemExit, msg
    else:
        msg = "Invalid color value : %s" % colorid
        raise SysetmExit, msg



#------------------------------------------------------------
# General purpose Experiment class
#------------------------------------------------------------
class Experiment:
    """The experiment class is a general purpose class."""
    #------------------------------------------------------------
    # __init__
    #------------------------------------------------------------    
    def __init__(self, screenres, experimentname, **useroptions):
        """  
        Args:
         * nofullscreen (bool):
            * If ``nofullscreen`` is ``True``, the display created will be
              windowed.
            * If ``False`` (the default), the display will be fullscreen.
         * ``screenres`` (tuple of ints): 2-value tuple or list representing
           pixel dimensions.
         * ``experimentname`` (str): string that will be displayed as the title
           of the new window.
        Kwargs:
         * ``fontname`` (str): Name of default font.
         * ``fontsize`` (int): Size of default font.
         * ``bgcolor`` (str or tuple): Backgound color. Default is white.
           String or rgb tuple.
         * ``fgcolor`` (str or tuple): Foreground color. Default is black.
           String or rgb tuple
         * ``patterncode`` (str): Name of patterncode file. Defaults to
           ``patterncode.txt`` but is only loaded if it is passed in.
         * ``imagedir`` (str): Directory images are in. Defaults to ``images``,
           but they are only loaded if it is passed in.
         * ``sounddir`` (str): Directory sounds are in. Defaults to ``sounds``,
           but they are only loaded if it is passed in.
         * ``datadir`` (str): Folder the datafiles will be stored in. Defaults
           to ``data``
         * ``ftphost`` (str): FTP host name
         * ``ftpuser`` (str): FTP user name
         * ``ftppassword`` (str): FTP password
         * ``verbose`` (bool): Print extra messages? Default is true.
         * ``framerate`` (int): Polling rate in fps.
         * ``suppresspygame`` (bool): Try not to use any pygame UI functions.
        """
        
        ### Reading in options/ setting defaults/ initalizing files.
        defaults = dict(
            font = None,
            fontname = None,
            fontsize = 32,
            fgcolor = "black",
            bgcolor = "white",
            patterncode = "",
            datadir = "data",
            outfilename = "",
            imagedir = "images",
            soundsdir = "sounds",
            ftphost = "",
            ftpuser = "",
            ftppassword = "",
            verbose = True,
            nofullscreen = False,
            framerate = 40,
            suppresspygame = False
        )
        
        self.options = defaults
        self.options.update( useroptions )
        
        self.resources = {}
        self.bgcolor = pgColor( self.options["bgcolor"] )
        self.fgcolor = pgColor( self.options["fgcolor"] )
        self.fontname = self.options["fontname"]
        self.fontsize = self.options["fontsize"]
        self.patterncode = self.options["patterncode"]
        self.datadir = self.options["datadir"]
        self.outfilename = self.options["outfilename"]
        self.imagedir = self.options["imagedir"]
        self.soundsdir = self.options["soundsdir"]
        self.ftphost = self.options["ftphost"]
        self.ftpuser = self.options["ftpuser"]
        self.ftppassword = self.options["ftppassword"]
        self.verbose = self.options["verbose"]
        self.nofullscreen = self.options["nofullscreen"]
        self.framerate = self.options["framerate"]
        self.suppresspygame = self.options["suppresspygame"]
        
        if self.options["patterncode"]:
            self.get_cond_and_subj_number( useroptions["patterncode"] )
            self.set_filename( self.outfilename )
        else:
            warning = """
            WARNING: No patterncode file passed." self.cond, self.ncond, and
            self.subj will not be set unless self.get_cond_and_subj_number is
            called separately. Also, no datafile will be automatically loaded.
            Calls to patterncode will default to assume that 'patterncode.txt'
            is the filename.
            """
            warn( warning )
        if "imagesdir" in useroptions.keys() and useroptions["imagesdir"]:
            self.load_all_images( directory = useroptions["imagesdir"] )
        if "soundsdir" in useroptions.keys() and useroptions["imagesdir"]:
            self.load_all_sounds( directory = useroptions["imagesdir"] )
        
        # UI initialization
        if not self.suppresspygame:
            pygame.init()
            if self.nofullscreen:
                self.screen = pygame.display.set_mode(screenres,
                    pglc.HWSURFACE|pglc.DOUBLEBUF)
            else:
                self.screen = pygame.display.set_mode(screenres,
                    pglc.HWSURFACE|pglc.DOUBLEBUF|pglc.FULLSCREEN) 
            pygame.display.set_caption(experimentname)
            self.font = pygame.font.SysFont( self.fontname, self.fontsize )
            self.background = self.clear_screen()
            self.clock = pygame.time.Clock()
        
        self.trial = 0
    
    #------------------------------------------------------------
    # set_filename
    #------------------------------------------------------------
    def set_filename(self, name=None):
        """ 
        Sets and opens file to be written. If the name field is not
        passed, the datafile opened is named the current subject
        number. 
        
        Kwargs:
         * ``name`` (str): The filename.
        
        Sets:
         * ``self.filename``
         * ``self.datafile``
        """
        
        if name == None:
            name = `self.subj` + ".dat"
        
        self.filename = os.path.join( self.datadir, name )
        self.datafile = open(self.filename, 'w')
    
    #------------------------------------------------------------
    # load_all_resources
    #------------------------------------------------------------        
    def load_all_resources(self, img_directory="", snd_directory=""):
        """ 
        Loads images and sounds by calling ``load_all_images`` and
        ``load_all_sounds``.
        
        Kwargs:
         * ``img_directory`` (str): Path to the folder containing
           images.
         * ``snd_directory`` (str): Path to the folder containing
           sounds.
        """
        if not img_directory and not snd_directory:
            raise Exception, "No filenames passed to load_all_resources."
        if img_directory:
            self.load_all_images(img_directory)
        if snd_directory:
            self.load_all_sounds(snd_directory)
    
    #------------------------------------------------------------
    # load_all_images
    #------------------------------------------------------------
    def load_all_images(self, directory=""):
        """
       Loads images and places their corresponding objects into
       ``self.resources``. Filters out ``Thumbs.db`` files (in the case of
       Macs) and hidden system files. The function filters out ``Thumbs.db``
       files (in the case of Macs) and UNIX system files (starting with ``.``).
       All images are placed in a list called ``self.resources``.  All images
       must be referenced by name, e.g.  ``self.resources['image1.gif']``. 
        
       Kwargs:
        * ``directory`` (str): Path to the folder containing images.
       
       Modifies:
           ``self.resources``
       """
        if not directory:
            raise Exception, "No directory passed to load_all_images."
        files = [ fn for fn in os.listdir(os.path.join( os.curdir, directory ))
                 if fn[0] != "." and fn!="thumbs.db" ]
        full_path_files = [ os.path.join( os.curdir, directory, fn) 
                           for fn in files ]
        images = [ self.load_image( fn ) for fn in full_path_files ]
        for fn in full_path_files:
            self.resources[ fn ] = self.load_image( fn )
    
    #------------------------------------------------------------
    # load_all_sounds
    #------------------------------------------------------------
    def load_all_sounds(self, directory=""):
        """
        ``load_all_sounds`` takes one value, the path to the folder containing
        sound files.  The function filters out ``Thumbs.db`` files (in the case
        of Macs) and UNIX system files (starting with ``.``). All sounds are
        placed in a list called ``self.resources``. All sounds must be
        referenced by name, i.e.  ``self.resources['sound1.wav'].play()``
        
        Kwargs:
         * ``directory`` (str): Path to the folder containing images.
        
        Updates:
            ``self.resources``
        """
        if not directory:
            raise Exception, "No directory passed to load_all_images."
        files = [ fn for fn in os.listdir(os.path.join( os.curdir, directory ))
                 if fn[0] != "." and fn!="thumbs.db" ]
        full_path_files = [ os.path.join( os.curdir, directory, fn) 
                           for fn in files ]
        sounds = [ pygame.mixer.Sound( fn ) for fn in full_path_files ]
        self.resources.update( files, sounds )
    
    #------------------------------------------------------------
    # load_image
    #------------------------------------------------------------
    def load_image(self, filename, colorkey=None):
        """
        Attempts to load an image given its filename.
        
        It has two means of determining which color will be made transparent:
        1. If ``colorkey`` is not ``None``, then the color passed will be made
           transparent.  If ``colorkey`` is ``-1``, then the RGB value in the
           top left-most pixel of the image will be set as the colorkey.
        2. If the filename is of the format ``*-transp-x-y.EXT``, where ``EXT``
           is the file e``x``tension, then ``x`` and ``y`` are the ``x`` and
           ``y`` coordinates of the pixel that will be made transparent.
        If neither of these conditions are met, the image will not have
        transparency.

        Args:
         * ``filename`` (str): path to image file.
        
        Kwargs:
         * ``colorkey`` (tuple of ints): path to image file.
        
        Returns:
            The resulting image object.
        
        Raises:
            ``pygame.error``
        """
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            warn( "Can't load image: %s" % fullname )
            raise SystemExit, message
        image = image.convert()
        # Deciding which pixel should be transparent:
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        else:
            partfn = fullname.split( '.' )[ -2]
            transpkeys = partfn.split( '-' )[-3:]
            if transpkeys[0] == "transp":
                try:
                    colorkey = image.get_at( map( int, transpkeys[1:] ) )
                    image.set_colorkey(colorkey, RLEACCEL)
                except Exception, message:
                    warn( "WARNING: Unable to set color key for file %s." % fullname )
                    warn( message )
        return image
    
    #------------------------------------------------------------
    # get_cond_and_subj_number
    #------------------------------------------------------------
    def get_cond_and_subj_number(self, filename=""):
        """
        Reads a patterncode file that must contain the following three values
        on its first three lines:
         1. Condition current subject will be in.
         2. Number of conditions.
         3. Current subject number (automatically updated).
        
        After reading the text file, the condition number and subject number
        are automatically updated and written back into the file for subsequent
        runnings.
        
        Kwargs:
         * ``filename`` (str): Path to the patterncode file. Defaults to
           ``patterncode.txt``
        
        Returns:
            A list of the items in the file, in int form.
        """
        if not filename:
            filename = self.patterncode
        try:
            myfile = open(filename,'r')
        except IOError, msg:
            mymsg = """
            get_cond_and_subj_number could not find the patterncode 
            file (which was expected at %s )
            """ % filename
            warn( msg )
            warn( mymsg )
            raise SystemExit
        lines = myfile.readlines()
        myfile.close()
        
        outlines = read_patterncode_lines( lines )
        myfile = open(filename,'w')
        myfile.seek(0)
        myfile.writelines( outlines )
        myfile.flush()
        myfile.close()
        
        return map( int, lines )
    
    #------------------------------------------------------------
    # get_cond_and_subj_number_ftp
    #------------------------------------------------------------
    def get_cond_and_subj_number_ftp(self, host="", username="", password="", filename=""):
        """
        Similar functionallity to ``get_cond_and_subj_number``. Reads data
        from a remote ftp client in order to set up participant numbers and
        conditions. The host, username, and password can be set during the
        initialization of the ``Experiment`` object.
        
        Kwargs:
         * ``host`` (str): web address of file hosting site
         * ``username`` (str): account name on the host site
         * ``password`` (str): password for the account 
         * ``filename`` (str): name of patterncode file, defaults to
           ``patterncode.txt``
        
        Returns:
            A list containing the lines in the file, converted to ints.
        """
        
        if not host:
            host = self.ftphost
        if not username:
            username = self.ftpuser
        if not password:
            password = self.ftppassword
        if not filename:
            filename = self.patterncode
        
        try: 
            ftp = FTP(host, username, password) # connect to ftp host
        except Exception, message:
            # TODO figure out what exception this raises.
            if not password:
                passmessage = "None given."
            else:
                passmessage = "Omitted."
            errormsg = """
            ERROR: Failed to connect to ftp host.
                host: %s
                username: %s
                password: %s
            """ % ( host, username, passmessage )
            warn( errormsg )
            raise SystemExit, message
        lines = []
        ftp.retrlines('RETR ' + filename, lines.append) # get lines
        
        outlines = self.read_patterncode_lines( lines )
        myfile = tempfile.TemporaryFile()
        myfile.writelines(outlines)
        myfile.seek(0) # rewind to the beginning of the file
        ftp.storlines('STOR ' + filename, myfile)
        myfile.close() # close deletes the tmpfile
        return map( int, lines )
    
    def read_patterncode_lines(self, lines):
        """
        Reads lines taken from a patterncode file.
        File should consists of 3 lines, as follows:
         1. Condition current subject will be in 
         2. Number of conditions
         3. Current subject number (automatically updated)
        Writes values to ``self.cond``, ``self.ncond``, and ``self.subj``.
        Returns the new lines to be written back to the file.
        
        Args:
         * ``lines`` (list of strs): Lines read in from patterncode file.
        
        Returns:
            A list of the strings' new lines.
        """
        outlines = numbers = [ int( line ) for line in lines ]
        
        # Writing new values.
        self.cond = numbers[0]
        self.ncond = numbers[1]
        self.subj = numbers[2]
        
        # Incrementing the values in the outfile.
        outlines[0] = (outlines[0]+1) % outlines[1]
        outlines[2] += 1
        outlines = [ str( line ) + os.linesep for line in outlines ]
        
        return outlines
    
    #------------------------------------------------------------
    # output_trial
    #------------------------------------------------------------
    def output_trial(self, myline, echo=False):
        """ 
        Writes a list of data to a file as a line in which each value seperated
        by a space. 
        
        Args:
         * ``myline`` (iterable): Iterable of items to be written to the line
        
        Kwargs:
         * ``echo`` (bool): If ``True``, prints the line to the screen.
        """   
        myline = ' '.join( map(str, myline) )
        if self.verbose or echo:
            print myline
        self.datafile.write(myline)
        
        self.datafile.write('\n')
        self.datafile.flush()
    
    #------------------------------------------------------------
    # upload_data
    #------------------------------------------------------------
    def upload_data(self, host="", username="", password="", filename="", netfilename=""):
        """
        Uploads data to a file storage site.  FTP credentials can be set during
        the initialization of the ``Experiment`` object.

        Kwargs:
         * ``host`` (str): Hostname of ftp server.
         * ``username`` (str): Username on server.
         * ``password`` (str): Password to server.
         * ``filename`` (str): Local file that will be uploaded. Defaults to
           ``self.filename``.
         * ``netfilename`` (str): Name of file to be written to server.
           Defaults to ``filename``.
        """
        if not host:
            host = self.ftphost
        if not username:
            username = self.ftpuser
        if not password:
            password = self.ftppassword
        if not filename:
            filename = self.filename
        if not netfilename:
            filename = filename
        
        myfile = open(filename)
        try:
            ftp = FTP(host, username, password) # connect to ftp host
            ftp.storlines('STOR ' + netfilename, myfile)
        except Exception, msg:
            # TODO: figure out what exception this raises.
            errormsg = """
            ERROR: connectivity error while uploading to FTP.
            """
            warn( errormsg )
            self.on_exit(msg=msg)
        myfile.close() # close
    
    #------------------------------------------------------------
    # tick
    #------------------------------------------------------------
    def tick( self ):
        """
        Waits until a given time based on ``self.framerate``. Useful while in a
        loop, to limit the rate at which it loops.
        """
        if not self.suppresspygame:
            self.clock.tick( self.framerate )
    
    #------------------------------------------------------------
    # update_display
    #------------------------------------------------------------
    def update_display(self, mysurf=None):
        """
        Blits the surface passed to the default display screen created by 
        the experiment class. Then flips it. 

        Kwargs:
         * ``mysurf`` (``pygame.surface``): The surface to be written to the
           screen.
        """
        if not mysurf:
            mysurf = self.background
        self.screen.blit(mysurf, (0,0))
        pygame.display.flip()
    
    #------------------------------------------------------------
    # place_text_image
    #------------------------------------------------------------
    def place_text_image(self, mysurf=None, prompt="", size=None, xoff=0, yoff=0, txtcolor=None, bgcolor=None, font=None, fontname=None ):
        """
        Blits a Text object to the surface passed.

        Kwargs:
         * ``mysurf`` (``pygame.surface``): Surface object to be blitted to.
         * ``prompt`` (str): String to be displayed
         * ``size`` (int): text size
         * ``xoff`` (int): Horizontal offset from center.
         * ``yoff`` (int): Vertical offset from center.
         * ``txtcolor`` (str or tuple): Color of the test (name or RGB).
         * ``bgcolor`` (str or tuple): Color of the background (name or RGB).
         * ``font`` (``pygame.font``): Font object to use for text rendering.
         * ``fontname`` (str): Name of font to use.
        
        Returns:
            A pygame surface object with the text placed on it.
        """
        # Legacy arg order:
        # mysurf, prompt, size, xoff, yoff, txtcolor, bgcolor
        if not mysurf:
            mysurf = self.background
        if not fontname:
            fontface = self.fontname
        if not size:
            size = self.fontsize
        thisfont = pygame.font.SysFont( fontface, size )
        if not txtcolor:
            txtcolor = self.fgcolor
        else:
            txtcolor = pgColor( txtcolor )
        if not bgcolor:
            bgcolor = self.bgcolor
        else:
            bgcolor = pgColor( bgcolor )
        text = self.get_text_image(font=thisfont, message=prompt, fgcolor=txtcolor, bgcolor=bgcolor)
        textpos = self.placing_rect(mysurf, text, xoff, yoff)
        mysurf.blit(text, textpos)
        return mysurf
    
    #------------------------------------------------------------
    # get_text_image
    #------------------------------------------------------------
    def get_text_image(self, font=None, message="", fgcolor=None, bgcolor=None):
        """ 
        Creates a Surface with anti-aliased text written on it, and returns it.
        
        Kwargs:
         * ``font`` (``pygame.font``): The font to use for the text.
         * ``message`` (str): String to be displayed
         * ``fontcolor`` (str or tuple): Color for text (RGB or name)
         * ``bgcolor`` (str or tuple): Color for the background (RGB or name)
        
        Returns:
            The surface with text written to it.
        """
        if not font:
            font = self.font
        if not fgcolor:
            fgcolor = self.fgcolor
        else:
            fgcolor = pgColor( fgcolor )
        if not bgcolor:
            bgcolor = self.bgcolor
        else:
            bgcolor = pgColor( bgcolor )
        base = font.render(message, 1, fgcolor, bgcolor)
        size = base.get_width(), base.get_height()
        img = pygame.Surface(size, 16)
        img = img.convert()
        img.blit(base, (0, 0))
        return img
    
    #------------------------------------------------------------
    # placing_text
    #------------------------------------------------------------
    def placing_rect(self, bkgd_surf=None, inner_surf=None, xoff=0, yoff=0):
        """ 
        Creates a Rect from Surface ``inner_surf`` and places it onto
        Surface ``bkgd_surf``.
        
        Kwargs:
         * ``bkgd_surf`` (``pygame.surface``): Surface to write to.
         * ``inner_surf`` (``pygame.surface``): Surface to write to the other
           surface.
         * ``xoff`` (int): Horizontal offset from center.
         * ``yoff`` (int): Vertical offset from center.
        
        Returns:
            The surface created.
        """
        if not bkgd_surf:
            bkgd_surf = self.background
        if not inner_surf:
            raise Exception, "ERROR: placing_rect requires an 'inner_surf' argument."
        rect = inner_surf.get_rect()
        rect.centerx = bkgd_surf.get_rect().centerx + xoff
        rect.centery = bkgd_surf.get_rect().centery + yoff
        return rect
        
    #------------------------------------------------------------
    # play_sound
    #------------------------------------------------------------
    # Do we want it to return the "play time"? - yes
    def play_sound(self, sndname, pause=0):
        """
        Plays a sound file for its length plus and length 'pause' in
        milliseconds. This function works with .wav files only. It pauses
        the timer.
        
        Args:
         * ``sndname`` (str): The sound name (omit the .wav extension)
        
        Kwargs:
         * ``pause`` (int): Time in milliseconds to pause the pygame timer
        
        Returns:
            The sound duration plus pause.
        """
        # TODO: What does "it pauses the timer" mean?
        filelen = int(self.resources[sndname].get_length()*1000)
        time_stamp = pygame.time.get_ticks()
        self.resources[sndname].play()
        pygame.time.wait( filelen )
        rt = pygame.time.get_ticks() - time_stamp
        if self.verbose:
            # TODO: What is going on here? What is this supposed to mean?
            print "PLAY TIME  =", rt - filelen
        return rt
    
    #------------------------------------------------------------
    # show_centered_image
    #------------------------------------------------------------
    def show_centered_image(self, imagename, bgcolor=None, alpha=None):
        """
        Centers an image in the screen with a given bgcolor.
        
        Args: 
         * ``imagename`` (str): Name of image.
        
        Kwargs:
         * ``bgcolor`` (str or tuple): Background color (name or RGB)
        
        Returns:
            A surface with the image blitted over a field of ``bgcolor``.
        """
        if not bgcolor:
            bgcolor = self.bgcolor
        else:
            bgcolor = pgColor( bgcolor )
        return self.show_image(imagename, bgcolor=bgcolor, xoffset=0, yoffset=0, alpha=alpha)
    
    #------------------------------------------------------------
    # show_image (for backward compatiblilty)
    #------------------------------------------------------------
    def show_image(self, imagename, bgcolor=None, xoff=0, yoff=0, alpha=None):
        """ 
        Creates a surface object with the dimensions of the display screen.
        Then blits an image to the center of the surface plus any offseting
        height/width. The surface is then returned. 
        
        .. NOTE ::
            This *creates* a Surface object, whereas show_image_add is passed a
            surface to be blitted on.
        
        Args: 
         * ``imagename`` (str): Name of image (must be in ``self.resources``).
        
        Kwargs:
         * ``bgcolor`` (str or tuple): Background color (name or RGB)
         * ``xoff`` (int): Horizontal offset from center.
         * ``yoff`` (int): Vertical offset from center.
         * ``alpha`` (float): Amount of opacity. Defaults to fully opaque.
        
        Returns:
            A surface with the image blitted over a field of ``bgcolor``.
        """
        if not bgcolor:
            bgcolor = self.bgcolor
        else:
            bgcolor = pgColor( bgcolor )
        size = self.screen.get_size()
        outsurf = pygame.Surface(size)
        outsurf = outsurf.convert()
        outsurf.fill(bgcolor)
        
        image = self.resources[imagename]
        image_rect = image.get_rect()
        if alpha != None:
            image.set_alpha(alpha)
        image_rect.centerx = outsurf.get_rect().centerx + xoff
        image_rect.centery = outsurf.get_rect().centery + yoff
        
        outsurf.blit(image,image_rect)
        return outsurf
    
    #------------------------------------------------------------
    # show_centered_image_add
    #------------------------------------------------------------
    def show_centered_image_add(self, mysurf=None, imagename=None, alpha=None):
        """
        Centers an image in the surface passed. Default surface is
        ``self.background``.
        
        .. NOTE::
            This REQUIRES a Surface object to be passed, whereas show_image
            creates a Surface to be blitted on  
        
        Kwargs:
         * ``mysurf`` (``pygame.surface``): Surface to blit to. Defaults to ``self.background``
         * ``imagename`` (str): Mandatory. Name of image (must be in
           ``self.resources``).
         * ``xoff`` (int): Horizontal offset from center.
         * ``yoff`` (int): Vertical offset from center.
         * ``alpha`` (float): Amount of opacity. Defaults to fully opaque.
        
        Returns:
            A surface with the image added.
        """
        if not imagename:
            raise Exception, "No image name passed to show_centered_image_add."
        if not mysurf:
            mysurf = self.background
        return self.show_image_add(mysurf, imagename, 0, 0, alpha)     
    
    #------------------------------------------------------------
    # show_image_add
    #------------------------------------------------------------
    def show_image_add(self, mysurf=None, imagename=None, xoffset=0, yoffset=0, alpha=None):
        """ 
        Places an image onto a passed Surface with given offsets relative to
        the center of the Surface. Returns the drawn-on Surface.
        
        mysurf - Surface to be blitted to imagename - name of the image file
        loaded by load_image (or load_all_images) xoffset/offset - offsets
        relative to the center of the Surface alpha - alpha value of the image
        
        .. NOTE::
            This REQUIRES a Surface object to be passed, whereas show_image
            creates a Surface to be blitted on  
        """
        if not imagename:
            raise Exception, "No image name passed to show_image_add."
        if not mysurf:
            mysurf = self.background
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
    def clear_screen(self, color=None):
        """ 
        Creates a Surface with the dimensions of the display screen, fills
        it with a given color, and returns the Surface.  
        
        Kwargs:
         * ``color`` (str of tuple): Color to draw on screen (name or rgb).
           Defaults to ``self.bgcolor``.
        """
        if not color:
            color = self.bgcolor
        else:
            color = pgColor( color )
        size = self.screen.get_size()
        background = pygame.Surface(size)
        background = background.convert()
        background.fill(color)
        return background    
    
    #------------------------------------------------------------
    # get_response_and_rt_pq
    #------------------------------------------------------------
    def get_response_and_rt_pq(self, val=None):
        """ 
        Monitors keyboard Events for the ``Q`` and ``P`` keys. Returns the time
        it took from the call to the function to the end of the function
        (reaction time; rt) and the response made (res). 
        
        Kwargs:
         * ``val`` (list or tuple) with coded values, e.g. ``['Left',
           'Right']`` or ``(0, 1)``
        
        Returns:
            A list with reaction time and the value code for the response made.
        """
        return self.get_response_and_rt( val=val, keys=['p','q'] )
    
    def get_response_and_rt(self, keys=['p','q'], val=None):
        """ 
        Monitors keyboard Events for the given set of keys (default ``Q`` and
        'P'). Case insensitive. Returns the time it took from the call to the
        function to the end of the function (reaction time; rt) and the coded
        version of the response (given in 'val'). 
        
        Kwargs:
         * ``keys`` (list or tuple of strings) where the keys are the names of
           the keys that will be pressed. Defaults to ``[q, p]``. Keypad
           numbers == keyboard numbers (although this could change) For a full
           list of valid key names, see the libSDL source, under
           ``$SDLroot/src/SDL_keyboard.c``.
         * ``val`` (list or tuple) with coded values, e.g. ``['Left',
           'Right']`` or ``(0, 1)``. Defaults to be the same as ``keys``.
        
        Returns:
            A list with reaction time and the value code for the response made.
        """
        if not val:
            val = keys
        time_stamp = pygame.time.get_ticks()
        while 1:
            self.tick()
            res = self.get_response()
            for i, r in enumerate( val ):
                if res == r:
                    return val[i]
    
    
    #------------------------------------------------------------
    # get_response ... decapitalizes capitals.
    #------------------------------------------------------------
    def get_response(self):
        """
        Waits for a key to be pressed, then Returns the key mapping for a
        single pressed letter, ignoring modifier keys. Actual key mappings are
        found in libSDL source, in: ``$SDLROOT/src/SDL_keyboard.c``.
        """
        pygame.event.clear()
        while 1:
            self.tick()
            self.check_for_exit()
            event = pygame.event.poll()
            if event.type == pglc.KEYDOWN:
                resp = pygame.key.name(event.key)
                if resp[0] == "[" and resp[-1]=="]": # this is how keypad keys are coded.
                    resp = resp[1:-1]
                return resp 
    
    #------------------------------------------------------------
    # check_for_exit
    #------------------------------------------------------------
    def check_for_exit(self):
        """
        Checks for the exit sequence: left shift plus ~.
        Overload this function to use a different exit keystroke.
        """
        if pygame.key.get_pressed()[pglc.K_LSHIFT] and pygame.key.get_pressed()[pglc.K_BACKQUOTE]:
            self.on_exit()
    
    #------------------------------------------------------------
    # prompt_text
    #------------------------------------------------------------
    def prompt_text(self, background=None, x=0, y=0, timelimit = None, prompt = '', fontsize = None, maxlength = 40, fgcolor=None, centered = False):
        """
        Makes an onscreen prompt for users to enter a single line of text.
        
        Kwargs: 
         * ``background`` (``pygame.surface``): the surface that will be
           refreshed; defaults to ``self.background``.
         * ``x`` (int): The horizontal coordinate, determining the left side of
           the prompt, or the center if ``centered`` is ``True``.
         * ``y`` (int): The vertical coordinate, determining the top of
           the prompt, or the center if ``centered`` is ``True``.
         * ``timelimit`` (int): (in milliseconds). Default is ``None``.
         * ``prompt`` (str): To be printed in front of the typed text. Default
           is a null string.
         * ``fontsize`` (int): Size of text printed on screen. Default is
           ``32``.
         * ``maxlength`` (int): Maximum number of characters allowed to be
           typed.  Default is ``40``. ``0`` means unlimited.
         * ``fgcolor`` (str or tuple): Color of text; name or rgb tuple.
           Default is ``self.fgcolor``
         * ``centered`` (bool): Maintain a centered alignment. ``x`` and ``y``
           become offset of center if ``True``. Default is ``False``.
        
        Returns:
            The typed text as it appeared on the screen.
        
        Possible future options:
            Restrictions on possible characters.
            Control over typeface.
        """
        if not background:
            background = self.background
        if not fgcolor:
            fgcolor = self.fgcolor
        else:
            fgcolor = pgColor( fgcolor )
        if fontsize:
            font = pygame.font.SysFont( self.fontname, fontsize ) 
        else:
            font = self.font
        pygame.event.clear()
        txtbx = TextPrompt(self.screen, background, maxlength=maxlength,
                           fgcolor=fgcolor, x=x, y=y, prompt = '', font = font)
        
        return txtbx.get_text_line(centered=centered, timelimit=timelimit)
    
    #------------------------------------------------------------
    # escapable_sleep
    #------------------------------------------------------------
    def escapable_sleep(self, pause=1000, esckey = None):
        """ 
        Pauses the program for 'pause'-number of milliseconds. Can be exited
        via the default keystroke in``check_for_exit``.
        
        Kwargs:
         * ``pause`` (int): (in milliseconds) Amount of time to sleep for.
         * ``esckey`` (int; from ``pygame.locals``): A key that, if pressed,
           will end the pause.
        """
        waittime = 0    
        time_stamp = pygame.time.get_ticks()
        while waittime < pause:
            self.tick()
            self.check_for_exit()
            pygame.event.clear()
            if esckey != None:
                if pygame.key.get_pressed()[esckey]:
                    break
            waittime = pygame.time.get_ticks() - time_stamp
    
    def draw_square(self, surf=None, color=None, x=0, y=0, width=10, height=10, thick=0):
        """ 
        Draws a square of the size and coordinates requested to the background,
        and returns the result.
        
        Kwargs:
         * ``surf`` (``pygame.surface``): Surface to draw to. Defaults to
           ``self.background``.
         * ``color`` (str of tuple): Color of rectangle (name or rgb).
         * ``x`` (int): The coordinate of the left side of the rectangle.
         * ``y`` (int): The coordinate of the top of the rectangle.
         * ``width`` (int): The width of the rectangle. Defaults to ``10``.
         * ``height`` (int): The height of the rectangle. Defaults to ``10``.
         * ``thick`` (int): The thickness of the rectangle border. If thick is
           ``0`` (the default), the rectangle is filled and has no border.
           Otherwise it is not filled.
        """
        if not surf:
            surf = self.background
        color = pgColor( color )
        pygame.draw.rect(surf, color, (x,y,width,height), thick)
        return surf
    
    def draw_on_screen_example( self, background=None, color=None, break_key=pglc.K_SPACE, radius=3 ):
        """
        This is an example of how to allow participants to draw on the screen
        with a mouse. They can draw by clicking and dragging the mouse.
        Pressing the break_key exits the drawing environment.
        
        Kwargs:
         * background (``pygame.surface``): The surface to draw to. Defaults to
           ``self.background``.
         * ``color`` (str or tuple): The maker color. Defaults to
           ``self.fgcolor``.
         * ``break_key`` (int (from ``pygame.locals``): Pressing this key
           terminates drawing.
         * ``radius`` (int): The radius of the drawing brush.
        """
        if not background:
            background = self.background
        if not color:
            color = self.fgcolor
        else:
            color = pgColor( color )
        has_drawn = False
        done = False
        last_pos = None
        timestamp = pygame.time.get_ticks()
        is_pressed = pygame.mouse.get_pressed()[0]
        defaultcursor = pygame.mouse.get_cursor()
        oldbackground = background.copy()
        pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))
        while not done:
            self.check_for_exit()
            for event in pygame.event.get():
                if not pygame.mouse.get_pressed()[0]:
                    is_pressed = False
                if has_drawn and event.type == KEYUP and event.key==break_key :
                    done = True
                    rt = pygame.time.get_ticks() - timestamp
                    break
                elif pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if is_pressed and last_pos:
                        pygame.draw.line( background, color, last_pos, pos, radius )
                    else:
                        pygame.draw.circle( background, color, pos, radius )
                    self.update_display( background )
                    has_drawn = True
                    last_pos = pos
                    is_pressed = True
                    
                #elif (event.type == MOUSEMOTION and event.buttons[0]) or (event.type == MOUSEBUTTONDOWN):
                #    pygame.draw.circle( background, color, event.pos, radius )
                #    self.update_display(background)
                #    has_drawn = True
        pygame.mouse.set_cursor( *defaultcursor )
        self.update_display( oldbackground )
        return 0, rt
    
    #------------------------------------------------------------
    # setup_gabor
    #------------------------------------------------------------
    def setup_gabor(self, grid_w, grid_h, windowsd):
        """ 
        This is a demo for using gabor patches. Call setup_gabor to set initial
        values for the gabor patch, then draw_gabor to actually draw it to a
        surface. They are thin wrappers to the GaborPatch class.
        
        Arguments:
         * ``grid_w`` (int): width
         * ``grid_h`` (int): height 
         * ``windowsd`` (float): standard deviation  
        """
        self.gabor = GaborPatch( grid_w, grid_h, windowsd )
    
    #------------------------------------------------------------
    # draw_gabor
    #------------------------------------------------------------
    def draw_gabor(self, freq, angle, scale):
        """ 
        This is a demo for using gabor patches. Call setup_gabor to set initial
        values for the gabor patch, then draw_gabor to actually draw it to a
        surface. They are thin wrappers to the GaborPatch class.
        
        Draws the gabor patch set by 'setup_gabor' 
        
        Args:
         * ``freq`` (int): the frequency of the gabor patch
         * ``angle`` (int): value to determine rotation on the patch. WARNING:
           units are degrees/2
         * ``scale`` (int) - enlarges the gabor patch by a given factor
        
        .. WARNING::
            Due to a bug in ``pygame``, ``angle`` is in units of degrees/2.
        
        .. NOTE::
            For faster blitting it is recommended to set the ``grid_w`` and
            ``grid_h`` in ``setup_gabor`` to be smaller than the actual patch
            desired. To offset this, use the scale value to blow up the image. 
            
            Due to the nature of rotating a surface, the size of the surface the
            gabor patch changes based on the value of the rotation angle. This
            function re-centers the patch after each rotation, but it should be
            noted as it will make the area of the surface larger. 
        """
        return self.gabor.draw_gabor( freq, angle, scale )
    
    #------------------------------------------------------------
    # on_exit
    #------------------------------------------------------------
    def on_exit(self, msg=""):
        """ 
        Clears all data that remains on queue and closes ``self.datafile``.
        
        Kwargs:
         * msg (str): Exit message.
        """
        self.datafile.flush()
        self.datafile.close()
        exit()
        raise SystemExit, msg

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

#------------------------------------------------------------
# MouseButton Class
# Creates a Rect object on initialization. Supports for 
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
# GaborPatch Class
# Creates a GaborPatch object, which is drawn by calling draw_gabor.
#------------------------------------------------------------
class GaborPatch:
    def __init__(self, grid_w=10, grid_h=10, windowsd=1):
        """ 
        Sets up initial values for a gabor patch and its gaussian blur.
        
        Arguments:
         * grid_w (int): width
         * grid_h (int): height 
         * windowsd (float): standard deviation  
        """
        # TODO: Gabors should also in principle have equal luminance.
        self.w = grid_w
        self.h = grid_h
        self.windowsd = windowsd
        self.centerx= self.w/2
        self.centery = self.h/2        
        normalization=self.bivariate_normpdf(self.centerx,self.centery,self.windowsd,self.windowsd,self.centerx,self.centery,1.0)
        self.window = np.array([[ [self.bivariate_normpdf(i,j,self.windowsd,self.windowsd,self.centerx,self.centery,1.0)/normalization]*3 for j in range(self.w)] for i in range(self.h)],na.Float64)
    
    #------------------------------------------------------------
    # draw_gabor
    #------------------------------------------------------------
    def draw_gabor(self, freq, angle, scale):
        """ 
        This is a demo for using gabor patches. Call setup_gabor to set initial
        values for the gabor patch, then draw_gabor to actually draw it to a
        surface. They are thin wrappers to the GaborPatch class.
        
        Draws the gabor patch set by 'setup_gabor' 
        
        Args:
         * ``freq`` (int): the frequency of the gabor patch
         * ``angle`` (int): value to determine rotation on the patch. WARNING:
           units are degrees/2
         * ``scale``(int) - enlarges the gabor patch by a given factor
        
        .. WARNING::
            Due to a bug in ``pygame``, ``angle`` is in units of degrees/2.
     
        .. NOTE::
            For faster blitting it is recommended to set the grid_w and grid_h
            in 'setup_gabor' to be smaller than the actual patch desired. To
            offset this, use the scale value to blow up the image. 
            
            Due to the nature of rotating a surface, the size of the surface the
            gabor patch changes based on the value of the rotation angle. This
            function re-centers the patch after each rotation, but it should be
            noted as it will make the area of the surface larger. 
        """
            
            
        surface = pygame.Surface([self.w,self.h], SRCALPHA)
        surface.fill(white)
        
        pixarray = pygame.surfarray.pixels3d(surface)
        pixrgb = np.array(pixarray)
        pixrgb[:,:,:]=0
        sinewavematrix = np.array([[ [((sin(degrees(j)/freq)+1)/2) * 255.0]
                                    for j in range(self.w)]] * self.h) 
        # (to run faster, only compute the sine wave once)
        finalimg = self.window * sinewavematrix
        finalimg = [[array('I', item) for item in line] for line in
                    finalimg.tolist()]
        pixarray[:] = finalimg[:]
        # rotate
        surface.unlock()
        surface = pygame.transform.rotozoom(surface, angle, scale)
        # adjusts for the increase in size do to rotation
        rect = surface.get_rect()
        surf = pygame.Surface([rect.w, rect.h])
        surf_rect = surf.get_rect()
        surf.blit(surface, surf_rect) # returns a larger surface
        return surf
    
    #------------------------------------------------------------
    # bivariate_normpdf
    #------------------------------------------------------------   
    def bivariate_normpdf(self, x, y, sigma_x, sigma_y, mu_x, mu_y, mul):
        """ 
        Formula used to set the gaussion blur 
        x,y - current position in the grid
        sigma_x/y - variance in each plane of the grid
        mu_x/y - mean
        mul - scales by this amplitude factor 
        """ 
        return mul / (2.0*pi*sigma_x*sigma_y) * exp(-1.0/2.0*((x-mu_x)**2.0/sigma_x**2.0 + (y-mu_y)**2/sigma_y**2.0)) 

class TextPrompt:
    """
    A text input prompt. Allows the on-screen editing of a single line of text.
    """
    def __init__(self, screen, background, **useroptions):
        """
        TextPrompt accepts the following keyword arguments when it starts up:
            x, y, font, fgcolor, restricted, maxlength, prompt. 
        """
        
        defaults = dict(
            x= 0, 
            y= 0, 
            font= pygame.font.Font(None, 32),
            fgcolor= (0,0,0), 
            restricted= '\'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\\\'()*+,-./:;<=>?@[\]^_`{|}~\'',
            maxlength= -1, 
            prompt= '' 
        )
        
        self.options = defaults
        defaults.update( useroptions )
        
        self.background = background
        self.screen = screen
        self.x = self.options['x']
        self.y = self.options['y']
        self.font = self.options['font']
        self.fgcolor = pgColor( self.options['fgcolor'] )
        self.restricted = self.options['restricted']
        self.maxlength = self.options['maxlength']
        self.prompt = self.options['prompt']; 
        self._value = ''
        self.shifted = False
        
        # This could be made an option but it's probably not necessary:
        pygame.key.set_repeat( 600, 150 )
        
    
    def center(self, offset = 0):
        self.x = self.background.get_rect().centerx + offset - (self.font.render(self.prompt+self._value, 1, self.fgcolor).get_width()/2)
    
    def set_pos(self, x, y):
        """ Set the position to x, y """
        self.x = x
        self.y = y
    
    def set_font(self, font):
        """ Set the font for the input """
        self.font = font
    
    def draw(self):
        """ Draw the text input to the screen """
        text = self.font.render(self.prompt+self._value, 1, self.fgcolor)
        self.screen.blit(text, (self.x, self.y))
    
    def update(self, events):
        """
        Update the input based on a list of events passed in.
        Returns true if enter is pressed.
        """
        # key.name doesn't know about shifting. Manual fix:
        conversion = dict( zip( "`1234567890-=[]\;',./", '~!@#$%^&*()_+{}|:"<>?' ) )
        for event in events:
            if event.type == pglc.KEYDOWN:
                if event.key == pglc.K_LSHIFT or event.key == pglc.K_RSHIFT:
                    self.shifted = True
                    continue
                if event.key == pglc.K_RETURN:
                    return True
                if event.key == pglc.K_BACKSPACE: 
                    self._value = self._value[:-1]
                    continue
                if event.key == pglc.K_SPACE:
                    self._value += ' '
                    continue
                #modsraw = event.key.get_mods()
                keydown = pygame.key.name( event.key )
                if self.shifted:
                    if keydown in conversion.keys():
                        keydown = conversion[ keydown ]
                    else:
                        keydown = keydown.upper()
                if keydown in self.restricted:
                    self._value += keydown
            elif event.type == pglc.KEYUP:
                if event.key == pglc.K_LSHIFT or event.key == pglc.K_RSHIFT:
                    self.shifted = False
        if self.maxlength >= 0:
            self._value = self._value[:self.maxlength]
        return False
    
    def get_text_line(self, centered=False, timelimit=None):
        """
        Prompts the user for a line of text, updating it as they type.
        
        The escape sequence here is to press both shift keys and tilde (this is
        to prevent subjects from accidentally quitting the experiment using
        tilde).
        """
        # create the pygame clock
        clock = pygame.time.Clock()
        timestamp = pygame.time.get_ticks()
        while 1:
            # have the program is running at 40 fps
            clock.tick(40)
            
            # events for self
            events = pygame.event.get()
            # process other events
            if timelimit and pygame.time.get_ticks()-timestamp > timelimit:
                break
            if self._value and pygame.key.get_pressed()[pglc.K_RETURN]:
                break
            if pygame.key.get_pressed()[pglc.K_LSHIFT] and pygame.key.get_pressed()[pglc.K_RSHIFT] and pygame.key.get_pressed()[pglc.K_BACKQUOTE]:
                raise SystemExit, "Quit sequence pressed."
            
            # clear the screen
            self.screen.blit(self.background, (0,0))
            
            # update self
            self.update(events)
            
            # blit self on the sceen
            if centered:
                self.center(offset = self.x)
            self.draw()
            # refresh the display
            pygame.display.flip()
        return self._value

def main():
    pass

if __name__ == '__main__':
    main()

