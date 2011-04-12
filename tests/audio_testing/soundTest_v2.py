import pygame
from pygame.locals import *
from lib.pypsyexp import *
from random import randrange, randint, shuffle
from wave import *

experimentname="Sound Test v2"
laptop = True
screenres = (800,600)

FREEPRESS = 0
CUEDPRESS = 1

black = (0,0,0)

class Sound(Experiment):
	
	def __init__(self, laptop, screenres, experimentname):
		
		Experiment.__init__(self, laptop, screenres, experimentname)
		
		if randint(0,1) == 0:
			self.press = FREEPRESS
		else:
			self.press = CUEDPRESS
		
		self.load_all_resources('images', 'sounds')
		[self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('soundPattern.txt')
		self.set_filename("s_" + str(self.subj))
		
	def mod_get_response_and_rt_pq(self, val):
		end = 0
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
		
	
	def do_trial(self, cond):

		self.mysurf.fill(black)
		if cond == FREEPRESS:
			msg = "Press freely"
			wait = 0
		elif cond == CUEDPRESS:
			msg = "Press ASAP after cue"
			wait = randrange(500, 1001, 500) # to prevent guessing
				
		self.place_text_image(self.mysurf, msg, 30, 0,0,white, black)
		self.update_display(self.mysurf)
			
		exit = False
		while not exit:			
			
			if cond == CUEDPRESS:
				self.escapable_sleep(wait) # pauses pygame clock right?
				#self.play_sound('sharp_click.wav', 80) # this isnt necessary and it makes the audio files more similar
				img = self.show_centered_image('click.png', black) #signals when to make a response with an image of 'CLICK!'
				self.mysurf.blit(img, [0,0])
				self.update_display(self.mysurf)
				
			[res, rt, pressed] = self.mod_get_response_and_rt_pq(['A','B'])
			# it takes 11-13ms on my PC to process time_since_last in the continous press condition				
			if res == 'A' or res == 'B':	
				time_since_last = pressed - self.place_holder # time since last response			
				self.place_holder = pressed 				# then gets updated
				time_since_start = pressed - self.experiment_timer
				return  [time_since_start, time_since_last, rt, wait, res, cond] # subtracting rt from pressed will get sound time		
			else:
				exit = False				

	def run(self):
		
		self.mysurf = self.clear_screen(black)
		self.update_display(self.mysurf)
		self.escapable_sleep(1000)
		
		self.experiment_timer = self.place_holder = pygame.time.get_ticks()
		self.play_sound('sharp_click.wav', 80) # this click will determine the start of the .wav file
		
		for i in range(1):
			for j in range(10):
				since_start, since_last, rt, wait, res, cond = self.do_trial(self.press)
				trial = (10*i) + j
				print [trial, since_start, since_last, rt, wait, res, cond]
				self.output_trial([trial, since_start, since_last, rt, wait, res, cond])
				
			if self.press == CUEDPRESS: # fixation point after each 10
				surf = self.show_centered_image('fixation.jpg', black)
				self.mysurf.blit(surf, [0,0])
				self.update_display(self.mysurf)	
				self.escapable_sleep(3000)		
	
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
