#!/bin/bash

# This version of run.command is relative... it opens exp.py in its own folder.

path=$0             # path is path to this file
cd ${path%/*.*}     # clip off the file name to get directory path and cd
python Stroop.py

