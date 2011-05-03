.. PyPsyExp documentation master file, created by
   sphinx-quickstart on Tue Apr 12 20:56:22 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


What is PyPsyExp?
====================================

PyPsyExp is a user-friendly and cross-platform library for developing
psychology experiments using `Python <http://python.org>`_, `Pygame
<http://pygame.org>`_ and `NumPy <http://numpy.org>`_. While (currently) not as
full featured as something like `VisionEgg <http://www.visionegg.org/>`_ or the
`Psychophysics toolbox <http://psychtoolbox.org/>`_, our objective is to
provide a clean and simple toolkit that may be exactly what you are looking for
if you need a straightforward way to design a higher-level cognition
experiment.

What does "higher-level" mean? It means you need a way to design simple, but
interactive experiments that involve presenting information on a computer
screen (but don't need millisecond accuracy on display refreshes) and
measuring a participant's responses and reaction time. 


Features
------------
 * Several input methods, such as mouse buttons and text boxes.
 * Automatic counterbalancing and data recording, across computers and even
   labs via FTP.
 * Complete cross-platform support; the same code should run on Windows, Macs,
   and UNIX machines.
 * Entirely free and open source. Free to extend in any way you want.

Quick setup
====================================

Dependencies
------------
To use pypsyexp. you'll need 
 * `Python 2.x <http://python.org>`_: A powerful scripting language summarized `here <http://xkcd.com/353/>`_
 * `NumPy <http://numpy.org/>`_: A package for numerical computation in Python.
 * `PyGame <http://pygame.org/download.shtml>`_: A Python wrapper for `libsdl <http://libsdl.org>`_, an open source multimedia library.

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

For more information, check out our tutorial on the Stroop experiment `here <http://smash.psych.nyu.edu/pypsyexp/stroop1.php>`_.


Documentation
=============

.. toctree::
    :maxdepth: 2
    
    pypsyexp
    Tutorials

Contact info
=============
If you're using (or trying to use) PyPsyExp and have run into bugs that need
fixing, features you'd like to see, or if you're just having trouble doing what
you want, send us an email at XXX@nyu.edu.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. vi: set sw=4 ts=4
