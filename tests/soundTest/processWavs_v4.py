####################################################################
#   To do:
#   1) Nothing
#
####################################################################

#import pygame
from pygame.locals import *
from time import *
from lib.pypsyexp import *
from numpy import *
from wave import open as W
import struct
import sys

laptop = True
experimentname = 'Proccess Wavs'
LAPTOP = ( 1024, 768 )
FULLSCREEN = (1024, 768 )

if laptop: screenres = LAPTOP
else: screenres = FULLSCREEN

class Processor():
    
    def __init__(self, laptop, screenres, experimentname):
        #pygame.init()
        self.laptop = laptop
        for arg in sys.argv:
        	print arg
        
    def do_exp(self):
        sample_window = 500
        #print "reading audio file"
        splits, runtime, length = self.readwav('sounds/s_525.wav') # splits is a numpy array
        audio = splits[0].reshape(1,length)[0]
        #print "finished reading audio file"
        pc_data = self.read_data('data/s_525.dat')
        #print "finished reading subject data file"
        self.cond = pc_data[0][6]
        
        [absolute_l, relative_l, indexes_l, audio_l, windows_l] = self.histog(audio, length, sample_window)
        #print absolute_l, relative_l
        l_list = self.parsewav(audio_l, length, absolute_l, relative_l, sample_window, windows_l) # beeps from computer
        self.start = l_list[0] # every running of the experiment starts with a click noise to signal the start       
        l_list = l_list[1:] # takes out the start click out of analysis
        r_list = l_list = self.add_data(l_list)
        wavs = self.analyze(pc_data, l_list)
        wavs =  self.clean(pc_data, r_list, wavs)
        
        for i in wavs:
        	print i
    
    def read_data(self, filename):
        a = []
        dat = open(filename, "rb")
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
        data = array(struct.unpack("%sh" %length*nchannel, frames), dtype=float).reshape(length,nchannel)
        splits = hsplit(abs(data), nchannel) # splits into left and right channels
        return splits, runtime, length  
        
    def histog(self, audio, length, window):
        absolute = relative = 0.0
        place_holder = window # need window again after some subtraction
        #[values, bins] = histogram(audio, bins=(audio.max()-audio.min()),normed=True) # numpy
        absolute = 3000 #where( cumsum(values) >= .9995)[0][0]
        
        start=sum(audio[0:window])
        offsets=append(start, array(audio[window:])-array(audio[:-window]))
        windows=cumsum(offsets)
        
        relative = max(windows)-10000
        
        return [absolute, relative, range(len(audio)-window+1), audio[:-window+1], windows]    
    
    def parsewav(self, audio, length, absolute, relative, sample_window, windows_l): # gets sound points
        
        f= d = greater( audio, absolute ) #list of True/False based on whether indiv. samples are greater than absolute

        g = array(where( f == True )[0]) # array where both absolute and relative are true
        start = last=g[0]
        res=[start]
        for item in g[1:]:
            if item-last>500:
                res.append(item)
            last=item
        
        #print res[:10]
        #vals=array(append(0,res))
        ms = array(res)/44100.0

        #print ms
        return ms
        
    def analyze(self, pc_data, l_channel):
        # pc_data = [  [trial, time since start, time since last click/press, RT, wait_time, response, cond], .. [], [] ]
        # l_channel =  [ [time(ms), time since start(ms), time since last ], ... [], [] ]
        new_array = []
        choice = pc_data
        if len(pc_data) <= len(l_channel):
            choice = pc_data
        else:
            choice = l_channel
        
        for i in range(len(choice)):
            #new_array.append( [ pc_data[i][0], pc_data[i][1], (l_channel[i][1]*1000), ( float(pc_data[i][1]) - (l_channel[i][1]*1000) ), pc_data[i][2], l_channel[i][2], (float(pc_data[i][2])-l_channel[i][2]), l_channel[i][0], pc_data[i][6] ] )
        	new_array.append( [ int(pc_data[i][0]), int(pc_data[i][1]), (l_channel[i][1]*1000), ( float(pc_data[i][1]) - float(l_channel[i][1]*1000) ), int(pc_data[i][2]), l_channel[i][2], (float(pc_data[i][2])-l_channel[i][2]), l_channel[i][0], 0 ] )
        
        return new_array
        
    def add_data(self, l_channel):
    	if type(l_channel) != list:
	    	l_channel = l_channel.tolist()
        res = []
        previous = self.start
        for i in range(len(l_channel)): # i here are lists
            time_since_last = l_channel[i] - previous
            res.append([l_channel[i], l_channel[i] - self.start,(time_since_last*1000) ])
            previous = l_channel[i]
        return res
    
    def clean( self, pc_data, r_list, wavs ):

    	#it will be probable for r_list to contain more/less points than PC data
    	# this will make them equal 	    	
    	if len(pc_data) < len( r_list):
    		dif = abs(len(pc_data) - len( r_list))
    		for i in range(dif):
    			pc_data.append( ['000', 9999999, 9999999, 9999999, 9999999, 'N/A', 'N/A'])    			
    	elif len(pc_data) > len( r_list):
    		dif = abs(len(pc_data) - len( r_list))
    		for j in range(dif):
    			r_list.append( [9999999, 9999999, 9999999] )
    			
    	#for i in range(len(pc_data)):
    	#	print pc_data[i], r_list[i]
    	
    	length = len(pc_data)	
    	start = r_list[0][1]
    	for k in range(1,length): #removes noise
    		if r_list[k][1] < (start + .5):		
    			r_list.pop(r_list.index(r_list[k]))
    			r_list.append( [99999999, 99999999, 99999999] ) #to keep the list the same len()
    		
    		start = r_list[k][1]
    	
    	#for i in range(len(pc_data)):
    	#	print pc_data[i], r_list[i]
    	
    	#this uses time since last
    	#for m in range(length):
    	#	if int(pc_data[m][2]) > (r_list[m][2]+500): # point doesnt exist
    	#		r_list.pop(r_list.index(m))
    	#		r_list.append( [9999999,9999999,9999999] )
    	#	elif int(pc_data[m][2])+500 < r_list[m][2]: # means point is missing 
    	#		r_list.insert( m, [99999999, 99999999,99999999] )
    	#		r_list.pop() # removes a hanging 9999999
    	
    	# alternatively use the difference since start, must be within 200ms of the previous difference
    	# works as long as the first point is picked up    		
    	#for m in range(length):
    	#	if abs(int(pc_data[m][2]) - int(r_list[m][2]) ) > 200:
    	#		r_list.insert( m, [99999999, 99999999,99999999] )
    	#		r_list.pop() # removes a hanging 9999999
    			
    	#for m in range(length): #denotes places where points are dropped
    	#	if abs(int(pc_data[m][1])-int(r_list[m][1]*1000)) > 500: # missed if there is a set interval
    	#		r_list.insert( m, [99999999, 99999999,99999999] )
    	#		r_list.pop() # removes a hanging 9999999
    	
    	#new_list = []
    	#for n in range(len(r_list)):
    	#	new_list.append(r_list[n][0])
    				
    	return self.analyze( pc_data, r_list )
    	    
    # Have to make sure that this can get everything if points are removed... ie. go back for them.    
    #def clean( self,pc_data, r_list, wavs ): #this assumes that initial system bell is picked up correctly
    #	start = wavs[0][3]
    #	if type(r_list) != list:
	#   	r_list = r_list.tolist()
    #	for i in range(len(wavs)):
    #		if wavs[i][3] <= -1: # missed a point, assumes PC is slower than Wav
    #			r_list.insert(i, 999999999.0)
    #			wavs = self.analyze( pc_data, self.add_data( self.range_check(wavs, r_list) ))
    #		if wavs[i][3] >= (abs(start)+500): # too many points
    #			r_list.pop(i)
    #			wavs = self.analyze( pc_data, self.add_data( self.range_check(wavs, r_list) ))
    #		start = wavs[i][3]    			
    #	return wavs
    
    #********************************************************************************************
    # Due to the nature or self.analyze, we have to make sure that self.analyze gets passed at 
    # least 1 list with a length equal or greater than the PC data list. This is because in lines 
    # 110-113, we chose the smaller list to itterate with. 
    #********************************************************************************************
    #def range_check(self, template, lis): 
    #	if len(lis) < len(template):
    #		count = len(template)-len(lis)
    #		for i in range(count):
    #			lis.append( 9999999 ) # not sure if this is completely correct
    #   return lis
        
def main():
    global laptop, screenres, experimentname
    exp = Processor(laptop, screenres, experimentname)
    exp.do_exp()
    
if __name__ == "__main__":
    main()
