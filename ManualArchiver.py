import os
try:
	from PIL import Image
except:
	print("ERROR Pillow module not installed")
	exit()

if not (os.path.exists("./saved/")):
	os.makedirs("./saved/")
	print("Made 'saved' directory")

if not (os.path.exists("./savedOriginal/")):
	os.makedirs("./savedOriginal/")
	print("Made 'saveOriginal' directory")

while (True):
	input("Next Element? [enter]:")

	#takes files, moves them, and extracts them into usable format
	if os.path.exists("InputDirectory"):
		os.system("mv ./InputDirectory/* ./test.zip")
		os.system("rm -r ./InputDirectory")
		os.system("unzip ./test.zip")
		os.system("rm ./test.zip")

	#get list of files
	fileList = os.listdir()
	fileList.remove('manual.py')
	fileList.remove('saved')
	fileList.remove('savedOriginal')
	fileList.sort()
	print("Number of images:\t" + str(len(fileList)))

	#renames the files for better sorting
	for i in fileList:
		temp = i.split(".")[0].rjust(4,"0")
		temp += "."
		temp += i.split(".")[1]
		os.rename(i,temp)

	fileList = os.listdir()
	fileList.remove('manual.py')
	fileList.remove('saved')
	fileList.remove('savedOriginal')
	fileList.sort()
	#print(fileList)

	#figures out what extransion to save as
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
		temp = 0
		for i in img:
			newImage.paste(i, (0, temp))
			temp += i.height

		#put stitched together picture in folder with correct number/name
		newImage.save("./saved/" + "(Comic Name [" + str(estimatedNumber + 1).rjust(4, "0") + "])" + 
				" Comic Name" + 
				"." + str(extension))

		#put initial pictures in folder with correct number/name
		temp = 0
		for i in img:
			temp += 1
			i.save("./savedOriginal/" + "(Comic Name [" + str(estimatedNumber + 1).rjust(4,"0") +
				"-" + str(temp).rjust(2,"0") + "])" +
				" Comic Name" + 
				"." + str(extension))

		print("Saved Image " + str(estimatedNumber + 1))

		newImage.close()

	#close everything out
	for i in img:
		i.close()

	#remove unneeded files
	for i in fileList:
		os.remove(i)
