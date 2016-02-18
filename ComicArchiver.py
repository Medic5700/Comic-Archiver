'''
Author: Medic5700
Purpose: To archive various webcomics in a local copy
'''
import urllib.request #for url stuff
import time #to sleep
import os #for the filesystem manipulation
import subprocess #used for saving stuff from the web using the system shell commands (if urllib fails)
version = "v4.8.4" #I know it's not proper coding to put a variable here, but here is where it makes sense?

class Debug:
    """Class for logging and debuging"""
    def __init__(self, debugMode, file="ComicArchiver.log"):
        self.__filename = file
        self.showDebug = debugMode #Bool
        
    def __save(self, text):
        """Function to save each log entry"""
        logfile = open(self.__filename, 'a')
        logfile.write(text)
        logfile.close()

    def log(self, text):
        """Takes string, pushes to stdout AND saves it to the log file
        
        For general logging, and non-fatal errors
        """
        temp = "[" + time.asctime() + "] Log: " + text
        print(temp)
        self.__save(temp + "\n")
    
    def err(self, text):
        """Takes string, pushes to stdout and saves it to the log file
        
        Mainly meant for non-recoverable errors that should cause the program to terminate"""
        temp = "[" + time.asctime() + "] ERR: " + text
        print(temp)
        self.__save(temp + "\n")        
    
    def debug(self, *args):
        """takes n number of strings, pushes to stdout and log file
        
        only writes input to stdout/log file when showDebug is True"""
        if (self.showDebug):
            temp = "Debug:"
            for i in args:
                temp += "\t" + str(i) + "\n"
            print(temp, end="") #fixes issue where log and sceen output newlines don't match
            self.__save(temp)
    
class SpecialCases:
    """Class for handling special cases triggered by URLCurrent matching a key in the dictionary"""
    
    def __init__(self, specialCases={}):
        assert (type(specialCases) == type({})),"SpecialCases -> __init__ -> arg1: specialCases needs to be a dictionary"
        self.__cases = specialCases
        
    def trigger(self, url):
        """takes URL, if URL in specialCases, executes code"""
        if (url in self.__cases):
            error.log("Special Case detected: " + url)
            self.__sandbox(self.__cases[url])
    
    def __sandbox(self, code):
        """Takes python code as string, runs code within a sandbox"""
        global URLCurrent
        global URLNext
        global targetTitle
        global targetURL
        error.debug("Before executing exec command","targetTitle = "+targetTitle, "targetURL = "+str(targetURL), "URLNext = "+URLNext, "URLCurrent = "+URLCurrent)
        
        sandboxScope = {"__builtins__":None,"URLCurrent":URLCurrent,"URLNext":URLNext,"targetTitle":targetTitle,"targetURL":targetURL}
        error.log("Executing code: \"" + code + "\"")
        exec(code, sandboxScope)
        URLCurrent = sandboxScope['URLCurrent']
        URLNext = sandboxScope['URLNext']
        targetTitle = sandboxScope['targetTitle']
        targetURL = sandboxScope['targetURL']
        
        error.debug("After executing exec command","targetTitle = "+targetTitle, "targetURL = "+str(targetURL), "URLNext = "+URLNext, "URLCurrent = "+URLCurrent)
        #TODO: Assert variables are the right type, only change variables if they change  
    
class Checkpoint:
    """Class for loading and saving checkpoints"""
    def __init__(self,name="Checkpoint.csv",checkpointFrequency=16):
        global URLCurrent
        global pageNumber
        global comicNumber        
        assert (checkpointFrequency>0),"Checkpoint -> __init__ -> arg2: checkpointFrequency needs to be greater then 0"
        self.filename = name
        self.__checkpointFrequency = checkpointFrequency
        self.__callsSinceLastCheckpoint = 0
        if not (os.path.exists(self.filename)):
            error.log("Checkpoint file not found, creating checkpoint file")
            file = open(self.filename,'w')
            file.write("URLCurrent,pageNumber,comicNumber\n")
            file.write(URLCurrent + "," + str(pageNumber) + "," + str(comicNumber) + "\n")
            file.close()
        #TODO: should return true/false if checkpoint file is created?
        
    def load(self):
        """Loads checkpoint"""
        global URLCurrent
        global pageNumber
        global comicNumber
        
        error.debug("Attempting to load checkpoint")
        raw = None
        try:
            file = open(self.filename, 'r')
            raw = file.read().split('\n')
            file.close()
        except Exception as exception:
            error.err("Could not load checkpoint file: " + self.filename)
        
        try:
            line = raw[len(raw)-2]
            error.debug("line: " + str(line))
            
            URLCurrent = (line.split(','))[0]
            pageNumber = int((line.split(','))[1])
            comicNumber = int((line.split(','))[2])
            error.log("Checkpoint Loaded: " + URLCurrent)
        except Exception as exception:
            error.err("Checkpoint file not formated correctly: " + self.filename)
        
    def save(self):
        """Saves checkpoint, saves on intervales"""
        global URLCurrent
        global pageNumber
        global comicNumber
        
        if(self.__callsSinceLastCheckpoint == self.__checkpointFrequency - 1):
            file = open(self.filename, 'a')
            file.write(URLCurrent + "," + str(pageNumber) + "," + str(comicNumber) + "\n")
            file.close()
            
            error.log("Checkpoint Saved: " + URLCurrent)
            self.__callsSinceLastCheckpoint = 0
        else:
            self.__callsSinceLastCheckpoint = self.__callsSinceLastCheckpoint + 1
        
def scrubURL(inlist):
    """Takes a URL as a string, returns a string that has unacceptableCharacters converted"""
    # http://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid
    unacceptableCharacters = " "
    acceptableCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="
    t1 = list(inlist)
    
    j=0
    while (j<len(t1)):
        if (unacceptableCharacters.find(str(t1[j]))!=-1):
            t1.insert(j+1,"%" + str(ord(t1[j])))
            t1.pop(j)
            error.log("scrubURL Warning: needed to replace a character in URL: " + inlist + "\n")
        j=j+1
    t2 = "".join(t1)    
    return t2

def scrubTitle(inlist):
    """Takes a string, returns a string with windows file system unfriendly characters scrubbed"""
    t1 = list(inlist)
    #acceptableCharacters = " ()[]{}.-%#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    unacceptableCharacters = "\\/:*?\"<>|\t\n"
    
    j=0
    while (j<len(t1)):
        if (unacceptableCharacters.find(str(t1[j]))!=-1):
            t1.insert(j+1,"%" + str(ord(t1[j])))
            t1.pop(j)
            error.debug("scrubTitle: Warning: needed to replace a character in target Title: " + inlist)
        j=j+1
    t2 = "".join(t1)
    
    if (len(t2) > 80):
        return t2[0:80]
    return t2

def saveTarget(targetURL, savePath, saveTitle, overrideExtension=None):
    """Takes a URL, filesystem savePath, and a file name (without file extention => Saves target of the URL at savePath as SaveTitle"""
    #assumes savePath is valid
    error.debug("Attempting to save = " + targetURL)
    
    extension = targetURL[targetURL.rfind('.'):len(targetURL)]
    if (overrideExtension != None):
        extension = overrideExtension
    
    targetObject = None        
    i = 0
    while ((i<=10) and (targetObject == None)):
        try:
            error.debug("Loading "+targetURL)
            targetObject = (urllib.request.urlopen(targetURL))
        except Exception as inst: #handles timeout I think
            error.log("Connection Fail: 1007 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(targetURL))
            time.sleep(4)  
        if (i == 10): #FAILSAFE
            error.err("Picture Load Timeout: -1008 (fatal) =>\tFailed to load picture, Forcing system exit")
            exit(-1008)
        i = i+1

    try:
        if (os.path.exists(savePath + "/" + saveTitle + extension)): #checks if file exists
            error.log("File exists: 1012 (non-fatal) => \tOverwriting existing file: \t" + savePath + "/" + saveTitle + extension)
        fileObject = open(savePath + "/" + saveTitle + extension, 'wb')
        fileObject.write(targetObject.read())
        fileObject.close()
    except Exception as inst:
        error.err("Picture failed to save: -1010 (fatal) =>\tSaveTitle:" + saveTitle + "\tExtension:" + extension + "\tError =>\t" + str(inst))
        exit(-1010)
    
    error.debug("target saved")
    targetObject.close()

def saveTarget2(targetURL, savePath, saveTitle, overrideExtension=None):
    """Takes a URL, filesystem savePath, and a file name (without file extention => Saves target of the URL at savePath as SaveTitle
    
    Uses windows powershell instead python's urllib"""
    
    error.debug("Attempting to save = " + targetURL)
    error.debug("savePath:" + savePath, "saveTitle:" + saveTitle)
    
    extension = targetURL[targetURL.rfind('.'):len(targetURL)]
    if (overrideExtension != None):
        extension = overrideExtension
    ''' #Sudo code for powershell command
    Invoke-WebRequest $targetURL -OutFile (savePath + "test.jpg"); mv -literalpath (savePath + "test.jpg") (savePath + saveTitle + extension)
    '''
    subprocess.check_output(["powershell","Invoke-WebRequest \""+targetURL+"\" -OutFile \"" + savePath + "test.jpg" + "\"; mv -literalpath '" + savePath + "test.jpg" + "' '" + savePath + saveTitle + extension + "'"])
    error.debug("target saved")
    #TODO: Error Handling

def looseDecoder(datastream, blocksize):
    """Takes a webpage data, decodes webpage blocksize at a time, returns string containing webpage data
    
    Some webpages have a couple characters that can't be decoded
    This decodes it in sections to avoid, enabling most of the webpage to be decoded
    May not fully decode webpage"""
    assert (blocksize > 2)
    assert (blocksize%2==0)
    error.debug("looseDecoder - len(datastream) = "+str(len(datastream)))
    temp = ""
    errorCounter = 0
    for i in range(0,int(len(datastream)/blocksize)-1):
        try:
            temp += datastream[i*blocksize:(i+1)*blocksize].decode('utf-8')
        except Exception as inst:
            errorCounter = errorCounter + 1
            for j in range(0,blocksize):
                temp += " "
            error.debug("looaseDecoder - decode warning, substituting block")
    if (errorCounter > 0):
        error.log("LooseDecoder Warning: 1011 (non-fatal) =>\tCould not decode part of webpage, substituting ("+str(errorCounter * blocksize)+ ") blanks")
    return temp

def loadWebpage(url):
    """Takes a URL, returns the webpage contents as a string"""
    webpageObject = None
    datasteam = None
    error.debug("Attempting to load webpage " + url)
    i = 0
    while ((i<=10) and (webpageObject == None)):
        try:
            error.debug("Loading "+url)
            webpageObject = urllib.request.urlopen(url)
            #http://stackoverflow.com/questions/2712524/handling-urllib2s-timeout-python #TODO: check if order matters
        except Exception as inst:
            error.log("Connection Fail: 1001 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i==10):
            error.err("Coonection Timeout: -1001 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1001)        
        i = i+1
    try:
        error.debug("Decoding webpage")
        datastream = looseDecoder(webpageObject.read(),4) #may help for webpages that seem to have one bad character
    except Exception as inst:
        error.err("Decode Error: -1003 (fatal) =>" + "\tUTF-8 decode error, Force System Exit =>\t" + str(inst))
        exit(-1003)  
    webpageObject.close()
    error.debug("Webpage loaded")
    return datastream

def loadWebpage2(url):
    """Takes a URL, returns the webpage contents as a string
    
    Uses the system command line (powershell) instead of using urllib"""
    datastream = None
    i = 0
    while ((i<=10) and (datastream == None)):
        try:
            error.debug("Loading "+url)
            datastream = str(    subprocess.check_output(["powershell","(Invoke-WebRequest \""+url+"\").Content"])    )
        except Exception as inst:
            error.log("Connection Fail: 1013 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i==10):
            error.err("Coonection Timeout: -1013 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1013)        
        i = i+1    
        
    error.debug("Webpage loaded")    
    return datastream
    
def parseTarget(datastream):
    """Takes in a string (webpage HTML), returns the target URL in an array of strings
    
    Used to find the URL of a picture"""
    '''
    Some HTML code
    '''
    #UserTweek
    blockStart = "" #inclusive, optional
    blockEnd = "" #inclusive, optional
    lineStart = "" #inclusive
    lineEnd = "" #inclusive
    targetStart = "" #non-inclusive
    targetEnd = "" #non-inclusive
    
    targets = []
    if (blockStart == "" or blockEnd == ""):
        blockStart = lineStart
        blockEnd = lineEnd
    block = datastream[datastream.find(blockStart):datastream.find(blockEnd, datastream.find(blockStart))+len(blockEnd)]
    error.debug("parseTarget - Block = " + str(block))
    while ((lineStart in block) and (lineEnd in block)): #goes through block for each lineStart
        substring = block[block.find(lineStart):block.find(lineEnd, block.find(lineStart))+len(lineEnd)]
        error.debug("parseTarget - substring = " + str(substring))
        
        try: #skips substring if targetStart isn't found
            targets.append(   substring[substring.index(targetStart)+len(targetStart):substring.index(targetEnd, substring.index(targetStart)+len(targetStart))]   )
            #error.debug("parseTarget - Target Found")
        except:
            error.debug("praseTarget - Target not found")
            
        block = block[block.find(lineEnd, block.find(lineStart))+len(lineEnd) : -1]
        error.debug("parseTarget - found linestart = " + str(block.find(lineStart) != -1), "parseTarget - len(block) = "+str(len(block)), "parseTarget - targets = "+str(targets))        
        
    return targets

def parseTitle(datastream):
    """Takes in a string (webpage HTML), returns the title as a string
    
    returns "" if title not found"""
    '''
    Some HTML code
    '''
    #UserTweek
    lineStart = "" #inclusive
    lineEnd = "" #inclusive
    targetStart = "" #non-inclusive
    targetEnd = "" #non-inclusive
    
    try:
        substring = datastream[datastream.index(lineStart):datastream.index(lineEnd, datastream.index(lineStart))+len(lineEnd)]
        return substring[substring.index(targetStart)+len(targetStart):substring.index(targetEnd, substring.index(targetStart)+len(targetStart))]
    except:
        error.debug("parseTitle => Title not found, returning \"\"")
        return ""

def parseDescription(datastream):
    """Takes in a string (webpage HTML), returns description as string
    
    returns "" if description not found"""
    '''
    Some HTML code
    '''
    #UserTweek
    lineStart = "" #inclusive
    lineEnd = "" #inclusive
    targetStart = "" #non-inclusive
    targetEnd = "" #non-inclusive
    
    try:
        substring = datastream[datastream.index(lineStart):datastream.index(lineEnd, datastream.index(lineStart))+len(lineEnd)]
        return substring[substring.index(targetStart)+len(targetStart):substring.index(targetEnd, substring.index(targetStart)+len(targetStart))]
    except:
        error.debug("parseDescription => target not found, returning \"\"")
        return ""

def parseURLNext(datastream):
    """Takes in a string (webpage HTML), returns the URL representing the next button as a string
    
    returns "" if next URL not found"""
    '''
    Some HTML code
    '''
    #UserTweek
    lineStart = "" #inclusive
    lineEnd = "" #inclusive
    targetStart = "" #non-inclusive
    targetEnd = "" #non-inclusive
    
    try:
        substring = datastream[datastream.index(lineStart):datastream.index(lineEnd, datastream.index(lineStart))+len(lineEnd)]
        return substring[substring.index(targetStart)+len(targetStart):substring.index(targetEnd, substring.index(targetStart)+len(targetStart))]
    except:
        error.debug("parseURLNext => Next URL not found")
        return ""
    
if __name__ == '__main__':
    #These options need to be configured
    comicName       = "Comic Name"
    URLStart        = "Start URL" #The url to start from
    URLLast         = "End URL" #the last url in the comic series, to tell the program exactly where to stop
    pagesToScan     = 9999 #Maximum number of pages that this program will scan in one go
    debugMode       = False
    useCheckpoints  = False
    savewebpage     = False #saves the HTML of the webpage
    
    #Other program options
    cases           = {} #a dictionary for special cases, with keys being the current URL to trigger them, and the value being a string of python code to execute (still figuring out the security on that one)    
    numberWidth     = 4 #the number of digits used to index comics
    loopDelay       = 0 #time in seconds
    
    
    error = Debug(debugMode, "ComicArchiver.log") #Initialize the Logging Class
    error.log("Comic Archiver has started, Version: " + version + " ==================================================")    
    if (debugMode):
        error.log("Debug logging is enabled")
        
    #Global variables for parsing webpages
    URLCurrent = URLStart
    URLNext = None
    targetTitle = None
    targetURL = None
    comicNumber = 1
    pageNumber = 1
    
    '''
    names = open("Names.csv",'w')
    names.write("URL,NAME,TITLE\n")
    names.close()
    '''

    special = SpecialCases(cases) #Initialize the SpecialCases Class
    if (useCheckpoints):
        error.log("Checkpoints Enabled")
        check = Checkpoint("ComicArchiver-Checkpoint.csv",16) #Initialize the Checkpoint Class
        check.load()    
    if not (os.path.exists("./saved/")): #create folder if it doesn't exsist
        error.log("Creating directory:\t" + "./saved/")
        os.makedirs("./saved/")
    
    for i in range (0, pagesToScan): #used for loop as failsafe incase the exit condition doesn't work as inteneded
        if (useCheckpoints):
            check.save()
        datastream = loadWebpage(URLCurrent)
        error.log("processing webpage (p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "-t" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + ") = \t" + URLCurrent)
        
        #This is where the parse Functions are called
        targetTitle = scrubTitle( parseTitle(datastream) )
        targetURL = parseTarget(datastream)
        for i in range(len(targetURL)):
            targetURL[i] = scrubURL(targetURL[i])        
        URLNext = scrubURL( parseURLNext(datastream) )

        special.trigger(URLCurrent)

        if (targetTitle == None):
            error.err("Missing Target: -1004")
            exit(-1004)
        if (targetURL == []):
            error.log("Missing TargetURLs: 1006 (non-fatal)")
            
        error.debug("targetTitle = "+targetTitle, "targetURL = "+str(targetURL), "URLNext = "+URLNext)
            
        #saves the target(s)
        if savewebpage == True:
            saveTarget(URLCurrent, "saved/", "(" + comicName + " [" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + "-p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "]) " + targetTitle, ".html") #saveing html page        
        for j in targetURL:
            saveTarget(j, "saved/", "(" + comicName + " [" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + "]) " + targetTitle) #saving comic image
            '''
            names = open("Names.csv",'a')
            names.write(j + "," + j[j.rfind("/"):len(j)] + "," + "(" + comicName + " [" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + "]) " + targetTitle + j[j.rfind('.'):len(j)] +"\n")
            names.close()
            '''
            comicNumber = comicNumber + 1

        error.debug("Finished processing webpage (" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + ")")        
        if URLCurrent == URLLast: #check for conclusion of comic
            error.log("End condition detected, program exit")
            exit(0)        
        
        if URLNext == None: #TODO this check should happen with URLCurrent at the top
            error.err("Missing URLNext: -1005 (fatal) =>\tURLNext missing, end condition not detected, forceing system exit")
            exit(-1005)
        #reset and reload
        pageNumber = pageNumber + 1
        URLCurrent = URLNext
        URLNext = None
        targetTitle = None
        targetURL = None       
        time.sleep(loopDelay)

    error.log("End Condition: -1009 (Unknown) =>\tPagesToScan reached, program terminating")
    exit(-1009)
    