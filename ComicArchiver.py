'''
Author: Medic5700
Purpose: To archive various webcomics in a local copy
'''
import urllib.request # for url stuff
import logging # for logging
import time # to sleep
import os # for the filesystem manipulation
import subprocess # used for saving stuff from the web using the system shell commands (if urllib fails)
import json # for javascript datascructure parsing, if needed
from typing import Any, Callable, Dict, Generic, List, Literal, Text, Tuple, Type, TypeVar

'''
class Debug:
    """Class for logging and debuging"""
    
    def __init__(self, debugMode : bool, file : str = "Debug.log"):
        self.__filename : str = file
        self.showDebug : bool = debugMode
        
    def __save(self, text : str):
        """Saves text to file as a log entry"""
        logfile = open(self.__filename, 'a')
        try:
            logfile.write(text)
        except:
            self.err("Error Occured in Error Logging Function: Attempting to report previous error")
            i : str # line
            for i in text:
                try:
                    logfile.write(i)
                except:
                    logfile.write("[ERROR]")
        logfile.close()

    def log(self, text : str):
        """Takes string, pushes to stdout AND saves it to the log file
        
        For general logging, and non-fatal errors
        """
        temp : str = "[" + time.asctime() + "] Log: " + text
        print(temp)
        self.__save(temp + "\n")
    
    def err(self, *text):
        """Takes string, pushes to stdout and saves it to the log file
        
        Mainly meant for non-recoverable errors that should cause the program to terminate"""
        timestamp = "[" + time.asctime() + "] ERR:"
        temp = ""
        for i in text:
            temp += "\t" + str(i) + "\n"
        print(timestamp + temp)
        self.__save(timestamp + temp + "\n")        
    
    def debug(self, *args):
        """takes n number of strings, pushes to stdout and log file
        
        only writes input to stdout/log file when self.showDebug is True (debugMode was set to true when initialized)"""
        if (self.showDebug):
            temp = "Debug:"
            for i in args:
                temp += "\t" + str(i) + "\n"
            print(temp, end="") #fixes issue where log and sceen output newlines don't match
            self.__save(temp)
    
#debugging and logging stuff
import logging
import inspect #used for logging, also used to assertion testing
debugHighlight = lambda _ : False #debugHighlight = lambda x : 322 <= x <= 565 #will highlight the debug lines between those number, or set to -1 to highlight nothing
def debugHelper(frame : "Frame Object") -> str:
    """Takes in a frame object, returns a string representing debug location info (IE: the line number and container name of the debug call)

    Usage 
        -> logging.debug(debugHelper(inspect.currentframe()) + "String")
        -> DEBUG:root:<container>"remove"[0348]@line[0372] = String
    Used for easy debugging identification of a specific line
    No, you can't assign that code segment to a lambda function, because it will always return the location of the original lambda definition

    Reference:
        https://docs.python.org/3/library/inspect.html#types-and-members
    """
    assert inspect.isframe(frame)
    
    #textRed : str = "\u001b[31m" #forground red
    textTeal : str = "\u001b[96m" #forground teal
    ANSIend  : str = "\u001b[0m" #resets ANSI colours

    line : str = ""

    if debugHighlight(frame.f_lineno):
        line += textTeal
   
    line += "<container>\"" + str(frame.f_code.co_name) + "\"" #the name of the encapuslating method that the frame was generated in
    line += "[" + str(frame.f_code.co_firstlineno).rjust(4, '0') + "]" #the line number of the encapsulating method that the frame was generated in
    line += "@line[" + str(frame.f_lineno).rjust(4, '0') + "]" #the line number when the frame was generate
    line += " = "

    if debugHighlight(frame.f_lineno):
        line += ANSIend

    return line
'''
       
class SpecialCases:
    """Class for handling special cases triggered by URLCurrent matching a key in the dictionary"""
    
    def __init__(self, specialCases = {}):
        assert type(specialCases) is dict, "SpecialCases -> __init__ -> arg1: specialCases needs to be a dictionary"
        
        self.__cases : dict = specialCases
        
    def trigger(self, url : str):
        """takes URL, if URL in specialCases, executes code"""

        assert type(url) is str

        if (url in self.__cases):
            #error.log("Special Case detected: " + url)
            logger.info("Special Case detected: " + url)
            try:
                self.__sandbox(self.__cases[url])
            except:
                #error.err("SpecialCases->trigger->__sandbox : (-1014) Error while executeing special case")
                logger.critical("SpecialCases->trigger->__sandbox : (-1014) Error while executeing special case")
                exit(-1014)
    
    def __sandbox(self, code):
        """Takes python code as string, runs code within a sandbox"""
        global URLCurrent
        global URLNext
        global targetTitle
        global targetURL
        global comicNumber
        global pageNumber
        
        #error.debug("Before executing exec command", 
        #            "targetTitle = " + str(targetTitle), 
        #            "targetURL   = " + str(targetURL), 
        #            "URLNext     = " + str(URLNext), 
        #            "URLCurrent  = " + str(URLCurrent),
        #            "comicNumber = " + str(comicNumber),
        #            "pageNumber  = " + str(pageNumber)
        #            )
        logger.debug("Before executing exec command")
        logger.debug("targetTitle = " + str(targetTitle))
        logger.debug("targetURL   = " + str(targetURL))
        logger.debug("URLNext     = " + str(URLNext))
        logger.debug("URLCurrent  = " + str(URLCurrent))
        logger.debug("comicNumber = " + str(comicNumber))
        logger.debug("pageNumber  = " + str(pageNumber))
        
        sandboxScope = {"__builtins__":None, 
                        "URLCurrent":URLCurrent, 
                        "URLNext":URLNext, 
                        "targetTitle":targetTitle, 
                        "targetURL":targetURL, 
                        "comicNumber":comicNumber, 
                        "pageNumber":pageNumber
                        }
        #error.log("Executing code: \"" + code + "\"")
        logger.info("Executing code: \"" + code + "\"")
        exec(code, sandboxScope)
        
        #only changes variables if they have changed
        if (URLCurrent != sandboxScope['URLCurrent']):
            #error.debug("changing URLCurrent: " + str(URLCurrent) + " -> " + str(sandboxScope['URLCurrent']))
            logger.debug("changing URLCurrent: " + str(URLCurrent) + " -> " + str(sandboxScope['URLCurrent']))
            if not isinstance(sandboxScope['URLCurrent'], str):
                #error.debug("could not change URLCurrent, incorrect type")
                logger.debug("could not change URLCurrent, incorrect type")
            else:
                URLCurrent = sandboxScope['URLCurrent']
        if (URLNext != sandboxScope['URLNext']):
            #error.debug("changing URLNext: " + str(URLNext) + " -> " + str(sandboxScope['URLNext']))
            logger.debug("changing URLNext: " + str(URLNext) + " -> " + str(sandboxScope['URLNext']))
            if not isinstance(sandboxScope['URLNext'], str):
                #error.debug("could not change URLNext, incorrect type")
                logger.debug("could not change URLNext, incorrect type")
            else:
                URLNext = sandboxScope['URLNext']
        if (targetTitle != sandboxScope['targetTitle']):
            #error.debug("changing targetTitle: " + str(targetTitle) + " -> " + str(sandboxScope['targetTitle']))
            logger.debug("changing targetTitle: " + str(targetTitle) + " -> " + str(sandboxScope['targetTitle']))
            if not isinstance(sandboxScope['targetTitle'], str):
                #error.debug("could not change targetTitle, incorrect type")
                logger.debug("could not change targetTitle, incorrect type")
            else:
                targetTitle = sandboxScope['targetTitle']
        if (targetURL != sandboxScope['targetURL']):
            #error.debug("changing targetURL: " + str(targetURL) + " -> " + str(sandboxScope['targetURL']))
            logger.debug("changing targetURL: " + str(targetURL) + " -> " + str(sandboxScope['targetURL']))
            if (type(targetURL) != type([])):
                #error.debug("could not change targetURL, incorrect type")
                logger.debug("could not change targetURL, incorrect type")
            else:
                targetURL = sandboxScope['targetURL']
        if (comicNumber != sandboxScope['comicNumber']):
            #error.debug("changing comicNumber: " + str(comicNumber) + " -> " + str(sandboxScope['comicNumber']))
            logger.debug("changing comicNumber: " + str(comicNumber) + " -> " + str(sandboxScope['comicNumber']))
            if not isinstance(sandboxScope['comicNumber'], int):
                #error.debug("could not change comicNumber, incorrect type")
                logger.debug("could not change comicNumber, incorrect type")
            else:
                comicNumber = sandboxScope['comicNumber']
        if (pageNumber != sandboxScope['pageNumber']):
            #error.debug("changing pageNumber: " + str(pageNumber) + " -> " + str(sandboxScope['pageNumber']))
            logger.debug("changing pageNumber: " + str(pageNumber) + " -> " + str(sandboxScope['pageNumber']))
            if not isinstance(sandboxScope['pageNumber'], int):
                #error.debug("could not change pageNumber, incorrect type")
                logger.debug("could not change pageNumber, incorrect type")
            else:
                pageNumber = sandboxScope['pageNumber']
        
        #error.debug("After executing exec command", 
        #            "targetTitle = " + str(targetTitle), 
        #            "targetURL   = " + str(targetURL), 
        #            "URLNext     = " + str(URLNext), 
        #            "URLCurrent  = " + str(URLCurrent),
        #            "comicNumber = " + str(comicNumber),
        #            "pageNumber  = " + str(pageNumber)
        #            ) 
        logger.debug("After executing exec command")
        logger.debug("targetTitle = " + str(targetTitle))
        logger.debug("targetURL   = " + str(targetURL))
        logger.debug("URLNext     = " + str(URLNext))
        logger.debug("URLCurrent  = " + str(URLCurrent))
        logger.debug("comicNumber = " + str(comicNumber))
        logger.debug("pageNumber  = " + str(pageNumber))
    
class Checkpoint:
    """Class for loading and saving checkpoints"""
    
    def __init__(self, name : str = "Checkpoint.csv", checkpointFrequency : int = 16):
        global URLCurrent
        global pageNumber
        global comicNumber
        assert type(name) is str
        assert len(name) > 0
        assert type(checkpointFrequency) is int
        assert (checkpointFrequency > 0),"Checkpoint -> __init__ -> arg2: checkpointFrequency needs to be greater then 0"
        
        self.filename : str = name
        self.__checkpointFrequency : int = checkpointFrequency
        self.__callsSinceLastCheckpoint : int = 0
        if not (os.path.exists(self.filename)):
            #error.log("Checkpoint file not found, creating checkpoint file")
            logger.info("Checkpoint file not found, creating checkpoint file")
            file = open(self.filename,'w')
            file.write("URLCurrent,pageNumber,comicNumber\n")
            file.write(URLCurrent + "," + str(pageNumber) + "," + str(comicNumber) + "\n")
            file.close()
        
    def load(self):
        """Loads checkpoint from file, sets URLCurrent, pageNumber, ComicNumber"""
        global URLCurrent
        global pageNumber
        global comicNumber
        
        #error.debug("Attempting to load checkpoint")
        logger.debug("Attempting to load checkpoint")
        raw : List[str] = None
        try:
            file = open(self.filename, 'r')
            raw = file.read().split('\n')
            file.close()
        except Exception as exception:
            #error.err("Could not load checkpoint file: " + self.filename)
            logger.error("Could not load checkpoint file: " + self.filename)
        
        try:
            line : str = raw[len(raw)-2]
            #error.debug("line: " + str(line))
            logger.debug("line: " + str(line))
            
            URLCurrent = str((line.split(','))[0])
            pageNumber = int((line.split(','))[1])
            comicNumber = int((line.split(','))[2])
            #error.log("Checkpoint Loaded: " + URLCurrent)
            logger.info("Checkpoint Loaded: " + URLCurrent)
        except Exception as exception:
            #error.err("Checkpoint file not formated correctly: " + self.filename)
            logger.error("Checkpoint file not formated correctly: " + self.filename)
        
    def save(self):
        """Saves checkpoint, saves (URLCurrent, pageNumber, comicNumber) on every checkpointFrequency"""
        global URLCurrent
        global pageNumber
        global comicNumber
        
        #error.debug("Attempting to save checkpoint")
        logger.debug("Attempting to save checkpoint")
        if (self.__callsSinceLastCheckpoint == self.__checkpointFrequency - 1):
            file = open(self.filename, 'a')
            file.write(URLCurrent + "," + str(pageNumber) + "," + str(comicNumber) + "\n")
            file.close()
            
            #error.log("Checkpoint Saved: " + URLCurrent)
            logger.info("Checkpoint Saved: " + URLCurrent)
            self.__callsSinceLastCheckpoint = 0
        else:
            self.__callsSinceLastCheckpoint = self.__callsSinceLastCheckpoint + 1
        
def scrubPath(usage : Literal["windows", "web", "failsafe", "ascii"], path : str, dropChar : bool = False) -> str:
    """Takes a string, parses it based on usage (windows, web, failsafe, ascii), removes/escapes characters"""

    assert type(usage) is str
    assert any([(i in usage) for i in ["windows", "web", "failsafe", "ascii"]])
    assert type(path) is str
    assert type(dropChar) is bool
    
    # http://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid
    acceptableURLCharacters : str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=" + "%"
    # https://msdn.microsoft.com/en-ca/library/windows/desktop/aa365247(v=vs.85).aspx#naming_conventions
    acceptableWindowsCharacters : str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 " + "`~!@#$%^&()-=_+[]{};',." # forbidden characters = "<>:/|?*" + "\\\""
    acceptableWindowsCharactersFailSafe : str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 " + "~%()-_[]{}."
    
    output : str = ""
    maxLength : int = None
    whitelist : str = ""
    
    if (usage == "windows"):
        whitelist = acceptableWindowsCharacters
        maxLength = 32
    elif (usage == "failsafe"):
        whitelist = acceptableWindowsCharactersFailSafe
        maxLength = 16
    elif (usage == "web"):
        whitelist = acceptableURLCharacters
    elif (usage == "ascii"):
        for i in range(0,256):
            whitelist += chr(i)
    else:
        #error.err("scrubPath => argument 2 (usage) invalid: " + str(usage))
        logger.critical("scrubPath => argument 2 (usage) invalid: " + str(usage))
        exit(-1015)
    
    i : str # char
    for i in path:
        if (i in whitelist):
            output += i
        else:
            if ((not dropChar) and (usage == "ascii")):
                output += ascii(i)
            if (not dropChar):
                output += "%" + hex(ord(i) // 16)[2:].upper() + hex (ord(i) % 16)[2:].upper() # Percent-Encoding
    
    if (maxLength != None):
        output = output[0 : min(maxLength, len(output))]
    return output

def saveTarget(targetURL : str, savePath : str, saveTitle : str, overrideExtension : str = None):
    """Takes a URL, filesystem savePath, and a file name (without file extention) => Saves target of the URL at savePath as SaveTitle"""
    # assumes savePath is valid

    assert type(targetURL) is str
    assert len(targetURL) > 0
    assert type(savePath) is str
    assert len(savePath) > 0
    assert type(saveTitle) is str
    assert len(saveTitle) > 0
    assert (type(overrideExtension) is str) or (type(overrideExtension) is type(None))

    #error.debug("Attempting to save = " + targetURL)
    logger.debug("Attempting to save = " + targetURL)
    
    fileExtension : str = targetURL[targetURL.rfind('.') : len(targetURL)]
    if (overrideExtension != None):
        fileExtension = overrideExtension
    
    targetObject = None        
    i : int = 0
    while ((i <= 10) and (targetObject == None)):
        try:
            #error.debug("Loading " + targetURL)
            logger.debug("Loading " + targetURL)
            targetObject = (urllib.request.urlopen(targetURL))
        except Exception as inst: # handles timeout I think
            #error.log("Connection Fail: 1007 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(targetURL))
            logger.warning("Connection Fail =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(targetURL))
            time.sleep(4)  
        if (i == 10): # FAILSAFE
            #error.err("Picture Load Timeout: -1008 (fatal) =>\tFailed to load picture, Forcing system exit")
            logger.critical("Picture Load Timeout: -1008 (fatal) =>\tFailed to load picture, Forcing system exit")
            exit(-1008)
        i = i + 1

    try:
        if (os.path.exists(savePath + "/" + saveTitle + fileExtension)): # checks if file exists
            #error.log("File exists: 1012 (non-fatal) => \tOverwriting existing file: \t" + savePath + "/" + saveTitle + fileExtension)
            logger.warning("File exists; Overwriting existing file: \t" + savePath + "/" + saveTitle + fileExtension)
        fileObject = open(savePath + "/" + saveTitle + fileExtension, 'wb')
        fileObject.write(targetObject.read())
        fileObject.close()
    except Exception as inst:
        #error.err("Picture failed to save: -1010 (fatal) =>\tSaveTitle:" + saveTitle + "\tExtension:" + fileExtension + "\tError =>\t" + str(inst))
        logger.critical("Picture failed to save: -1010 (fatal) =>\tSaveTitle:" + saveTitle + "\tExtension:" + fileExtension + "\tError =>\t" + str(inst))
        exit(-1010)
    
    #error.debug("target saved")
    logger.debug("target saved")
    targetObject.close()

def saveTarget2(targetURL : str, savePath : str, saveTitle : str, overrideExtension : str = None):
    """Takes a URL, filesystem savePath, and a file name (without file extention => Saves target of the URL at savePath as SaveTitle
    
    Uses Windows Powershell instead python's urllib
    Is really REALLY dumb performance wise, as it closes and opens a new instance of Powershell with EVERY call
    """
    
    assert type(targetURL) is str
    assert len(targetURL) > 0
    assert type(savePath) is str
    assert len(savePath) > 0
    assert type(saveTitle) is str
    assert len(saveTitle) > 0
    assert (type(overrideExtension) is str) or (type(overrideExtension) is type(None))

    #error.debug("Attempting to save = " + targetURL)
    logger.info("Attempting to save = " + targetURL)
    #error.debug("savePath:" + savePath, "saveTitle:" + saveTitle)
    logger.info("savePath:" + savePath, "saveTitle:" + saveTitle)
    
    fileExtension : str = targetURL[targetURL.rfind('.') : len(targetURL)]
    if (overrideExtension != None):
        fileExtension = overrideExtension
        
    if (os.path.exists(savePath + "/" + saveTitle + fileExtension)): # checks if file exists
        #error.log("File exists: 1012 (non-fatal) => \tskipping existing file: \t" + savePath + "/" + saveTitle + fileExtension)
        logger.info("File exists: 1012 (non-fatal) => \tskipping existing file: \t" + savePath + "/" + saveTitle + fileExtension)
        return    
    ''' #Sudo code for powershell command
    Invoke-WebRequest $targetURL -OutFile (savePath + "test.jpg"); 
    mv -literalpath (savePath + "test.jpg") (savePath + saveTitle + fileExtension)
    '''
    try:
        # subprocess.check_output(["powershell","Invoke-WebRequest \"" + targetURL + "\" -OutFile \"" + savePath + "/" + "test.jpg" + "\"; mv -literalpath '" + savePath + "/" + "test.jpg" + "' '" + savePath + "/" + saveTitle + fileExtension + "'"])
        process = subprocess.run(["powershell","Invoke-WebRequest \"" + targetURL + "\" -OutFile \"" + savePath + "/" + "test.jpg" + "\"; mv -literalpath '" + savePath + "/" + "test.jpg" + "' '" + savePath + "/" + saveTitle + fileExtension + "'"],
                       stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if (process.stderr != b''):
            #error.err("saveTarget2: (-1016) Error Unable to save target via powershell",
            #          process.args,
            #          process.stdout.decode("UTF-8"),
            #          process.stderr.decode("UTF-8"),
            #          "Does the working directory have [square brackets]? because that seems to screw with powershell <-------------------------"
            #          )
            logger.critical("saveTarget2: (-1016) Error Unable to save target via powershell")
            logger.critical(process.args)
            logger.critical(process.stdout.decode("UTF-8"))
            logger.critical(process.stderr.decode("UTF-8"))
            logger.critical("Does the working directory have [square brackets]? because that seems to screw with powershell <-------------------------")
            exit(-1016)
    except Exception as inst:
        #error.err("saveTarget2: (-1015) Error Unable to save target via powershell => " + str(inst))
        logger.critical("saveTarget2: (-1015) Error Unable to save target via powershell => " + str(inst))
        exit(-1015)
        
    #error.debug("target saved")
    logger.debug("target saved")

def looseDecoder(datastream, blocksize : int = 4) -> str:
    """Takes a webpage data, decodes webpage blocksize at a time, returns string containing webpage data
    
    Some webpages have a couple characters that can't be decoded
    This decodes it in sections to avoid that, enabling most of the webpage to be decoded
    May not fully decode webpage
    """
    assert type(datastream) is bytes
    assert type(blocksize) is int
    assert (blocksize > 2)
    assert (blocksize % 2 == 0)

    #error.debug("looseDecoder - len(datastream) = " + str(len(datastream)))
    logger.debug("looseDecoder - len(datastream) = " + str(len(datastream)))
    errorCounter : int = 0
    
    temp : str = ""
    i : int
    for i in range(0, int(len(datastream)/blocksize) - 1):
        try:
            temp += datastream[i*blocksize : (i+1)*blocksize].decode('utf-8')
        except Exception as inst:
            errorCounter = errorCounter + 1
            for _ in range(0, blocksize):
                temp += " "
    if (errorCounter > 0):
        #error.log("LooseDecoder Warning: 1011 (non-fatal) =>\tCould not decode part of webpage, substituting (" + str(errorCounter * blocksize) + ") blanks")
        logger.info("LooseDecoder Warning: 1011 (non-fatal) =>\tCould not decode part of webpage, substituting (" + str(errorCounter * blocksize) + ") blanks")
    return temp

def asciiDecoder(datastream : bytes) -> str:
    """Takes in a bytearray datastream, replaces non-ascii characters with ' ', converts bytearray to string, returns an string"""
    assert type(datastream) is bytes

    output : str = ""

    i : int
    for i in range(len(datastream)):
        if datastream[i] < 128:
            output += chr(datastream[i])

    return output


def loadWebpage(url : str) -> str:
    """Takes a URL, returns the webpage contents as a string"""
    webpageObject = None
    datastream : str = None
    #error.debug("Attempting to load webpage " + url)
    logger.debug("Attempting to load webpage " + url)
    i : int = 0
    while ((i <= 10) and (webpageObject == None)):
        try:
            #error.debug("Loading " + url)
            logger.debug("Loading " + url)
            webpageObject = urllib.request.urlopen(url)
            # http://stackoverflow.com/questions/2712524/handling-urllib2s-timeout-python #TODO: check if order matters
        except Exception as inst:
            #error.log("Connection Fail: 1001 (non-fatal) =>" + "\tAttempt " + str(i) + ":" + str(inst) + ":\t" + str(url))
            logger.info("Connection Fail: 1001 (non-fatal) =>" + "\tAttempt " + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i == 10):
            #error.err("Coonection Timeout: -1001 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            logger.critical("Coonection Timeout: -1001 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1001)        
        i = i + 1
        
    try:
        #error.debug("Decoding webpage")
        logger.debug("Decoding webpage")
        datastream = asciiDecoder(webpageObject.read()) # may help for webpages that seem to have one bad character
    except Exception as inst:
        #error.err("Decode Error: -1003 (fatal) =>" + "\tUTF-8 decode error, Force System Exit =>\t" + str(inst))
        logger.critical("Decode Error: -1003 (fatal) =>" + "\tUTF-8 decode error, Force System Exit =>\t" + str(inst))
        exit(-1003)  
    webpageObject.close()
    #error.debug("Webpage loaded")
    logger.debug("Webpage loaded")
    return datastream

def loadWebpage2(url : str):
    """Takes a URL, returns the webpage contents as a string
    
    Uses Windows Powershell instead python's urllib
    Is really REALLY dumb performance wise, as it closes and opens a new instance of Powershell with EVERY call
    """
    datastream = None
    i : int = 0
    while ((i<=10) and (datastream == None)):
        try:
            #error.debug("Loading " + url)
            logger.debug("Loading " + url)
            datastream = str(    subprocess.check_output(["powershell", "(Invoke-WebRequest \"" + url + "\").Content"])    )
        except Exception as inst:
            #error.log("Connection Fail: 1013 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            logger.info("Connection Fail: 1013 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i==10):
            #error.err("Coonection Timeout: -1013 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            logger.critical("Coonection Timeout: -1013 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1013)        
        i = i + 1    
        
    #error.debug("Webpage loaded")
    logger.debug("Webpage loaded")
    return datastream

def parseForTargets(datastream, lineStart : str, lineEnd : str, targetStart : str, targetEnd : str, blockStart : str = "", blockEnd : str = "") -> List[str]:
    """Takes in a string (webpage HTML), and search peramiters (lineStart, lineEnd, etc), returns an array of targets as strings
    
    (Mainly used to find the URL of picture(s))
    lineStart    - inclusive
    lineEnd      - inclusive
    targetStart  - non-inclusive
    targetEnd    - non-inclusive
    blockStart   - inclusive, optional
    blockEnd     - inclusive, optional, starts search after blockStart
    """
    targets : List[str] = []
    if (blockStart == "" or blockEnd == ""):
        blockStart = lineStart
        blockEnd = lineEnd
    block : str = datastream[datastream.find(blockStart) : datastream.find(blockEnd, datastream.find(blockStart) + len(blockStart)) + len(blockEnd)]
    #error.debug("parseTarget - Block = " + str(block))
    logger.debug("parseTarget - Block = " + str(block))
    while ((lineStart in block) and (lineEnd in block)): # goes through block for each lineStart
        substring : str = block[block.find(lineStart) : block.find(lineEnd, block.find(lineStart)) + len(lineEnd)]
        #error.debug("parseTarget - substring = " + str(substring))
        logger.debug("parseTarget - substring = " + str(substring))
        
        try: # skips substring if targetStart isn't found
            targets.append(   substring[substring.index(targetStart) + len(targetStart) : substring.index(targetEnd, substring.index(targetStart) + len(targetStart))]   )
        except:
            #error.debug("praseTarget - Target not found")
            logger.debug("praseTarget - Target not found")
            
        if block.find(lineEnd, block.find(lineStart)) != -1: # checks if there is a new substring to be found after the end of the old substring
            block = block[block.find(lineEnd, block.find(lineStart))+len(lineEnd) : ]
        else:
            block = ""
        
        #error.debug("parseTarget - found linestart = " + str(lineStart in block), 
        #            "parseTarget - found lineEnd = " + str(lineEnd in block), 
        #            "parseTarget - len(block) = "+str(len(block)), 
        #            "praseTarget - reamining block = " + str(block),
        #            "parseTarget - targets = "+str(targets)
        #            )
        logger.debug("parseTarget - found linestart = " + str(lineStart in block))
        logger.debug("parseTarget - found lineEnd = " + str(lineEnd in block))
        logger.debug("parseTarget - len(block) = "+str(len(block)))
        logger.debug("praseTarget - reamining block = " + str(block))
        logger.debug("parseTarget - targets = "+str(targets))
        
    return targets    

def parseForString(datastream, lineStart : str, lineEnd : str, targetStart : str, targetEnd : str) -> str:
    """Takes in a string (webpage HTML) and search paramiters (lineStart, lineEnd, etc), returns a string found
        
    returns the empty string "" if target is not found"""
    try:
        substring : str = datastream[datastream.index(lineStart) : datastream.index(lineEnd, datastream.index(lineStart)) + len(lineEnd)]
        return substring[substring.index(targetStart) + len(targetStart) : substring.index(targetEnd, substring.index(targetStart) + len(targetStart))]
    except:
        #error.debug("parseForString => Search Failed")
        logger.debug("parseForString => Search Failed")
        return ""    
    
def parseForLine(datastream, target : str) -> str:
    """Takes in a string (webpage HTML) and target, and returns the entire line the target was found on
    
    returns the empty string "" if target is not found"""
    #TODO needs more testing
    try:
        targetLocation : int = datastream.index(target)
        lineStart : int = datastream.rindex("\n", 0, targetLocation)
        lineEnd : int = datastream.index("\n", targetLocation, len(datastream))
        return datastream[lineStart:lineEnd]
    except:
        #error.debug("parseForLine => Search Failed")
        logger.debug("parseForLine => Search Failed")
        return ""
    
def sanityCheck():
    """Returns True if all global variables are of correct type and ranges, False otherwise"""
    global URLCurrent
    global URLNext
    global targetTitle
    global targetURL
    global comicNumber
    global pageNumber
    
    fatelError = False
    
    if (targetURL == []):
        #error.log("Missing TargetURLs: 1006 (non-fatal)")
        logger.info("Missing TargetURLs: 1006 (non-fatal)")
    else:
        if '' in targetURL:
            #error.log("TargetURLs are Null: 1026 (non-fatal)")
            logger.info("TargetURLs are Null: 1026 (non-fatal)")
            temp = []
            for i in targetURL:
                if (i != ''):
                    temp.append(i)
            targetURL = temp
    
#class saveProcess:
#    '''an attempt to use a SINGLE powershell instance to save multiple targets in series.
#    IE: open powershell, give url, save thing, give url, save thing, etc
#    '''
#    #import subprocess
#    def __init__(self):
#        self.p = subprocess.Popen("powershell", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
if __name__ == '__main__':
    # These options need to be configured
    comicName       : str   = "Comic Name"
    URLStart        : str   = "Start URL" # The url to start from
    URLLast         : str   = "End URL" # the last url in the comic series, to tell the program exactly where to stop
    pagesToScan     : int   = 9999 # Maximum number of pages that this program will scan in one go
    debugMode       : bool  = False
    useCheckpoints  : bool  = False
    fullArchive     : bool  = False # saves the aditional information from webpage
    
    # Other program options
    cases           : dict  = {} 
    '''a dictionary for special cases, with keys being the current URL to trigger them, and the value being a string of python code to execute (still figuring out the security on that one)
    IE:
    cases           = {"www.exampleURL1.com": "targetURL = [\"www.exampleURL1.com/example.jpg\"]",
                       "www.exampleURL2.com": "targetURL = [\"www.exampleURL2.com/example.jpg\"]"
                        }
    '''
    numberWidth     : int   = 4 # the number of digits used to index comics
    loopDelay       : int   = 0 # time in seconds
    transactionFileName : str = "ComicArchiver-Transactions.csv"
    
    # Logging
    logger = logging.getLogger()
    logformat = logging.Formatter('[%(asctime)s] (LINE:%(lineno)s | FUNC:%(funcName)s) %(levelname)s : %(message)s')
    log2File = logging.FileHandler('ComicArchiver.log')
    log2Console = logging.StreamHandler()
    log2File.setFormatter(logformat)
    log2Console.setFormatter(logformat)
    # log2File.setLevel(logformat) # Do not do this, this does nothing, you have to set logging level to the logger this handler gets added to
    # log2Console.setLevel(logformat) # Do not do this, this does nothing, you have to set logging level to the logger this handler gets added to
    logger.addHandler(log2File)
    logger.addHandler(log2Console)
    if debugMode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info("Comic Archiver has started, =====================================================================")
    if debugMode:
        logger.info("Debug logging is enabled")
   
    #error = Debug(debugMode, "ComicArchiver.log") # Initialize the Logging Class
    #error.log("Comic Archiver has started, =====================================================================")
    #if (debugMode):
    #    error.log("Debug logging is enabled")
    

    # Global variables for parsing webpages
    URLCurrent      : str   = URLStart
    URLNext         : str   = None
    targetTitle     : str   = ""
    targetURL       : str   = None
    comicNumber     : int   = 1
    pageNumber      : int   = 1

    special = SpecialCases(cases) # Initialize the SpecialCases Class
    if (useCheckpoints):
        #error.log("Checkpoints Enabled")
        logger.info("Checkpoints Enabled")
        check = Checkpoint("ComicArchiver-Checkpoint.csv",16) # Initialize the Checkpoint Class
        check.load()

    if not (os.path.exists("./saved/")): # create folder if it doesn't exsist
        #error.log("Creating directory:\t" + "./saved/")
        logger.info("Creating directory:\t" + "./saved/")
        os.makedirs("./saved/")
    
    if (fullArchive):
        if (not os.path.exists(transactionFileName)):
            #error.log(transactionFileName + " not found, creating file")
            logger.info(transactionFileName + " not found, creating file")
            file = open(transactionFileName, 'w')
            file.write("Page URL, PageNumber, ComicNumber, Target URL, Original File Name, Saved File Title\n")
            file.close()
    
    i : int
    for i in range(0, pagesToScan): # used for loop as failsafe incase the exit condition doesn't work as inteneded
        if (useCheckpoints):
            check.save()
        datastream = loadWebpage(URLCurrent)
        #error.log("processing webpage (p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "-t" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + ") = \t" + URLCurrent)
        logger.info("processing webpage (p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "-t" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + ") = \t" + URLCurrent)
        
        # This is where the parse Functions are called
        # UserTweak
        ''' # title
        Some reference HTML
        '''
        targetTitle = scrubPath("windows", parseForString(datastream,
                                                          '', # lineStart   inclusive
                                                          '', # lineEnd     inclusive
                                                          '', # targetStart non-inclusive
                                                          '') # targetEnd   non-inclusive
                                )
        
        ''' # next URL
        Some reference HTML
        '''
        URLNext = scrubPath("web", parseForString(datastream,
                                                  '', # lineStart   inclusive
                                                  '', # lineEnd     inclusive
                                                  '', # targetStart non-inclusive
                                                  '') # targetEnd   non-inclusive
                            )
        
        ''' # target
        Some reference HTML
        '''
        targetURL = parseForTargets(datastream,
                                    '', # lineStart   inclusive
                                    '', # lineEnd     inclusive
                                    '', # targetStart non-inclusive
                                    '', # targetEnd   non-inclusive
                                    '', # blockStart  inclusive     optional
                                    '') # blockEnd    inclusive     optional
        
        for i in range(len(targetURL)):
            targetURL[i] = scrubPath("web", targetURL[i])
            
        if (fullArchive):
            ''' # target discription
            Some reference HTML
            '''
            targetDiscription = parseForString(datastream,
                                               '', # lineStart   inclusive
                                               '', # lineEnd     inclusive
                                               '', # targetStart non-inclusive
                                               '') # targetEnd   non-inclusive

        special.trigger(URLCurrent)
        
        # sanity checks
        if (targetTitle == None):
            #error.err("Missing TargetTitle: -1004")
            logger.critical("Missing TargetTitle: -1004")
            exit(-1004)
        if (targetURL == []):
            #error.log("Missing TargetURLs: 1006 (non-fatal)")
            logger.info("Missing TargetURLs: 1006 (non-fatal)")

        sanityCheck()
            
        #error.debug("targetTitle = " + str(targetTitle),
        #            "targetURL = " + str(targetURL),
        #            "URLNext = " + URLNext
        #            )
        logger.debug("targetTitle = " + str(targetTitle))
        logger.debug("targetURL = " + str(targetURL))
        logger.debug("URLNext = " + URLNext)
        
        if (fullArchive):
            saveTarget(URLCurrent, "saved", "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + str(targetTitle), ".html") # saveing html page
            fileTransaction = open(transactionFileName,'a')
            fileTransaction.write(URLCurrent +","+ str(pageNumber) +","+ str(comicNumber) +","+ URLCurrent +","+ URLCurrent +","+ "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + str(targetTitle) + ".html" + "\n")
            fileTransaction.close()
            
            if (targetDiscription != ""):
                if (os.path.exists("saved/" + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + str(targetTitle) + ".txt")):
                    #error.log("File exists, overwriting: " + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + str(targetTitle) + ".txt")
                    logger.info("File exists, overwriting: " + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + str(targetTitle) + ".txt")
                fileDiscription = open("saved/" + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + str(targetTitle) + ".txt", 'wb') # notice this is writing in binary mode
                fileDiscription.write((targetDiscription + "\n").encode('UTF-8')) # encoding it in UTF-8
                fileDiscription.close()
        
        # saves the target(s)
        for j in targetURL:
            saveTarget(j, "saved", "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "]) " + str(targetTitle)) # saving comic image
            if (fullArchive):
                fileTransaction = open(transactionFileName, 'a')
                fileTransaction.write(URLCurrent +","+ str(pageNumber) +","+ str(comicNumber) +","+ j +","+ j[j.rfind("/"):len(j)] + "," + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "]) " + str(targetTitle) + j[j.rfind('.'):len(j)] + "\n")
                fileTransaction.close()
            #error.log("Processing webpage (" + str(pageNumber).zfill(numberWidth) + "); Saving Image (" + str(comicNumber) + ") : " + str(j))
            logger.info("Processing webpage (" + str(pageNumber).zfill(numberWidth) + "); Saving Image (" + str(comicNumber) + ") : " + str(j))
            comicNumber = comicNumber + 1

        #error.debug("Finished processing webpage (" + str(pageNumber).zfill(numberWidth) + ")")   
        logger.debug("Finished processing webpage (" + str(pageNumber).zfill(numberWidth) + ")")     
        if (URLCurrent == URLLast): # check for conclusion of comic
            #error.log("End condition detected, program exit")
            logger.info("End condition detected, program exit")
            exit(0)        
        
        if (URLNext == None): #TODO this check should happen with URLCurrent at the top
            #error.err("Missing URLNext: -1005 (fatal) =>\tURLNext missing, end condition not detected, forceing system exit")
            logger.critical("Missing URLNext: -1005 (fatal) =>\tURLNext missing, end condition not detected, forceing system exit")
            exit(-1005)
        
        # reset and reload
        pageNumber = pageNumber + 1
        URLCurrent = URLNext
        URLNext = None
        targetTitle = ""
        targetURL = None       
        time.sleep(loopDelay)

    #error.log("End Condition: -1009 (Unknown) =>\tPagesToScan reached, program terminating")
    logger.warning("End Condition: -1009 (Unknown) =>\tPagesToScan reached, program terminating")
    exit(-1009)
