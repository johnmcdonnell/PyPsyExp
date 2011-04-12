import pygame
from pygame.locals import *
from lib.pypsyexp import *
from random import randrange, randint, shuffle
from wave import *
import time

experimentname="Sound Test v5"
laptop = True
screenres = (800,600)

black = (0,0,0)

class Sound(Experiment):
	
	def __init__(self, laptop, screenres, experimentname):
		
		Experiment.__init__(self, laptop, screenres, experimentname)

		self.load_all_resources('images', 'sounds')
		[self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('soundPattern.txt')
		self.set_filename("s_" + str(self.subj))
		
	def mod_get_response_and_rt_pq(self, val):
		time_stamp = pygame.time.get_ticks()		
		while 1:
			res = self.get_response()
			if (res == 'Q' or res=='q'):
				res = val[0]
				break
			elif (res == 'P' or res == 'p'):
				res = val[1]
				break
				
		end = pygame.time.get_ticks()		
		rt = end - time_stamp
		
		return [res, rt, end]		
	
	def do_trial(self):

		#wait = randrange(500,1001, 500)
		wait = 500
		pygame.time.delay(wait)
		#self.play_sound('sharp_click.wav', 0)		
		print '\a'
		surf = self.show_centered_image('click.png', black)
		self.mysurf.blit(surf, [0,0])
		self.update_display( self.mysurf ) 
		
		end = pygame.time.get_ticks()
		#[res, rt, pressed] = self.mod_get_response_and_rt_pq(['Q','P'])
		[res, rt, pressed] = ['N/A', 000, end]
		time_since_last = pressed - self.place_holder # time since last response			
		self.place_holder = pressed 				# then gets updated
		time_since_start = pressed - self.experiment_timer

		self.mysurf.blit(self.clear_screen(black), [0,0])
		self.update_display(self.mysurf)

		return [time_since_start, time_since_last, rt, wait, res]
		
	def run(self):
        self.mysurf = self.clear_screen(black)
		
		self.update_display(self.mysurf)
		
		cond ="N/A"
		self.experiment_timer = self.place_holder = pygame.time.get_ticks()
		#print '\a'
		self.play_sound('sharp_click.wav', 0)
		time.sleep(.200)
		for i in range(500):
			since_start, since_last, rt, wait, res = self.do_trial()		
			trial = i
			print [trial, since_start, since_last, rt, wait, res, cond]
			self.output_trial([trial, since_start, since_last, rt, wait, res, cond])	
	
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
