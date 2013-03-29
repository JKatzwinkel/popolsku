#encoding=UTF-8

import codecs

class Zagadka:
	rubryki=[] # rows
	gloski={} # positions of occurences of letters
	rierunki # alignments of words
	
	def __init__(szerokosc, wysokosc):
		

alfabet=u'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż'
czestoscie={gloska:10 for gloska in alfabet}

wordlist = codecs.open('warzywa', encoding='utf-8')

words=[word.strip() for word in wordlist]
for word in words:
	for gloska in word:
		czestoscie[gloska]+=1

ogolem=sum(czestoscie.values())
prawdopodobienstwa={gloska:float(czestoscie[gloska])/ogolem 
	for gloska in alfabet}

for gloska, czestosc in czestoscie.items():
	print gloska, czestosc



zagadka=Zagadka(30,20)
for rubryka in range(0,20):
	zagadka.append(['']*30)

for word in words:
	print 'Ukryję słowo', word
	rzadkoscie=sorted(word, key=lambda gloska:czestoscie[gloska])
	print ''.join(rzadkoscie)
