'''
Author: Medic5700
Purpose: To archive various webcomics in a local copy
'''
import urllib.request #for url stuff
import time #to sleep
import os #for the filesystem manipulation
import subprocess #used for saving stuff from the web using the system shell commands (if urllib fails)
version = "v4.8.5"

class Debug:
    """Class for logging and debuging"""
    
    def __init__(self, debugMode, file = "ComicArchiver.log"):
        self.__filename = file
        self.showDebug = debugMode #Bool
        
    def __save(self, text):
        """Saves text to file as a log entry"""
        logfile = open(self.__filename, 'a')
        try:
            logfile.write(text)
        except:
            self.err("Error Occured in Error Logging Function: Attempting to report previous error")
            for i in text:
                try:
                    logfile.write(i)
                except:
                    logfile.write("[ERROR]")
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
        
        only writes input to stdout/log file when self.showDebug is True (debugMode was set to true when initialized)"""
        if (self.showDebug):
            temp = "Debug:"
            for i in args:
                temp += "\t" + str(i) + "\n"
            print(temp, end="") #fixes issue where log and sceen output newlines don't match
            self.__save(temp)
    
class SpecialCases:
    """Class for handling special cases triggered by URLCurrent matching a key in the dictionary"""
    
    def __init__(self, specialCases = {}):
        assert (type(specialCases) == type({})),"SpecialCases -> __init__ -> arg1: specialCases needs to be a dictionary"
        
        self.__cases = specialCases
        
    def trigger(self, url):
        """takes URL, if URL in specialCases, executes code"""
        if (url in self.__cases):
            error.log("Special Case detected: " + url)
            try:
                self.__sandbox(self.__cases[url])
            except:
                error.err("SpecialCases->trigger->__sandbox : (-1014) Error while executeing special case")
                exit(-1014)
    
    def __sandbox(self, code):
        """Takes python code as string, runs code within a sandbox"""
        global URLCurrent
        global URLNext
        global targetTitle
        global targetURL
        global comicNumber
        global pageNumber
        
        error.debug("Before executing exec command", 
                    "targetTitle = " + str(targetTitle), 
                    "targetURL = " + str(targetURL), 
                    "URLNext = " + str(URLNext), 
                    "URLCurrent = " + str(URLCurrent),
                    "comicNumber = " + str(comicNumber),
                    "pageNumber = " + str(pageNumber)
                    )
        
        sandboxScope = {"__builtins__":None, 
                        "URLCurrent":URLCurrent, 
                        "URLNext":URLNext, 
                        "targetTitle":targetTitle, 
                        "targetURL":targetURL, 
                        "comicNumber":comicNumber, 
                        "pageNumber":pageNumber
                        }
        error.log("Executing code: \"" + code + "\"")
        exec(code, sandboxScope)
        
        #only changes variables if they have changed
        if (URLCurrent != sandboxScope['URLCurrent']):
            error.debug("changing URLCurrent: " + str(URLCurrent) + " -> " + str(sandboxScope['URLCurrent']))
            if not isinstance(sandboxScope['URLCurrent'], str):
                error.debug("could not change URLCurrent, incorrect type")
            else:
                URLCurrent = sandboxScope['URLCurrent']
        if (URLNext != sandboxScope['URLNext']):
            error.debug("changing URLNext: " + str(URLNext) + " -> " + str(sandboxScope['URLNext']))
            if not isinstance(sandboxScope['URLNext'], str):
                error.debug("could not change URLNext, incorrect type")
            else:
                URLNext = sandboxScope['URLNext']
        if (targetTitle != sandboxScope['targetTitle']):
            error.debug("changing targetTitle: " + str(targetTitle) + " -> " + str(sandboxScope['targetTitle']))
            if not isinstance(sandboxScope['targetTitle'], str):
                error.debug("could not change targetTitle, incorrect type")
            else:
                targetTitle = sandboxScope['targetTitle']
        if (targetURL != sandboxScope['targetURL']):
            error.debug("changing targetURL: " + str(targetURL) + " -> " + str(sandboxScope['targetURL']))
            if (type(targetURL) != type([])):
                error.debug("could not change targetURL, incorrect type")
            else:
                targetURL = sandboxScope['targetURL']
        if (comicNumber != sandboxScope['comicNumber']):
            error.debug("changing comicNumber: " + str(comicNumber) + " -> " + str(sandboxScope['comicNumber']))
            if not isinstance(sandboxScope['comicNumber'], int):
                error.debug("could not change comicNumber, incorrect type")
            else:
                comicNumber = sandboxScope['comicNumber']
        if (pageNumber != sandboxScope['pageNumber']):
            error.debug("changing pageNumber: " + str(pageNumber) + " -> " + str(sandboxScope['pageNumber']))
            if not isinstance(sandboxScope['pageNumber'], int):
                error.debug("could not change pageNumber, incorrect type")
            else:
                pageNumber = sandboxScope['pageNumber']
        
        error.debug("After executing exec command", 
                    "targetTitle = " + str(targetTitle), 
                    "targetURL = " + str(targetURL), 
                    "URLNext = " + str(URLNext), 
                    "URLCurrent = " + str(URLCurrent),
                    "comicNumber = " + str(comicNumber),
                    "pageNumber = " + str(pageNumber)
                    ) 
    
class Checkpoint:
    """Class for loading and saving checkpoints"""
    
    def __init__(self, name = "Checkpoint.csv", checkpointFrequency = 16):
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
        
    def load(self):
        """Loads checkpoint from file, sets URLCurrent, pageNumber, ComicNumber"""
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
        """Saves checkpoint, saves (URLCurrent, pageNumber, comicNumber) on every checkpointFrequency"""
        global URLCurrent
        global pageNumber
        global comicNumber
        
        error.debug("Attempting to save checkpoint")
        if (self.__callsSinceLastCheckpoint == self.__checkpointFrequency - 1):
            file = open(self.filename, 'a')
            file.write(URLCurrent + "," + str(pageNumber) + "," + str(comicNumber) + "\n")
            file.close()
            
            error.log("Checkpoint Saved: " + URLCurrent)
            self.__callsSinceLastCheckpoint = 0
        else:
            self.__callsSinceLastCheckpoint = self.__callsSinceLastCheckpoint + 1
        
def scrubPath(usage, path, dropChar = False):
    """Takes a string, parses it based on usage (windows, web, failsafe, ascii), removes/escapes characters"""
    # http://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid
    acceptableURLCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=" + "%"
    # https://msdn.microsoft.com/en-ca/library/windows/desktop/aa365247(v=vs.85).aspx#naming_conventions
    acceptableWindowsCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 " + "`~!@#$%^&()-=_+[]{};',." #forbidden characters = "<>:/|?*" + "\\\""
    acceptableWindowsCharactersFailSafe = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 " + "~%()-_[]{}."
    
    output = ""
    maxLength = None
    whitelist = ""
    
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
        error.err("scrubPath => argument 2 (usage) invalid: " + str(usage))
        exit(-1015)
    
    for i in path:
        if (i in whitelist):
            output += i
        else:
            if ((not dropChar) and (usage == "ascii")):
                output += ascii(i)
            if (not dropChar):
                output += "%" + str(ord(i))
    
    if (maxLength != None):
        output = output[0 : min(maxLength, len(output))]
    return output

def saveTarget(targetURL, savePath, saveTitle, overrideExtension = None):
    """Takes a URL, filesystem savePath, and a file name (without file extention) => Saves target of the URL at savePath as SaveTitle"""
    #assumes savePath is valid
    error.debug("Attempting to save = " + targetURL)
    
    extension = targetURL[targetURL.rfind('.') : len(targetURL)]
    if (overrideExtension != None):
        extension = overrideExtension
    
    targetObject = None        
    i = 0
    while ((i <= 10) and (targetObject == None)):
        try:
            error.debug("Loading " + targetURL)
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

def saveTarget2(targetURL, savePath, saveTitle, overrideExtension = None):
    """Takes a URL, filesystem savePath, and a file name (without file extention => Saves target of the URL at savePath as SaveTitle
    
    Uses windows powershell instead python's urllib
    """
    
    error.debug("Attempting to save = " + targetURL)
    error.debug("savePath:" + savePath, "saveTitle:" + saveTitle)
    
    extension = targetURL[targetURL.rfind('.') : len(targetURL)]
    if (overrideExtension != None):
        extension = overrideExtension
        
    ''' #Sudo code for powershell command
    Invoke-WebRequest $targetURL -OutFile (savePath + "test.jpg"); 
    mv -literalpath (savePath + "test.jpg") (savePath + saveTitle + extension)
    '''
    try:
        subprocess.check_output(["powershell","Invoke-WebRequest \"" + targetURL + "\" -OutFile \"" + savePath + "/" + "test.jpg" + "\"; mv -literalpath '" + savePath + "/" + "test.jpg" + "' '" + savePath + "/" + saveTitle + extension + "'"])
    except Exception as inst:
        error.err("saveTarget2: (-1015) Error Unable to save target via powershell => " + str(inst))
        exit(-1015)
        
    error.debug("target saved")

def looseDecoder(datastream, blocksize):
    """Takes a webpage data, decodes webpage blocksize at a time, returns string containing webpage data
    
    Some webpages have a couple characters that can't be decoded
    This decodes it in sections to avoid that, enabling most of the webpage to be decoded
    May not fully decode webpage
    """
    assert (blocksize > 2)
    assert (blocksize%2 == 0)
    error.debug("looseDecoder - len(datastream) = " + str(len(datastream)))
    errorCounter = 0
    
    temp = ""
    for i in range(0, int(len(datastream)/blocksize) - 1):
        try:
            temp += datastream[i*blocksize : (i+1)*blocksize].decode('utf-8')
        except Exception as inst:
            errorCounter = errorCounter + 1
            for j in range(0, blocksize):
                temp += " "
    if (errorCounter > 0):
        error.log("LooseDecoder Warning: 1011 (non-fatal) =>\tCould not decode part of webpage, substituting (" + str(errorCounter * blocksize) + ") blanks")
    return temp

def loadWebpage(url):
    """Takes a URL, returns the webpage contents as a string"""
    webpageObject = None
    datasteam = None
    error.debug("Attempting to load webpage " + url)
    i = 0
    while ((i<=10) and (webpageObject == None)):
        try:
            error.debug("Loading " + url)
            webpageObject = urllib.request.urlopen(url)
            #http://stackoverflow.com/questions/2712524/handling-urllib2s-timeout-python #TODO: check if order matters
        except Exception as inst:
            error.log("Connection Fail: 1001 (non-fatal) =>" + "\tAttempt " + str(i) + ":" + str(inst) + ":\t" + str(url))
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
    
    Uses the system command line (powershell) instead of using urllib
    """
    datastream = None
    i = 0
    while ((i<=10) and (datastream == None)):
        try:
            error.debug("Loading " + url)
            datastream = str(    subprocess.check_output(["powershell", "(Invoke-WebRequest \"" + url + "\").Content"])    )
        except Exception as inst:
            error.log("Connection Fail: 1013 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i==10):
            error.err("Coonection Timeout: -1013 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1013)        
        i = i + 1    
        
    error.debug("Webpage loaded")    
    return datastream

def parseForTargets(datastream, lineStart, lineEnd, targetStart, targetEnd, blockStart = "", blockEnd = ""):
    """Takes in a string (webpage HTML), and search peramiters (lineStart, lineEnd, etc), returns an array of targets as strings
    
    (Mainly used to find the URL of picture(s))
    
    
    
    
    
    """
    targets = []
    if (blockStart == "" or blockEnd == ""):
        blockStart = lineStart
        blockEnd = lineEnd
    block = datastream[datastream.find(blockStart) : datastream.find(blockEnd, datastream.find(blockStart)) + len(blockEnd)]
    error.debug("parseTarget - Block = " + str(block))
    while ((lineStart in block) and (lineEnd in block)): #goes through block for each lineStart
        substring = block[block.find(lineStart) : block.find(lineEnd, block.find(lineStart)) + len(lineEnd)]
        error.debug("parseTarget - substring = " + str(substring))
        
        try: #skips substring if targetStart isn't found
            targets.append(   substring[substring.index(targetStart) + len(targetStart) : substring.index(targetEnd, substring.index(targetStart) + len(targetStart))]   )
        except:
            error.debug("praseTarget - Target not found")
            
        block = block[block.find(lineEnd, block.find(lineStart))+len(lineEnd) : ]
        error.debug("parseTarget - found linestart = " + str(lineStart in block), 
                    "parseTarget - found lineEnd = " + str(lineEnd in block), 
                    "parseTarget - len(block) = "+str(len(block)), 
                    "praseTarget - reamining block = " + str(block),
                    "parseTarget - targets = "+str(targets)
                    )      
        
    return targets    

def parseForString(datastream, lineStart, lineEnd, targetStart, targetEnd):
    """Takes in a string (webpage HTML) and search paramiters (lineStart, lineEnd, etc), returns a string found
        
    returns the empty string "" if target is not found"""
    try:
        substring = datastream[datastream.index(lineStart) : datastream.index(lineEnd, datastream.index(lineStart)) + len(lineEnd)]
        return substring[substring.index(targetStart) + len(targetStart) : substring.index(targetEnd, substring.index(targetStart) + len(targetStart))]
    except:
        error.debug("parseForString => Search Failed")
        return ""    
    
if __name__ == '__main__':
    #These options need to be configured
    comicName       = "Comic Name"
    URLStart        = "Start URL" #The url to start from
    URLLast         = "End URL" #the last url in the comic series, to tell the program exactly where to stop
    pagesToScan     = 9999 #Maximum number of pages that this program will scan in one go
    debugMode       = False
    useCheckpoints  = False
    fullArchive     = False #saves the aditional information from webpage
    
    #Other program options
    cases           = {} #a dictionary for special cases, with keys being the current URL to trigger them, and the value being a string of python code to execute (still figuring out the security on that one)
    numberWidth     = 4 #the number of digits used to index comics
    loopDelay       = 0 #time in seconds
    transactionFileName = "ComicArchiver-Transactions.csv"
    
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

    special = SpecialCases(cases) #Initialize the SpecialCases Class
    if (useCheckpoints):
        error.log("Checkpoints Enabled")
        check = Checkpoint("ComicArchiver-Checkpoint.csv",16) #Initialize the Checkpoint Class
        check.load()

    if not (os.path.exists("./saved/")): #create folder if it doesn't exsist
        error.log("Creating directory:\t" + "./saved/")
        os.makedirs("./saved/")
    
    if (fullArchive):
        if (not os.path.exists(transactionFileName)):
            error.log(transactionFileName + " not found, creating file")
            file = open(transactionFileName, 'w')
            file.write("Page URL, PageNumber, ComicNumber, Target URL, Original File Name, Saved File Title\n")
            file.close()
    
    for i in range (0, pagesToScan): #used for loop as failsafe incase the exit condition doesn't work as inteneded
        if (useCheckpoints):
            check.save()
        datastream = loadWebpage(URLCurrent)
        error.log("processing webpage (p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "-t" + (('{:0>' + str(numberWidth) + '}').format(comicNumber)) + ") = \t" + URLCurrent)
        
        #This is where the parse Functions are called
        #UserTweak
        ''' #title
        Some reference HTML
        '''
        targetTitle = scrubPath("windows", parseForString(datastream,
                                                          '',
                                                          '',
                                                          '',
                                                          '')
                                )
        ''' #next URL
        Some reference HTML
        '''
        URLNext = scrubPath("web", parseForString(datastream,
                                                  '',
                                                  '', # lineEnd
                                                  '',
                                                  '')
                            )        
        ''' #target
        Some reference HTML
        '''
        targetURL = parseForTargets(datastream,
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '')
        for i in range(len(targetURL)):
            targetURL[i] = scrubPath("web", targetURL[i])
            
        if (fullArchive):
            ''' #target discription
            Some reference HTML
            '''
            targetDiscription = parseForString(datastream,
                                               '',
                                               '',
                                               '',
                                               '')

        special.trigger(URLCurrent)

        if (targetTitle == None):
            error.err("Missing Target: -1004")
            exit(-1004)
        if (targetURL == []):
            error.log("Missing TargetURLs: 1006 (non-fatal)")
            
        error.debug("targetTitle = " + targetTitle, 
                    "targetURL = " + str(targetURL), 
                    "URLNext = " + URLNext
                    )
        
        if (fullArchive):
            saveTarget(URLCurrent, "saved", "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + targetTitle, ".html") #saveing html page
            fileTransaction = open(transactionFileName,'a')
            fileTransaction.write(URLCurrent +","+ str(pageNumber) +","+ str(comicNumber) +","+ URLCurrent +","+ URLCurrent +","+ "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + targetTitle + ".html" + "\n")
            fileTransaction.close()
            
            if (targetDiscription != ""):
                if (os.path.exists("saved/" + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + targetTitle + ".txt")):
                    error.log("File exists, overwriting: " + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + targetTitle + ".txt")
                fileDiscription = open("saved/" + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "-p" + str(pageNumber).zfill(numberWidth) + "]) " + targetTitle + ".txt", 'w')
                fileDiscription.write(targetDiscription + "\n")
                fileDiscription.close()
        
        #saves the target(s)
        for j in targetURL:
            saveTarget(j, "saved", "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "]) " + targetTitle) #saving comic image
            if (fullArchive):
                fileTransaction = open(transactionFileName, 'a')
                fileTransaction.write(URLCurrent +","+ str(pageNumber) +","+ str(comicNumber) +","+ j +","+ j[j.rfind("/"):len(j)] + "," + "(" + comicName + " [" + str(comicNumber).zfill(numberWidth) + "]) " + targetTitle + j[j.rfind('.'):len(j)] + "\n")
                fileTransaction.close()                
            comicNumber = comicNumber + 1

        error.debug("Finished processing webpage (" + str(pageNumber).zfill(numberWidth) + ")")        
        if (URLCurrent == URLLast): #check for conclusion of comic
            error.log("End condition detected, program exit")
            exit(0)        
        
        if (URLNext == None): #TODO this check should happen with URLCurrent at the top
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
