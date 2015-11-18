'''
Author: Medic5700
Purpose: To archive various comics in a local copy
'''
import urllib.request #for url stuff
import time #to sleep
import os #for the folder manipulation
version = "v4.7" #I know it's not proper coding to put a variable here, but here is where it makes sense?

class Debug:
    #Used for logging and debuging
    def __init__(self):
        self.message = ""
        
    def save(self):
        logfile = open("Debug.log", 'a')
        logfile.write(self.message)
        logfile.close()

    def log(self, text):
        #pushes text to stdout AND to the log file
        temp = "[" + time.asctime() + "] Log: " + text
        print(temp)
        self.message = temp + "\n"
        self.save()
    
    def debug(self, *args):
        #pushes text to stdout AND to the log file, takes as many arguments as needed
        temp = "Debug:\n"
        for i in args:
            temp += "\t" + str(i) + "\n"
        print(temp)
        self.message = temp
        self.save()
    
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
            if (debug):
                error.debug("scrubTitle: Warning: needed to replace a character in target Title: " + inlist)
        j=j+1
    t2 = "".join(t1)
    
    if (len(t2) > 80):
        return t2[0:80]
    return t2

def saveTarget (targetURL, savepath, saveTitle, overrideExtension=None):
    #assumes savepath is valid
    if (debug):
        error.debug("Attempting to save = " + targetURL)
    
    extension = targetURL[targetURL.rfind('.'):len(targetURL)]
    if (overrideExtension != None):
        extension = overrideExtension
    
    targetObject = None        
    i = 0
    while ((i<=10) and (targetObject == None)):
        try:
            if (debug):
                error.debug("Loading "+targetURL)
            targetObject = (urllib.request.urlopen(targetURL))
        except Exception as inst: #handles timeout I think
            error.log("Connection Fail: 1007 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(targetURL))
        if (i == 10): #FAILSAFE
            error.log("Picture Load Timeout: -1008 (fatal) =>\tFailed to load picture, Forcing system exit")
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
        error.log("Picture failed to save: -1010 (fatal) =>\tSaveTitle:" + saveTitle + "\tExtension:" + extension + "\tError =>\t" + str(inst))
        exit(-1010)
    
    if (debug):
        error.debug("target saved")
    targetObject.close()

def looseDecoder(datastream, blocksize):
    #a loose webpage decoder, converts blocks of text at a time incase a couple characters are not decodable.
    #may not fully decode webpage (IE: the very last characters of a webpage)
    assert (blocksize > 2)
    assert (blocksize%2==0)
    if (debug):
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
            if (debug):
                error.debug("looaseDecoder - decode warning, substituting block")
    if (errorCounter > 0):
        error.log("LooseDecoder Warning: 1011 (non-fatal) =>\tCould not decode part of webpage, substituting ("+str(errorCounter * blocksize)+ ") blanks")
    return temp

def loadWebpage(url):
    #gets and decodes webpage
    webpageObject = None
    datasteam = None
    if (debug):
        error.debug("Attempting to load webpage " + url)
    i = 0
    while ((i<=10) and (webpageObject == None)):
        try:
            if (debug):
                error.debug("Loading "+url)
            webpageObject = urllib.request.urlopen(url)
            #http://stackoverflow.com/questions/2712524/handling-urllib2s-timeout-python #TODO: check if order matters
        except Exception as inst:
            error.log("Connection Fail: 1001 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i==10):
            error.log("Coonection Timeout: -1001 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1001)        
        i = i+1
        
    try:
        if (debug):
            error.debug("Decoding webpage")
        datastream = looseDecoder(webpageObject.read(),4) #may help for webpages that seem to have one bad character
        #supertemp = (webpageObject.read()).decode('utf-8')
    except Exception as inst:
        error.log("Decode Error: -1003 (fatal) =>" + "\tUTF-8 decode error, Force System Exit =>\t" + str(inst))
        exit(-1003)  
    webpageObject.close()
    if (debug):
        error.debug("Webpage loaded")
    return datastream

def loadWebpage2(url):
    #an alternate way to load webpages via powershell
    datastream = None
    i = 0
    while ((i<=10) and (webpageObject == None)):
        try:
            if (debug):
                error.debug("Loading "+url)
            datastream = str(    subprocess.check_output(["powershell","(Invoke-WebRequest \""+url+"\").Content"])    )
        except Exception as inst:
            error.log("Connection Fail: 1013 (non-fatal) =>" + '\tAttempt ' + str(i) + ":" + str(inst) + ":\t" + str(url))
            time.sleep(4)
        if (i==10):
            error.log("Coonection Timeout: -1013 (fatal) =>" + "\tTimeout while attempting to access webpage, Force System Exit")
            exit(-1013)        
        i = i+1    
        
    if (debug):
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
    '''
    if (blockStart == "" or blockEnd == ""):
        block = datastream
    else:
        block = datastream[datastream.find(blockStart):datastream.find(blockEnd, datastream.find(blockStart))+len(blockEnd)]
    '''
    if (blockStart == "" or blockEnd == ""):
        blockStart = lineStart
        blockEnd = lineEnd
    block = datastream[datastream.find(blockStart):datastream.find(blockEnd, datastream.find(blockStart))+len(blockEnd)]
    while (block.find(lineStart) != -1):
        substring = block[block.find(lineStart):block.find(lineEnd, block.find(lineStart))+len(lineEnd)]
        targets.append(scrubURL(   substring[substring.find(targetStart)+len(targetStart):substring.find(targetEnd, substring.find(targetStart)+len(targetStart))]   ))
        block = block[block.find(lineEnd, block.find(lineStart))+len(lineEnd) : -1]
        if (debug):
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
    startingNumber  = 1
    pagesToScan     = 10000 #number of pages that this program will scan
    debug           = True
    
    #UserTweek
    comicName       = "Comic Name"
    URLStart        = "Start URL" #The url to start from
    URLLast         = "End URL" #the last url in the comic series, to tell the program exactly where to stop
    
    numberWidth     = 4 #the number of digits used to index comics
    
    #Global variables for parsing webpages
    URLCurrent = URLStart
    URLNext = None
    targetTitle = None
    targetURL = None
    comicNumber = startingNumber
    
    '''
    names = open("Names.csv",'w')
    names.write("URL,NAME,TITLE\n")
    names.close()
    '''

    error = Debug() #the error logging
    error.log("Comic Archiver has started, Version: " + version + " ==================================================")    
    if (debug):
        error.log("Debug logging is enabled")

    #create folder if it doesn't exsist
    if not (os.path.exists("./saved/")):
        error.log("Creating directory:\t" + "./saved/")
        os.makedirs("./saved/")
    
    for pageNumber in range (startingNumber, startingNumber + pagesToScan): #used for loop as failsafe incase the exit condition doesn't work as inteneded        
        datastream = loadWebpage(URLCurrent)
        error.log("processing webpage (p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "-t" + str(comicNumber) + ") = \t" + URLCurrent)
        
        targetTitle = parseTitle(datastream)
        targetURL = parseTarget(datastream)
        URLNext = parseURLNext(datastream)

        if (targetTitle == None):
            error.log("Missing Target: -1004")
            exit(-1004)
        if (targetURL == None):
            error.log("Missing TargetURL: -1006")
            exit(-1006)
            
        if (debug):
            error.debug("targetTitle = "+targetTitle, "targetURL = "+str(targetURL), "URLNext = "+URLNext)
            
        #saves the target(s)
        if savewebpage == True:
            saveTarget(URLCurrent, "saved/", "(" + comicName + " [" + str(comicNumber) + "-p" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + "]) " + targetTitle, ".html") #saveing html page        
        for j in targetURL:
            saveTarget(j, "saved/", "(" + comicName + " [" + str(comicNumber) + "]) " + targetTitle) #saving comic image
            '''
            names = open("Names.csv",'a')
            names.write(j + "," + j[j.find("comics")+7:len(j)] + "," + "(" + comicName + " [" + str(comicNumber) + "]) " + targetTitle + j[j.rfind('.'):len(j)] +"\n")
            names.close()
            '''
            comicNumber = comicNumber + 1

        #check for conclusion of comic
        if URLCurrent == URLLast:
            error.log("End condition detected, program exit")
            exit(0)
        
        if (debug):
            error.debug("Finished processing webpage (" + (('{:0>' + str(numberWidth) + '}').format(pageNumber)) + ")")        
        #reset and reload
        if URLNext == None:
            error.log("Missing URLNext: -1005 (fatal) =>\tURLNext missing, end condition not detected, forceing system exit")
            exit(-1005)
            
        URLCurrent = URLNext
        URLNext = None
        targetTitle = None
        targetURL = None       
        time.sleep(loopDelay)

    error.log("End Condition: -1009 (Unknown) =>\tPagesToScan reached, program terminating")
