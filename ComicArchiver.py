'''
Author: Medic5700
Purpose: To archive various webcomics in a local copy
'''
import urllib.request #for url stuff
import time #to sleep
import os #for the filesystem manipulation
version = "v4.8.1" #I know it's not proper coding to put a variable here, but here is where it makes sense?

class Debug:
    #Class for logging and debuging
    #required to be initalized below the declaration for global variables
    def __init__(self, debugMode, file="ComicArchiver.log"):
        self.__filename = file
        self.showDebug = debugMode #Bool
        
    def __save(self, text):
        logfile = open(self.__filename, 'a')
        logfile.write(text)
        logfile.close()

    def log(self, text):
        #pushes text to stdout AND to the log file
        temp = "[" + time.asctime() + "] Log: " + text
        print(temp)
        self.__save(temp + "\n")
    
    def err(self, text):
        #The same as log, but meant to be used for program crashing errors
        temp = "[" + time.asctime() + "] ERR: " + text
        print(temp)
        self.__save(temp + "\n")        
    
    def debug(self, *args):
        #pushes text to stdout AND to the log file, takes as many arguments as needed
        if (self.showDebug):
            temp = "Debug:"
            for i in args:
                temp += "\t" + str(i) + "\n"
            print(temp)
            self.__save(temp)
    
class SpecialCases:
    #Class for handling special cases triggered by URLCurrent matching a key in the dictionary
    def __init__(self, specialCases={}):
        assert (type(specialCases) == type({})),"SpecialCases -> __init__ -> arg1: specialCases needs to be a dictionary"
        self.__cases = specialCases
        
    def trigger(self, url):
        #This determins if the current page is a special case
        if (url in self.__cases):
            error.log("Special Case detected: " + url)
            self.__sandbox(self.cases[url])
    
    def __sandbox(self, code):
        #A sandbox to run exec in with limited access to the rest of the program, still not the most secure, but more secure then nothing
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
    #Class for loading and saving checkpoints
    def __init__(self,name="Checkpoint.csv",checkpointFrequency=16):
        global URLCurrent
        global pageNumber
        global comicNumber        
        assert (checkpointFrequency>0),"Checkpoint -> __init__ -> arg2: checkpointFrequency needs to be greater then 0"
        self.filename = name
        self.__checkpointFrequency = checkpointFrequency
        self.__callsSinceLastCheckpoint = 0
        if not (os.path.exists(self.filename)):
            error.log("Creating checkpoint file")
            file = open(self.filename,'w')
            file.write("URLCurrent,pageNumber,comicNumber\n")
            file.write(URLCurrent + "," + str(pageNumber) + "," + str(comicNumber) + "\n")
            file.close()
        
    def load(self):
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
    #should not be needed
    #takes a string, removes non-windows file system friendly chars, and converts them, and returns the string
    # http://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid
    unacceptableCharacters = " "
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
    #takes a string, removes and converts non-windows file system friendly chars OR unicod chars OR chars in the extanded ascii table, and returns the string
    t1 = list(inlist)
    #acceptableCharacters = " ()[]{}.-%#0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    unacceptableCharacters = "\\/:*?\"<>|"
    
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

def saveTarget (targetURL, savepath, saveTitle, overrideExtension=None):
    #assumes savepath is valid
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
        if (i == 10): #FAILSAFE
            error.err("Picture Load Timeout: -1008 (fatal) =>\tFailed to load picture, Forcing system exit")
            exit(-1008)
        time.sleep(4)  
        i = i+1

    try:
        if (os.path.exists(savepath + "/" + saveTitle + extension)): #checks if file exists
            error.log("File exists: 1012 (non-fatal) => \tOverwriting existing file: \t" + savepath + "/" + saveTitle + extension)
        fileObject = open(savepath + "/" + saveTitle + extension, 'wb')
        fileObject.write(targetObject.read())
        fileObject.close()
    except Exception as inst:
        error.err("Picture failed to save: -1010 (fatal) =>\tSaveTitle:" + saveTitle + "\tExtension:" + extension + "\tError =>\t" + str(inst))
        exit(-1010)
    
    error.debug("target saved")
    targetObject.close()

def looseDecoder(datastream, blocksize):
    #a loose webpage decoder, converts blocks of text at a time incase a couple characters are not decodable.
    #may not fully decode webpage (IE: the very last characters of a webpage)
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
    #gets and decodes webpage
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
        #supertemp = (webpageObject.read()).decode('utf-8')
    except Exception as inst:
        error.err("Decode Error: -1003 (fatal) =>" + "\tUTF-8 decode error, Force System Exit =>\t" + str(inst))
        exit(-1003)  
    webpageObject.close()
    error.debug("Webpage loaded")
    return datastream

def loadWebpage2(url):
    #an alternate way to load webpages via powershell?
    datastream = None
    i = 0
    while ((i<=10) and (webpageObject == None)):
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
    
def parseTitle(datastream):
    #find the target title
    #TODO: decide wheather to scrube targetTitle AND replace the forward slashes with a dot (for when titles are just the date)[probibly should make a function to do just that]
    '''
    Some HTML code
    '''
    #UserTweek
    lineStart = "" #inclusive
    lineEnd = "" #inclusive
    targetStart = "" #non-inclusive
    targetEnd = "" #non-inclusive
    
    substring = datastream[datastream.find(lineStart):datastream.find(lineEnd, datastream.find(lineStart))+len(lineEnd)]
    return scrubTitle(   substring[substring.find(targetStart)+len(targetStart):substring.find(targetEnd, substring.find(targetStart)+len(targetStart))]   )

def parseTarget(datastream):
    #find the target (picture) URL
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
    while (block.find(lineStart) != -1):
        substring = block[block.find(lineStart):block.find(lineEnd, block.find(lineStart))+len(lineEnd)]
        
        targets.append(scrubURL(   substring[substring.find(targetStart)+len(targetStart):substring.find(targetEnd, substring.find(targetStart)+len(targetStart))]   ))
        block = block[block.find(lineEnd, block.find(lineStart))+len(lineEnd) : -1]
        error.debug("parseTarget - found linestart = " + str(block.find(lineStart) != -1), "parseTarget - len(block) = "+str(len(block)), "parseTarget - targets = "+str(targets))        

    return targets

def parseURLNext(datastream):
    #finds URL of the next webpage (if needed)
    '''
    Some HTML code
    '''
    #UserTweek
    lineStart = "" #inclusive
    lineEnd = "" #inclusive
    targetStart = "" #non-inclusive
    targetEnd = "" #non-inclusive
    
    substring = datastream[datastream.find(lineStart):datastream.find(lineEnd, datastream.find(lineStart))+len(lineEnd)]
    return scrubURL(   substring[substring.find(targetStart)+len(targetStart):substring.find(targetEnd, substring.find(targetStart)+len(targetStart))]   )    
    
if __name__ == '__main__':
    #some prgrame options
    #UserTweek
    savewebpage     = False
    loopDelay       = 1 #time in seconds
    pagesToScan     = 10000 #number of pages that this program will scan
    debugMode       = False
    useCheckpoints  = False
    
    #UserTweek
    comicName       = "Comic Name"
    URLStart        = "Start URL" #The url to start from
    URLLast         = "End URL" #the last url in the comic series, to tell the program exactly where to stop
    
    cases           = {} #a dictionary for special cases, with keys being the current URL to trigger them, and the value being a string of python code to execute (still figuring out the security on that one)
    
    numberWidth     = 4 #the number of digits used to index comics
    
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

    error = Debug(debugMode, "ComicArchiver.log") #Initialize the logging class
    error.log("Comic Archiver has started, Version: " + version + " ==================================================")    
    if (debugMode):
        error.log("Debug logging is enabled")
        
    special = SpecialCases(cases)
    
    if (useCheckpoints):
        error.log("Checkpoints Enabled")
        check = Checkpoint("Checkpoint.csv",16)
        check.load()    

    #create folder if it doesn't exsist
    if not (os.path.exists("./saved/")):
        error.log("Creating directory:\t" + "./saved/")
        os.makedirs("./saved/")
    
    for i in range (0, pagesToScan): #used for loop as failsafe incase the exit condition doesn't work as inteneded
        if (useCheckpoints):
            check.save()
        
        datastream = loadWebpage(URLCurrent)
        error.log("processing webpage (p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "-t" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + ") = \t" + URLCurrent)
        
        targetTitle = parseTitle(datastream)
        targetURL = parseTarget(datastream)
        URLNext = parseURLNext(datastream)

        special.trigger(URLCurrent)

        if (targetTitle == None):
            error.err("Missing Target: -1004")
            exit(-1004)
        if (targetURL == None):
            error.err("Missing TargetURL: -1006")
            exit(-1006)
            
        error.debug("targetTitle = "+targetTitle, "targetURL = "+str(targetURL), "URLNext = "+URLNext)
            
        #saves the target(s)
        if savewebpage == True:
            saveTarget(URLCurrent, "saved/", "(" + comicName + " [" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + "-p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "]) " + targetTitle, ".html") #saveing html page        
        for j in targetURL:
            saveTarget(j, "saved/", "(" + comicName + " [" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + "]) " + targetTitle) #saving comic image
            '''
            names = open("Names.csv",'a')
            names.write(j + "," + j[j.find("comics")+7:len(j)] + "," + "(" + comicName + " [" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + "]) " + targetTitle + j[j.rfind('.'):len(j)] +"\n")
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
    