#here i've tried to divide the words into Verbs and Adjectives. But, i don't remember for what i made it


import re
stage = 1000 #and 2_1000, 3_1000, etc...

source = 'sources/' + str(stage) #where exist row words
dir_verb = 'verbs/' + str(stage) #where going words sorted by category
dir_adjectives = 'adjectives/' + str(stage)

def openFile(path):
	return open(path).read().split(' ')

dictionary = openFile(source) #list of words

def write_to_file(name_of_chapter, dictt, path):
	dst = open(path, 'w')
	header = '----------'+name_of_chapter+'----------' + '\n'
	dst.write(header)
	for i in range(len(dictt)):
		line = dictt[i] + '\n'
		dst.write(line)
	dst.close()
	print('success writed!')

def search_verbs(dictt):
	verbs = []
	for verb in dictt:
		if re.search(u'en$', verb) and not re.search(u'^[A-Z]', verb):
			verbs.append(verb)
	write_to_file('Verbs', verbs, dir_verb)

search_verbs(dictionary)
