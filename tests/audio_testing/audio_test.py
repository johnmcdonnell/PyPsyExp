from trunk import *

def main():
    
    aud = pypsyexp.Audio('s_68_small.wav', 's_68.dat', .98, .75, 8000)
    aud.do_exp()
    
main()