# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import config
import random
import os
import sys
import field
import trial
import tkutil
import datetime
import time
"""
Runs a generic experiment; global parameters are in config.py.  Specific
parameters for each trial are read for lines in a parms file. Trial.py
defines the Trial class does all the specifics for a trial -- getting the
initial parameters, running the trial, and saving the data.  
"""
def get_name(mess, t):
    """
    Uses TKinter to get first and last name separated by a space.
    get_name(message, title) -> string with names
    """
    while 1:
        answer = tkutil.enterbox(message=mess, title=t)
        if answer == "" or answer == None:
            tkutil.msgbox(message="Please enter required information")
            continue
        
        if tkutil.is_alpha(answer):
            break
        else:
            tkutil.msgbox(message="No specials!")
    return answer

def instruct(fname, mess, tit):
    """
    Uses TKinter to display instructions in a file, fname.
    """
    with open(fname, "r") as f:
        t = f.readlines()
    tkutil.textbox(message=mess, title=tit, text=t)

def prepare(blockLab):
    """
    Trials objects are created from lines in a file named in config.trialParms.
    A two dimensional array to Trial objects is constructed.  Blocks and trials
    are the dimensions.
    
    'prepare' is passed a list of header labels, e.g. ("[block1", "[block2"). The parser skips to the header matching each label in the list. and reads each line 
    (skiping lines beginning with ';' (comments), and uses split to make
    a tuple of args which are passed to the constructor of each Trial.  
    """
    blockList = []
    for blockName in blockLab:
        trialList = []         

        for repeat in range(config.blockRepeat):
            infile = open(config.trialParms, "r") 
            while 1:
                s = infile.readline()
                if s.find(blockName) >= 0:
                    break
            while 1:
                s = infile.readline()
                if not s or s.find("[") >= 0:
                    break
                if s[0] == ';':
                    continue
                args = s.split()
                trialList.append(trial.Trial(args))
            infile.close()
        # need to shuffle
        random.shuffle(trialList)
        blockList.append(trialList)

    return blockList

def msgScreen(text, wait_time, screen, background):
    """
    Displays text on a single line centered in the display for 'time' duration.
    """

    background.fill(config.bg)
    screen.blit(background,(0,0))
    font = pygame.font.SysFont("Times New Roman", 30)
    s = font.render(text, True, config.fg)
    w, h = font.size(text)
    x, y = screen.get_rect().center
    screen.blit(s, (x - w/2, y - h/2))
    pygame.display.update()
    time.sleep(wait_time)
    
def run(blockList, screen, background):
    """
    Get trial for the current block.  Call give() to run the trial.
    """
    nblock = 1
    for block in blockList:
        for currentTrial in block:
            currentTrial.give(screen, background)
        # give rest between blocks, but not after last block
        if nblock < len(blockList):
            nblock += 1
            msgScreen("Take a short break", 5, screen, background)
   
def saveTrials(blockList, exp, sub):
    """
    Save the data for the subject in a file where the filename is based
    on the participants name, e.g., joe blow has filename blowjoe.dat
    """
    now = datetime.datetime.now()
    s = sub.split(" ")
    if len(s) >= 2:
        ofile = s[1]+s[0]+".dat"
    else:
        ofile = s[0]+".dat"
    with open(ofile, 'a') as of:
        of.write("; %d/%d/%d; %d:%02d\n" % (now.month, now.day, now.year, now.hour, now.minute))
        of.write("; Experimenter's name: %s\n" % exp)
        of.write("; Subject's name: %s\n" % sub)
        for line in config.dataFileHeader:
            of.write(line)
    for block in blockList:
        for currTrial in block:
            currTrial.printOut(ofile)

def main():

    instruct("welcome.txt", "To continue click OK", "Illusion Experiment")
    experimenter = get_name("Type the Experimenter's name: Jane Doe", "Experimenter's name")
    subject = get_name("Type the Participant's name: Jane Doe", "Participant's name")
    instruct(config.instructions, "To continue click OK", "Instructions")
    pygame.init()   
    #   Reset screen properties to highest res full screen and double buffered
    modes = pygame.display.list_modes()
    # modes[0] is too high a res for some machines -- step back to modes[1]    
    if config.dbuf == True:
        screen = pygame.display.set_mode(modes[0], pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(modes[0], pygame.FULLSCREEN)
    screen = pygame.display.get_surface()
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    pygame.mouse.set_visible(False)
    #   if practice trials are called for, make them and run them
    if len(config.practiceLables) > 0 :
        msgScreen("Begin practice trials", 2, screen, background)
        practiceList = prepare(config.practiceLables)
        run(practiceList, screen, background)
    msgScreen("Start Trials",5, screen, background)
    #   Make trials, run, and save
    blockList = prepare(config.blockLables)
    run(blockList, screen, background)
    saveTrials(blockList, experimenter, subject)
    #   Say goodnight, Gracie
    msgScreen("That's all.  Thanks for your participation.", 5, screen, background)
    pygame.quit()
    
if __name__ == "__main__":
    main()

