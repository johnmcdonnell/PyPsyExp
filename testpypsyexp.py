
import pygame
import pypsyexp as ppe
import unittest

COLS = pygame.colordict.THECOLORS


class testExp(ppe.Experiment):
    def __init__(self, res, name, **options):
        ppe.Experiment.__init__(self, (500, 500), "Test", **options )
        self.set_filename( "/dev/null" )

    def testTextbox(self):
        self.datafile = open( '/dev/null', 'w' )
        background = self.clear_screen( COLS['white'] )
        pygame.draw.rect( background, COLS['red'], (50, 100, 30, 30) )
        return self.prompt_text( background, 100, 100, maxlength= 30 )

class testExpUnit( unittest.TestCase ):
    def setUp( self ):
        self.exp = testExp()
    
    def test_getresp(self): 
        self.exp.prompt_text( prompt="Press p or q." )
        print self.exp.get_response_and_rt_pq()



def main():
    options = dict( nofullscreen=True, fontname="Times New Roman" )
    e = testExp((500, 500), "Test", **options )
    resp = e.testTextbox()
    print resp

if __name__ == '__main__':
    main()

