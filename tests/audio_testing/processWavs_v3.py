####################################################################
#	To do:
#	1) Adjust threshold criteria for 1000-window
#	2) Look over analyze when ready
#	3) ...left and right cant be split, so adjust for it
#	3) CLEAN UP!
#	4) Check array values for output
#   5) Needs to adjust for the condition
#
####################################################################

import pygame
from pygame.locals import *
from time import *
from lib.pypsyexp import *
from numpy import array
from wave import open as W
import struct

laptop = True
experimentname = 'Proccess Wavs'
LAPTOP = ( 1024, 768 )
FULLSCREEN = (1024, 768 )

if laptop: screenres = LAPTOP
else: screenres = FULLSCREEN

class Processor():

	
	def __init__(self, laptop, screenres, experimentname):
		pygame.init()
		self.laptop = laptop	
		
	def do_exp(self):
		sample_window = 8000
		
		splits, runtime, length = self.readwav('sounds/s_68.wav') # splits is a numpy array
		pc_data = self.read_data('data/s_68.dat')
		self.cond = pc_data[0][6]
		
		[absolute_l, relative_l, windows_l] = self.histog(splits[0],length, sample_window) # beeps from computer
		print absolute_l, relative_l

		l_list = self.parsewav(splits[0], length, absolute_l, relative_l, sample_window, windows_l) # beeps from computer
		self.start = l_list[0][0] # every running of the experiment starts with a click noise to signal the start		
		l_list.pop(0) # takes out the start click out of analysis
		self.add_data(l_list)
		self.analyze(pc_data, l_list)

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
		timed = pygame.time.get_ticks() ############
		[values, bins] = histogram(audio, bins=(audio.max()-audio.min()),normed=True) # numpy

		absolute = where( cumsum(values) >= .99)[0][0]
		
		print "end of histog for single sample", (pygame.time.get_ticks() - timed)/1000.0 ##############
		timed = pygame.time.get_ticks() ############

		a = audio[0:] # start values
		b = append(audio[window+1:length], resize(array(0), window+1)).reshape(length,1) #end values	
		# next line adds neg(a) and b, and appends the sum of the first window to the start of the array		
		offsets = append( sum( audio[0 : window] ), sum( hstack( ( negative(a) , b ) ), axis = 1) )
		windows = cumsum( offsets )
		print "end of getting windows bins: ", (pygame.time.get_ticks() - timed)/1000.0 ##############
		
		timed = pygame.time.get_ticks()
		[values, bins] = histogram(windows, bins=(windows.max()-windows.min()), normed=True)
		print "End of histogram function : " , (pygame.time.get_ticks() - timed)/1000.0
		
		timed = pygame.time.get_ticks()
		relative = where ( cumsum( values ) >= .75 )[0][0]

		print "End of getting relative : " , (pygame.time.get_ticks() - timed)/1000.0

		return [absolute, relative, windows]	
	
	def parsewav(self, audio, length, absolute, relative, sample_window, windows_l): # gets sound points
		
		timed = pygame.time.get_ticks()
		
		d = greater( audio, absolute ) #list of True/False based on whether indiv. samples are greater than absolute
		e = greater( windows_l[0:length].reshape(length,1), relative) # same, but for windows list
		f = logical_and( d, e )  # true = where both are true for both absolute and relative
		g = where( f == True )[0] # array where both absolute and relative are true
		h = g[1:len(g)].reshape(len(g)-1, 1) # new array from 1:len
		i = g[0:len(g)-1].reshape(len(g)-1, 1)  # new arrary from 0:len-1
		j = abs(sum( hstack( (negative(h), i) ), axis =1 )) # difference between g+h, stacked, sumed across and abs'd 	
		vals = append( 0, asarray(where( j > 8000 ))) # indices of where the correct points are	
		ms = (g[vals[:]+1]/44100.0).reshape(len(vals), 1).tolist()	# ms... somewhere 1 value is missing, so had to add it in		

		print ms
		print "end of parsewav ", (pygame.time.get_ticks() - timed)/1000.0 ##############
		return ms
		
	def analyze(self, pc_data, l_channel):
		# pc_data = [  [trial, time since start, time since last click/press, RT, wait_time, response, cond], .. [], [] ]
		# l_channel =  [ [time(ms), time since start(ms), time since last ], ... [], [] ]
		timed = pygame.time.get_ticks()		
		new_array = []
		choice = pc_data
		if len(pc_data) <= len(l_channel):
			choice = pc_data
		else:
			choice = l_channel
		
		for i in range(58):
			new_array.append( [ pc_data[i][0], pc_data[i][1], (l_channel[i][1]*1000), ( float(pc_data[i][1]) - (l_channel[i][1]*1000) ), pc_data[i][2], l_channel[i][2], (float(pc_data[i][2])-l_channel[i][2]), pc_data[i][6] ] )
		
		print "end of analyze ", (pygame.time.get_ticks() - timed)/1000.0
		
		print "[trial, since_start_PC, since_start_MIC, DIFF, since_click_PC, since_click_MIC, DIFF, COND]"
		for i in new_array:
			print i
		
	def add_data(self, l_channel):
		
		previous = self.start
		for i in range(len(l_channel)): # i here are lists
			time_since_last = l_channel[i][0] - previous
			l_channel[i].extend( [ l_channel[i][0] - self.start, (time_since_last*1000) ] )
			previous = l_channel[i][0]		
		
def main():
	global laptop, screenres, experimentname
	exp = Processor(laptop, screenres, experimentname)
	exp.do_exp()
	
if __name__ == "__main__":
	main()
