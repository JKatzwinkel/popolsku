#encoding=UTF-8

import codecs
from random import shuffle, randint
import re

class Zagadka:
	rubryki=[] # rows
	gloski={} # positions of occurences of letters
	kierunki=[] # alignments of words
	# encode alignments/directions as follows:
	# bit 1: move right
	# bit 2: move down
	# bit 3: move left
	# bit 4: move up
	# that way, direction 2 would be straight down, while 3 means diagonal
	# alignment down-rightwards, 4 means to the left and 12 up-leftwards
	
	def __init__(self, szerokosc, wysokosc):
		self.szerokosc=szerokosc
		self.wysokosc=wysokosc
		self.gloski=[['_']*szerokosc for rubryka in range(0,wysokosc)]
		self.kierunki=[[0]*szerokosc for rubryka in range(0,wysokosc)]
		self.gdzie_jest={gloska:[] for gloska in alfabet}
		self.czestoscie={gloska:10 for gloska in alfabet}

	# ukrych slowa
	def hide(self, words):
		shuffle(words)
		# statistics
		for word in words:
			for gloska in word:
				self.czestoscie[gloska]+=1
		ogolem=sum(self.czestoscie.values())
		self.prawdopodobienstwa={gloska:float(self.czestoscie[gloska])/ogolem 
			for gloska in alfabet}
		#for gloska, czestosc in self.czestoscie.items():
			#print gloska, czestosc
		#print words
		for word in words:
			#print 'Ukryję słowo', word
			self.ukryc_slowo(word)

	# fill puzzle up with random letters
	def fill(self):
		probranges={}
		counter=0
		for gloska, prob in self.czestoscie.items():
			probranges[counter] = gloska
			counter += prob
		# fill
		for rubryka in self.gloski:
			for i in range(len(rubryka)):
				if rubryka[i] == '_':
					rnd = randint(0,counter)
					while not probranges.get(rnd, None):
						rnd -= 1
					rubryka[i] = probranges[rnd]
		
	# hide single word
	def ukryc_slowo(self, slowo): #hide word
		# sort the word's letters by their overall frequency
		rzadkoscie=sorted(slowo, key=lambda gloska:self.czestoscie[gloska])[:2]
		kierunki=globals()['kierunki']
		# begin with least frequent letter
		for gloska in rzadkoscie:
			if len(self.gdzie_jest[gloska]) > 0:
				# all occurences of current letter
				jest_tam = [m.start() for m in re.finditer(gloska, slowo)]
				# for every position where this letter is already in puzzle:
				candidates={}
				gdzie_jest=self.gdzie_jest[gloska]
				shuffle(gdzie_jest)
				for pozycja in gdzie_jest:
					# find positions that cross as many existing words as possible
					for steps in jest_tam:
						shuffle(kierunki)
						for kierunek in kierunki:
							start_point = self.isc_tylem(pozycja, kierunek, steps)
							crosses = self.odpowiedni(slowo, start_point, kierunek)
							candidates[crosses] = candidates.get(crosses, [])+[
								(start_point, kierunek)]
				# choose one of the positions where word crosses the most others
				best = max(candidates.keys())
				if len(candidates)>0 and best>-1:
					candidates=candidates[best]
					shuffle(candidates)
					start_point, kierunek = candidates[0]
					self.pisac(slowo, start_point, kierunek)
					return
		# place randomly
		for proba in range(1000):
			col=randint(0, self.szerokosc-1)
			row=randint(0, self.wysokosc-1)
			kierunek=kierunki[randint(0, len(kierunki)-1)]
			if self.odpowiedni(slowo, (col, row), kierunek)>-1:
				self.pisac(slowo, (col, row), kierunek)
				return
		print "ERROR: could not place word"
					
	# place word at given position
	def pisac(self, slowo, pozycja, kierunek):
		col, row = pozycja
		for gl in slowo:
			self.ukryc_gloske(gl, (col, row), kierunek)
			col += kierunek & 1 # move right if lowest bit is set
			row += kierunek / 2 & 1 # move down if second bit is set
			col -= kierunek / 4 & 1 # move left if third bit is set
			row -= kierunek / 8 & 1 # move up if fourth bit is set

	# determine whether a word fits at a given position with certain
	# alignment
	def odpowiedni(self, slowo, pozycja, kierunek):
		col, row = pozycja
		matches=0
		for gloska in slowo:
			g, k = self.gloska_w((col, row))
			if k>=15:
				return -1
			if g != '_':
				if g != gloska:
					return -1
				else:
					matches+=1
			col += kierunek & 1 # move right if lowest bit is set
			row += kierunek / 2 & 1 # move down if second bit is set
			col -= kierunek / 4 & 1 # move left if third bit is set
			row -= kierunek / 8 & 1 # move up if fourth bit is set
		_, k = self.gloska_w((col, row))
		if kierunek == k:
			return -1
		return matches

	# returns information about the given cell
	def gloska_w(self, pozycja):
		col, row = pozycja
		if col >= self.szerokosc or col < 0:
			return (None, 15)
		if row >= self.wysokosc or row < 0:
			return (None, 15)
		return (self.gloski[row][col], self.kierunki[row][col])
	
	# go backwards from position in opposite direction for a number 
	# of steps (krok, za krokiem)
	def isc_tylem(self, pozycja, kierunek, krokiem):
		col, row = pozycja
		col -= kierunek & 1 * krokiem
		row -= kierunek / 2 & 1 * krokiem
		col += kierunek / 4 & 1 * krokiem
		row += kierunek / 8 & 1 * krokiem
		return (col, row)

	#hide single letter at position (pozycja/ustep) with alignment
	def ukryc_gloske(self, gloska, pozycja, kierunek): 
		col, row = pozycja
		self.gdzie_jest[gloska] += [pozycja]
		self.kierunki[row][col] = kierunek
		self.gloski[row][col] = gloska
		
	# basic displayal
	def __str__(self):
		res=u''
		for i in zagadka.gloski:
			res+=' '.join(i)+'\n'
		return res.encode('utf8')
		
	# marks words in uppercase letters
	def solve(self):
		for row in range(self.wysokosc):
			for col in range(self.szerokosc):
				gloska, kierunek = self.gloska_w((col, row))
				if kierunek > 0:
					self.gloski[row][col] = gloska.upper()

alfabet=u'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż'

kierunki=[1,2,3]

wordlist = codecs.open('warzywa', encoding='utf-8')

words=[word.strip() for word in wordlist]

zagadka=Zagadka(30,20)
zagadka.hide(words)
zagadka.fill()
print zagadka
#zagadka.solve()
#print zagadka
