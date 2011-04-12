
import pygame
import pygame.locals as pglc
import pypsyexp as ppe
import unittest

COLS = pygame.colordict.THECOLORS


class testExp( unittest.TestCase ):
    def setUp( self ):
        options = dict( fontname="Times New Roman" )
        self.exp = ppe.Experiment(True, (500, 500), "Test", **options )
        self.exp.set_filename( "/dev/null" )
    
    def test_getresp(self): 
        self.exp.place_text_image( prompt="Press p or q." )
        self.exp.update_display()
        print "On screen should be a request for a response (p or q)."
        print self.exp.get_response_and_rt_pq()
    
    def test_esc_sleep(self): 
        self.exp.place_text_image( prompt="Sleeping for 10 seconds." )
        self.exp.place_text_image( prompt="Press n to escape.", yoff=80 )
        self.exp.update_display()
        print "On screen should say we're sleeping."
        self.exp.escapable_sleep(pause = 10 * 1000, esckey=pglc.K_n)
    
    def test_textbox(self):
        #self.datafile = open( '/dev/null', 'w' )
        print "Should have put up a text box."
        background = self.exp.clear_screen( COLS['white'] )
        pygame.draw.rect( background, COLS['red'], (50, 100, 30, 30) )
        print "Textbox response:"
        print self.exp.prompt_text( background, 100, 100, maxlength= 30 )


if __name__ == '__main__':
    unittest.main()

