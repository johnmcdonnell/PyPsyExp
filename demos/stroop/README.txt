Greetings pypsyexp user!

This demo recaptulates the famous stroop task. It presents words in one of four
colors (red, green, blue, or yellow) and depending on the block, queries either
the color specified by the word or the color of the word itself. In a block in
which the actual color is queried, some catch words are either gibberish or
non-color english words. One variable manipulated is whether the word is
inverted or not.

The demo is provided as a demonstration of appropriate coding practices while
using pypsyexp. A quick way to get started with pypsyexp is to take this demo
and modify it to suit your needs.

There are two versions present here:

'stroop_new.py' - This is a new of the demo, which was designed to take
                  advantage of the changes to the api that have been made from
                  revision 31 to 45, including built-in intialization and heavy
                  use of keyword arguments for transparency. It has also been
                  cleaned up a little bit, for less redundency and inceased
                  clarity. It is recommended that beginners to pypsyexp start
                  here.

'Stroop.py' - This is the legacy version of the demo, which was designed to
              use the pypsyexp module as it existed prior to revision 31.
              It still works with the current version of pypsyexp.

Quick start:
To see how the program runs, change directory at the commandline to this
folder, then type

python stroop_new.py

The experiment should boot up.

Requirements:
This demo requires a working installation of pygame. For advice on how to get
pygame working on your computer, or more information about the pypsyexp
package, point your browser to http://pypsyexp.org.

To ask a question, report a bug, or suggest a feature, join us at 
http://getsatisfaction.com/pypsyexp

