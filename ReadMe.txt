# Comic-Archiver
A (template for a) program for saving a local copy of a webcomic from the net (Essentially a web scraper)
Since most websites are different, each site will need some code tweeking to save properly
(Will mark those sections of code with #UserTweek)
Most of the recoding will be in the __main__ declaration
// This program is old (since Python2 old), and been through many revisions. But it works well enough to keep using it.

Running:
running the main program will autogenerate the "ComicArchiver.log" and a "saved" folder to store the targets

TODO:
-add getting started to ReadMe.txt
-perhaps make an option to load a config file instead of having to manually alter source code?
-improve sandbox code execution, more failsafes
-if debug.err invoked, print last x lines of debug dialog, even if debuging is disabled
-build error handling into savetarget2 function
-replace subprocess.check_output with subprocess.run # https://docs.python.org/3.5/library/subprocess.html

BUGS:
-saveTarget2 can't overwrite files, not proper error handling
-urllib.request.urlopen() can hang, causing program to hang
-checkpoints save on pages that are ABOUT to be processed, not pages that HAVE been processed
-checkpoint is saved immediatly after loading a checkpoint
