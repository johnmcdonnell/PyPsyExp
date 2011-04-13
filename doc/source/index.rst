.. PyPsyExp documentation master file, created by
   sphinx-quickstart on Tue Apr 12 20:56:22 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


What is PyPsyExp?
====================================

PyPsyExp is a user-friendly library for developing psychology experiments
using Python, Pygame and NumPy. While (currently) not as full featured as
something like VisionEgg or the Psychophysics toolbox, we may be exactly
what you are looking for if you need a simple way to design a higher-level
cognition experiment.

What does "higher-level" mean? It means you need a way to design simple, but
interactive experiments that involve presenting information on a computer
screen (but don't need millisecond accuracy on display refreshes) and
measuring a participant's responses and reaction time. 

Quick setup
====================================

Dependencies
------------
To use pypsyexp. you'll need 
 * `Python 2.x <http://python.org>`_
 * `numpy <http://numpy.org>`_
 * `pygame <http://pygame.org>`_

Download
--------
We keep the latest versions of our code publically accessible in a subversion
repository, located at https://compcog.svn.beanstalkapp.com/pypsyexp/trunk.

If you have never used pygame before, we recommend you begin by installing
pygame along with a simple stroop task, which serves as a demonstration of how
pypsyexp works::
 svn co https://compcog.svn.beanstalkapp.com/pypsyexp/trunk/demos/stroop pypsyexp_demo

...which will check out the demo to the folder ``pypsyexp_demo``.

If you are already familiar with the library and simply want to check out the
latest version, this will check out the library alone::
 svn co https://compcog.svn.beanstalkapp.com/pypsyexp/trunk/lib/

Experiment design
-----------------
The actual pypsyexp library is in the ``lib/`` directory. In ``stroop_new.py``
is an experiment file that loads in the library and runs an experiment that is
designed to replicate the classic Stroop effect. The file follows a structure
we would recommend, defining a class called ``StroopExperiment`` which extends
the ``Experiment`` class defined in the ``pypsyexp`` library. To build your own
experiment, you can simply alter this file to suit your needs.


Documentation:
=============

.. toctree::
    :maxdepth: 2
    
    pypsyexp


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. vi: set sw=4 ts=4
