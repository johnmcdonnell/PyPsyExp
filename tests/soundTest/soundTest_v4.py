import pygame
from pygame.locals import *
from lib.pypsyexp import *
from random import randrange, randint, shuffle
from wave import *
import time

experimentname="Sound Test v4"
laptop = True
screenres = (800,600)

black = (0,0,0)

class Sound(Experiment):
	
	def __init__(self, laptop, screenres, experimentname):
		
		Experiment.__init__(self, laptop, screenres, experimentname)

		self.load_all_resources('images', 'sounds')
		[self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('soundPattern.txt')
		self.set_filename("s_" + str(self.subj))
		
	
	def run_loop(self):
		#exit = False
		wait = 500
		li = []
		start_time = place_holder = pygame.time.get_ticks()
		while (place_holder+wait)>= start_time:
			start_time = pygame.time.get_ticks()
			for event in pygame.event.get():
				if event.type == KEYDOWN:
					if pygame.key.get_pressed()[K_LSHIFT]: #and pygame.key.get_pressed()[K_BACKQUOTE]:
						self.exit1()
					else:
						li.append( pygame.key.name( 97 ) )
						
		#self.play_sound('sharp_click.wav', 0)
		print '\a'			
		end = pygame.time.get_ticks()
		[res, rt, pressed] = ['A', '000', end]
		time_since_last = pressed - self.place_holder # time since last response			
		self.place_holder = pressed 				# then gets updated
		time_since_start = pressed - self.experiment_timer
					
			
		if len(li) > 0:
			cond = 1
		else: cond = 0
		
		return [time_since_start, time_since_last, rt, wait, res, cond, len(li)]
		
	def run(self):	
		self.experiment_timer = self.place_holder = pygame.time.get_ticks()
		print '\a'
		time.sleep(.200)
		for i in range(500):
			since_start, since_last, rt, wait, res, cond, li = self.run_loop()			
			trial = i
			print [trial, since_start, since_last, rt, wait, res, cond, li]
			self.output_trial([trial, since_start, since_last, rt, wait, res, cond, li])	
	
		self.exit1()
					
	def exit1(self):
		exit()
		SystemExit
		

def main():
	global laptop, screenres, experimentname
	exp = Sound(laptop, screenres, experimentname)
	exp.run()		

if __name__ == '__main__':
    main()
