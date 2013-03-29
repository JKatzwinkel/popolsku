#encoding=UTF-8

import codecs
from random import shuffle, randint
import re

class Zagadka:
	instances=[]
	
	#self.rubryki=[] # rows
	#self.gloski={} # positions of occurences of letters
	#self.kierunki=[] # alignments of words
	# encode alignments/directions as follows:
	# bit 1: move right
	# bit 2: move down
	# bit 3: move left
	# bit 4: move up
	# that way, direction 2 would be straight down, while 3 means diagonal
	# alignment down-rightwards, 4 means to the left and 12 up-leftwards
	
	
	def __init__(self, szerokosc, wysokosc, title=None):
		self.szerokosc=szerokosc
		self.wysokosc=wysokosc
		self.gloski=[['_']*szerokosc for rubryka in range(0,wysokosc)]
		self.kierunki=[[0]*szerokosc for rubryka in range(0,wysokosc)]
		self.kierunki_ukryte=sorted(kierunki)
		self.gdzie_jest={gloska:[] for gloska in alfabet}
		self.czestoscie={gloska:20 for gloska in alfabet}
		if title:
			self.title=title
		else:
			self.title=''
		Zagadka.instances+=[self]

	# ukrych slowa
	def hide(self, words):
		self.slowa = [slowo for slowo in words]
		shuffle(words)
		# statistics
		for word in words:
			for gloska in word.lower():
				self.czestoscie[gloska]+=1
		self.czestoscie[' ']=0
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
				if rubryka[i] in ('_', ' '):
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
		#TODO: remove word from list
					
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
				if g != gloska or k == kierunek:
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

	# marks words in uppercase letters
	def solve(self):
		for row in range(self.wysokosc):
			for col in range(self.szerokosc):
				gloska, kierunek = self.gloska_w((col, row))
				if kierunek > 0:
					self.gloski[row][col] = gloska.upper()
		#TODO: make list of words visible

		
	# basic displayal
	def __str__(self):
		res=u''
		for i in self.gloski:
			res+=' '.join(i)+'\n'
		return res.encode('utf8')
		
	# return a caption/heading for this puzzle
	# in tex
	def heading_tex(self):
		tex=u'\\multicolumn{{{0}}}{{|c|}}{{{1}}}\\\\\n\n'
		if len(self.slowa)<45:
			liczbo=liczba[len(self.slowa)-1]
		else:
			liczbo=u'{0}'.format(len(self.slowa))
		label=u'\\textsc{{{0}}}'.format(self.title, liczbo)
		sublabel=u'{0} ukryte słowa'
		sublabel=sublabel.format(liczbo)
		box=u'\\parbox[t]{{.8\\linewidth}}{{{0}}}'.format(label)
		res=u'\\hline\n'
		res+=tex.format(self.szerokosc, label)
		res+=tex.format(self.szerokosc, sublabel)
		res+='\\hline\n'
		return res

	# return a list indicating what's hidden in the puzzle
	# in tex
	def list_tex(self):
		# at most 3 columns
		columns = 1
		if self.szerokosc>=25:
			while len(self.slowa)/columns > 5 and columns<3:
				columns+=1
		col_items=len(self.slowa)/columns
		while columns*col_items < len(self.slowa):
			col_items+=1
		tex=u'\\begin{enumerate}'
		line=1
		for column in range(columns):
			tex+='\\begin{{minipage}}[t]{{{0:.1f}\\linewidth}}\n'.format(1.2/columns)
			while line <= min(len(self.slowa), (column+1)*col_items):
				tex+='\\item \\underline{\\hspace{.75\\linewidth}}\n'
				line+=1
			tex+='\\end{minipage}\n'
		tex+='\\end{enumerate}\n'
		return tex
		
	def kierunki_tex(self):
		tex=u'\\multicolumn{{{0}}}{{r}}{{\\tiny $ {1} $}}'
		return tex.format(self.szerokosc, 
			' '.join([arrows[k] for k in self.kierunki_ukryte]))
					
	# return latex table
	def totex(self):
		if self.szerokosc<25: # print list next to puzzle
			res=u'''
	\\begin{{minipage}}{{.4\\textwidth}}
	\\begin{{flushleft}}
		{0}
		\\end{{flushleft}}
	\\end{{minipage}}'''.format(self.list_tex())
			res+=u'''
	\\begin{{minipage}}{{.55\\textwidth}}
		\\begin{{tabular}}{{|{0}|}}
			{1}
			\\hline\n
			'''.format(' '.join(['c']*self.szerokosc), self.heading_tex())
			for row in self.gloski:
				res+=u'{0} \\\\\n'.format(u' & '.join(row))
			res+='''
		\\hline
		{0}
	\\end{{tabular}}
	\\end{{minipage}}
\n\n'''.format(self.kierunki_tex())
		else: #print list right below puzzle
			res=u'''\\begin{{center}}
	\\begin{{tabular}}{{|{1}|}}
		{0}
		\\hline\n'''.format(self.heading_tex(), ' '.join(['c']*self.szerokosc))
			for row in self.gloski:
				res+=u'{0} \\\\\n'.format(u' & '.join(row))
			res+='''
		\\hline
		{1}
	\\end{{tabular}}
\\end{{center}}
{0}
\n\n'''.format(self.list_tex(), self.kierunki_tex())
		return res

# saves all known zagadki to one .tex file	
def save_tex(filename):
	tex = u''
	for puzzle in Zagadka.instances:
		tex += puzzle.totex()
		
	output = tex_template.format(tex)
	with codecs.open(filename, 'w', encoding='utf-8') as tex_file:
		for line in output:
			tex_file.write(line)
		
		
# return new instance
def zagadka(width, height, filename=None, words=None, title=None):
	puzzle = Zagadka(width, height, title=title)
	if filename:
		wordlist = codecs.open(filename, encoding='utf-8')
		words=[word.strip() for word in wordlist]
		#words=[re.sub('[-]', ' ', word) for word in words]
	if words:
		puzzle.hide(words)
		puzzle.fill()
	return puzzle
		
tex_template=u'''\\documentclass[a4paper,11pt]{{article}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{lmodern}}
\\begin{{document}}
\\setlength{{\\tabcolsep}}{{1.5pt}}\n
\sffamily \n
{0}
\\end{{document}}'''

alfabet=u'aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż '
arrows={1:'\\rightarrow',
				2:'\\downarrow',
				3:'\\searrow',
				4:'\\leftarrow',
				6:'\\swarrow',
				8:'\\uparrow',
				9:'\\nearrow',
				12:'\\nwarrow' }

liczba = codecs.open('liczba', encoding='utf-8')
liczba=[liczbo.strip() for liczbo in liczba]

kierunki=[1,2,3]


zagadka(30,20,filename='warzywa',title="Warzywa")
zagadka(23,16,filename='owoce',title="Owoce")
zagadka(20,13,filename='czasowniki',title="Czasowniki")
zagadka(25,17,filename='czasowniki2',title="Czasowniki - Koniugacja")
zagadka(40,28,filename='bardzo_dlugo_exc2',title=u"Bardzo długa słowa")

#for puzzle in Zagadka.instances:
#	puzzle.solve()
	
save_tex('zadagki.tex')
