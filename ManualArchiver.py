import os
try:
	from PIL import Image
except:
	print("ERROR: Pillow module not installed")
	print("To install use $> pip3 install pillow")
	exit()

#creates required folder
if not (os.path.exists("./saved/")):
	os.makedirs("./saved/")
	print("Made 'saved' directory")

if not (os.path.exists("./savedOriginal/")):
	os.makedirs("./savedOriginal/")
	print("Made 'savedOriginal' directory")

ComicName = "ComicName"
fileExclusionList = ("ManualArchiver.py",
                     "saved",
                     "savedOriginal")
inputDirectory = "InputDirectory"
saveOriginal = True #enables saving of the original pictures before they are stitched together

while (True):
	input("Next Element? [enter]:")

	#takes files, moves them, and extracts them into usable format
	if os.path.exists("./" + inputDirectory):
		os.system("mv " + ("./" + inputDirectory + "/*") + " " + "./test.zip")
		os.system("rm -r ./" + inputDirectory)
		os.system("unzip ./test.zip")
		os.system("rm ./test.zip")

	#get list of files for renaming
	fileList = os.listdir()
	for i in fileExclusionList:
		if i in fileList:
			fileList.remove(i)
	fileList.sort()
	#renames the files for better sorting (IE: from '9.jpg, 10.jpg, 11.jpg' to '09.jpg, 10.jpg, 11.jpg')
	for i in fileList:
		temp = i.split(".")[0].rjust(4,"0")
		temp += "."
		temp += i.split(".")[1]
		os.rename(i,temp)

	fileList = os.listdir()
	for i in fileExclusionList:
		if i in fileList:
			fileList.remove(i)
	fileList.sort() #fileList is now the primary file list, ordered

	print("Number of images:\t" + str(len(fileList)))

	#figures out what extransion to save as
	#TODO this needs doing better
	extension = ""
	for i in fileList:
		t1 = i.split(".")[-1].lower()
		#will choose the file extension of the first file, but can be extended to be more complicated if needed
		if extension == "":
			extension = t1
	print("File Extension:\t" + str(extension))

	#get last numbered file
	estimatedNumber = len(os.listdir("./saved/")) #a 'good enough' estimate, instead of parsing file names

	#stich those pictures together
	# https://note.nkmk.me/en/python-pillow-concat-images/
	img = []
	imgHeight = 0
	imgWidth = 0
	for i in fileList:
		temp = Image.open(i)
		imgHeight += temp.height
		imgWidth = max(imgWidth, temp.width)
		img.append(temp)

	if len(fileList) > 0:
		newImage = Image.new('RGB', (imgWidth, imgHeight), (0,0,0))
		heightOffset = 0
		for i in img:
			newImage.paste(i, (0, heightOffset))
			heightOffset += i.height

		#put stitched together picture in folder with correct number/name
		newImage.save("./saved/" + "(" + ComicName +" [" + str(estimatedNumber + 1).rjust(4, "0") + "]) " + 
		              ComicName + "." + str(extension))

		#put initial pictures in folder with correct number/name
		if saveOriginal == True:
			countOriginal = 0
			for i in img:
				extensionOriginal = fileList[countOriginal].split(".")[-1].lower() #extracts the file extension string from the filename
				i.save("./savedOriginal/" +
                                       "(" + ComicName + " [" + str(estimatedNumber + 1).rjust(4,"0") +
				       "-" + str(countOriginal + 1).rjust(2,"0") + "]) " +
				       ComicName + "." + str(extensionOriginal))
				countOriginal += 1

			print("Number of Saved Original Images: " + str(countOriginal))

		print("Saved Image Number: " + str(estimatedNumber + 1))

		newImage.close()

	#close everything out
	for i in img:
		i.close()

	#remove unneeded files
	for i in fileList:
		os.remove(i)
