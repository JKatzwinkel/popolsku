#encoding=UTF-8

import codecs
from random import shuffle, randint
import re

class Zagadka:
	instances=[]
	
	# encode alignments/directions as follows:
	# bit 1: move right
	# bit 2: move down
	# bit 3: move left
	# bit 4: move up
	# that way, direction 2 would be straight down, while 3 means diagonal
	# alignment down-rightwards, 4 means to the left and 12 up-leftwards
	
	# title: optional title
	def __init__(self, szerokosc, wysokosc, title=None):
		self.szerokosc=szerokosc
		self.wysokosc=wysokosc
		self.gloski=[['_']*szerokosc for rubryka in range(0,wysokosc)]
		self.kierunki=[[0]*szerokosc for rubryka in range(0,wysokosc)]
		self.part_of=[[[None] for col in range(szerokosc)]
			for rubryka in range(0,wysokosc)]
		self.kierunki_ukryte=[1,2,3]
		self.gdzie_jest={gloska:[] for gloska in alfabet}
		self.czestoscie={gloska:5 for gloska in alfabet}
		self.options={}
		self.hidden=[]
		self.uncovered=[]
		self.description=[]
		if title:
			self.title=title
		else:
			self.title=''
		self.density=.4
		Zagadka.instances+=[self]

	# returns last instance created
	@staticmethod # or @classmethod
	def last():
		if len(Zagadka.instances)>0:
			return Zagadka.instances[-1]
		print "Error: can't retrieve puzzle instance!"
		return None
	
	# forgets last created instance
	@staticmethod # or: @classmethod?
	def undo():
		if len(Zagadka.instances)>0:
			Zagadka.instances=Zagadka.instances[:-1]
	
	# calculate the impacts of a certain step on
	# the choices of remaining words
	def options_after_placing(self, slowo, position, kier):
		words = filter(lambda w:not (w in self.hidden or w == slowo), self.slowa)
		theory=self.pisac(slowo, position, kier, virtual=True)
		if not theory:
			return []
		result=[]
		# compute for all other words
		for word in words:
			options = self.options[slowo]
			remaining=[]
			for opt in options:
				# TODO: move score calculation to extra function
				score=self.odpowiedni(word, opt[0], opt[1], virtual=theory)
				if score > -1:
					remaining.append((opt[0], opt[1], score))#+opt[2])) # add asomeness of
					# move itself to each future asomeness?
				shuffle(remaining)
			result+=[(word, remaining)]
		return result
	
	
	# returns the word that
	def pick_word(self):
		words = filter(lambda w:not w in self.hidden, self.slowa)
		if words==[]:
			return None
		#words = filter(lambda w:len(self.options[w])>0, words)
		words = sorted(words, key=lambda w:len(self.options[w]))
		word = words[-1]
		if len(self.options[word])>len(words)*2:
			# make it quick
			# TODO: because of the default placement directions, 
			# TODO: positions on the right of the field 
			# TODO: are less likely to be chosen. Find a way
			# TODO: to make up for this!
			i = randint(0, max(1,int((1-self.density)*len(self.options[word]))))
			opt = self.options[word][i]
			return (word, opt[0], opt[1])
		outlook=[]
		for word in words:
			for opt in self.options[word]:
				remaining = self.options_after_placing(word, opt[0], opt[1])
				# (word, ((pos), kier), [(w,[((...])
				outlook.append((word, (opt[0], opt[1]), remaining))
		# temp functions
		let_words = lambda p: len(p[2])
		let_moves = lambda p: sum([len(w[1]) for w in p[2]])
		let_score = lambda p: sum([o[2] for w in p[2] for o in w[1]])
		# TODO: put the score function somewhere global and
		# make it be influenced by letter statistics and density parameter
		has_score = lambda p: let_score(p)+self.odpowiedni(p[0], p[1][0], p[1][1])
		shuffle(outlook)
		ranking = sorted(
			sorted(
				sorted(outlook, key=let_moves), key=has_score), key=let_words)
		if ranking == []:
			return None
		#for rank in ranking[-2:]:
			#print rank[0], rank[1], len(rank[2]), # word, pos, words left possible
			#print [len(w[1]) for w in rank[2]], # options for remaining words
			#print [o[2] for w in rank[2] for o in w[1]], # best future score
		choice = ranking[-1]
		return (choice[0], choice[1][0], choice[1][1])#[0]
			

	# ukrych slowa
	def hide(self, words, kierunki=[1,2,3]):
		self.kierunki_ukryte=kierunki
		words = filter(lambda w:re.findall('[()-]', w) == [], words)
		self.slowa = [slowo for slowo in words]
		# statistics, initializations
		for word in self.slowa:
			self.options[word] = None
			for gloska in word.lower():
				self.czestoscie[gloska]+=1
		self.czestoscie[' ']=0
		ogolem=sum(self.czestoscie.values())
		self.prawdopodobienstwa={gloska:float(self.czestoscie[gloska])/ogolem 
			for gloska in alfabet}
		# start iterative hiding
		while len(self.hidden)<len(self.slowa):
			self.compute_positions()
			words=[w for w in self.slowa if not w in self.hidden]
			move = self.pick_word()#self.best_placable()
			if move:
				# Ukryję słowo move[0] w move[1]
				self.pisac(move[0], move[1], move[2])
			else:
				print "Can't put any more words"
				return
		

	# computes all possible placements for all words that are still to
	# be hidden. result is a dictionary in which a list is stored for
	# each word, beginning with its most promising placements
	def compute_positions(self):
		to_hide=filter(lambda x:not x in self.hidden, self.slowa)
		for word in to_hide:
			opt=[]
			#TODO: some real shit!
			if not self.options[word]:
				for row in range(0, self.szerokosc):
					for col in range(0, self.wysokosc):
						pos=(col,row)
						for kier in self.kierunki_ukryte:
							#TODO: placement score method
							crossing = self.odpowiedni(word, pos, kier)
							score = crossing
							if crossing > -1:
								opt+=[(pos, kier, score)]
			else:
				for o in self.options[word]:
					pos,kier,score = o
					# TODO: placement score method
					score = self.odpowiedni(word, pos, kier)
					if score > -1:
						opt+=[(pos, kier, score)]
			# TODO: move score calculation to extra function
			# TODO: remember to put density parameter and letter statistics
			# in it!
			shuffle(opt)
			opt=sorted(opt,key=lambda o:o[2],reverse=True)
			self.options[word] = opt
		self.slowa = filter(lambda w:len(self.options[w])>0, self.slowa)
					

	# determine whether a word fits at a given position with certain
	# alignment
	# virtual entries are (glos, kier)-tuples that are considered
	# when set, as hypothetical view into the future
	def odpowiedni(self, slowo, pozycja, kierunek, virtual={}):
		if self.gloska_w(self.isc_tylem(pozycja, kierunek, 1))[1] == kierunek:
			return -1		
		col, row = pozycja
		slowo = slowo.lower()
		matches=0
		for gloska in slowo:
			g, k, _ = self.gloska_w((col, row))
			if k>15:
				return -1
			prognose = virtual.get((col, row), None)
			if g != '_' or prognose:
				if prognose:
					if prognose[0] != gloska or prognose[1] == kierunek:
						return -1
					else:
						matches += 1
				else:
					if g != gloska or k == kierunek:
						return -1
					else:
						matches+=1
			col += kierunek & 1 # move right if lowest bit is set
			row += kierunek / 2 & 1 # move down if second bit is set
			col -= kierunek / 4 & 1 # move left if third bit is set
			row -= kierunek / 8 & 1 # move up if fourth bit is set
		_, k, _ = self.gloska_w((col, row))
		if k == kierunek:
			return -1
		return matches

	# returns information about the given cell
	def gloska_w(self, pozycja):
		col, row = pozycja
		if col >= self.szerokosc or col < 0:
			return (None, 16, [])
		if row >= self.wysokosc or row < 0:
			return (None, 16, [])
		return (self.gloski[row][col], 
			self.kierunki[row][col],
			self.part_of[row][col])
	
	# go backwards from position in opposite direction for a number 
	# of steps (krok, za krokiem)
	def isc_tylem(self, pozycja, kierunek, krokiem):
		col, row = pozycja
		col -= (kierunek & 1) * krokiem
		row -= (kierunek / 2 & 1) * krokiem
		col += (kierunek / 4 & 1) * krokiem
		row += (kierunek / 8 & 1) * krokiem
		return (col, row)

	#hide single letter at position (pozycja/ustep) with alignment
	def ukryc_gloske(self, gloska, pozycja, kierunek): 
		col, row = pozycja
		if self.gloski[row][col] != '_':
			if self.gloski[row][col] != gloska:
				print "ALARM"
			return
		self.gdzie_jest[gloska] += [pozycja]
		self.kierunki[row][col] = kierunek
		self.gloski[row][col] = gloska

	# place word at given position
	# virtual writing does not actually write anything,
	# but simutales writing and returns a dictionary
	# containing letters and direction that
	# would have been written
	def pisac(self, slowo, pozycja, kierunek, virtual=False):
		if self.odpowiedni(slowo, pozycja, kierunek)<0:
			return None
		col, row = pozycja
		if virtual:
			res={}
		for gl in slowo.lower():
			if virtual:
				res[(col, row)]=(gl, kierunek)
			else:
				self.ukryc_gloske(gl, (col, row), kierunek)
				self.part_of[row][col] += [slowo]
			col += kierunek & 1 # move right if lowest bit is set
			row += kierunek / 2 & 1 # move down if second bit is set
			col -= kierunek / 4 & 1 # move left if third bit is set
			row -= kierunek / 8 & 1 # move up if fourth bit is set
		if virtual:
			return res
		self.hidden+=[slowo]
			
	# marks words in uppercase letters
	def solve(self, word=None):
		for row in range(self.wysokosc):
			for col in range(self.szerokosc):
				gloska, kierunek, part_of = self.gloska_w((col, row))
				if kierunek > 0 and (word in part_of):
					self.gloski[row][col] = gloska.upper()
		if not word:
			self.uncovered=[word for word in self.slowa]
		else:
			self.uncovered+=[word]

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
			
	# uncover one word
	def przyklad(self):
		index=len(self.uncovered)-len(self.slowa)
		if index<0:
			self.solve(word=self.slowa[index])

		
	# basic displayal
	def __str__(self):
		res=u''
		for i in self.gloski:
			res+=' '.join(i)+'\n'
		return res.encode('utf8')
	
	# adds a description text that can be printed above puzzle
	# pass as string or list of strings
	def add_description(self, desc):
		if type(desc) in (unicode, str):
			self.description += [desc]
		if type(desc) is list:
			self.description += desc
		
	# return a caption/heading for this puzzle
	# in tex
	def heading_tex(self):
		tex=u'\t\t\\multicolumn{{{0}}}{{|c|}}{{{1}}}\\\\\n'
		if len(self.slowa)<46:
			liczbo=liczba[len(self.slowa)-1]
		else:
			liczbo=u'{0}'.format(len(self.slowa))
		label=u'\\textsc{{{0}}}'.format(self.title, liczbo)
		sublabel=u'{0} ukryte słowa'
		sublabel=sublabel.format(liczbo)
		box=u'\\parbox[t]{{.8\\linewidth}}{{{0}}}'.format(label)
		res=u'\t\t\\hline\n'
		res+=tex.format(self.szerokosc, label)
		def subheading_tex(width, sublabel):
			textsize=''
			if len(sublabel)>=self.szerokosc*1.5:
				if len(sublabel)>=self.szerokosc*2.2:
					head_slowa=sublabel.split(' ')
					return tex.format(width, textsize+' '.join(
						head_slowa[:len(head_slowa)/2]))+subheading_tex(width, 
						' '.join(head_slowa[len(head_slowa)/2:]))
				else:
					textsize='\\small '
			return tex.format(width, textsize+sublabel)
		res+=subheading_tex(self.szerokosc, sublabel)
		res+='\t\t\\hline\n'
		return res
		
	def description_tex(self):
		tex=u''
		for line in self.description:
			tex+=u'{0}\\newline\n'.format(line)
		if self.description == []:
			tex+=u'Ukryte słowa\\newline\n'
		return tex+'\n'

	# return a list indicating what's hidden in the puzzle
	# in tex
	def list_tex(self):
		# at most 3 columns
		tex=u'\\begin{enumerate}\n'
		columns = 1
		if self.szerokosc>=25:
			while len(self.slowa)/columns > 5 and columns<3:
				columns+=1
		else:
			tex+='\\itemsep0em\n'
		col_items=len(self.slowa)/columns
		while columns*col_items < len(self.slowa):
			col_items+=1
		if col_items > self.wysokosc-3:
			tex+='\\vspace{{{0:.2f}cm}}\n'.format(col_items/10.)
		line=1
		for column in range(columns):
			if columns>1:
				tex+='\t\\begin{{minipage}}[t]{{{0:.1f}\\textwidth}}\n'.format(1./columns)
			while line <= min(len(self.slowa), (column+1)*col_items):
				if line<len(self.uncovered)+1:
					tex+=u'\t\t\\item \\underline{{\\textit{{{0}}}\\hspace{{.07\\linewidth}}}}\n'.format(
						self.uncovered[line-1])
				else:
					tex+='\t\t\\item \\underline{\\hspace{.75\\linewidth}}\n'
				line+=1
			if columns>1:
				tex+='\t\\end{minipage}\n'
		tex+='\\end{enumerate}\n'
		return tex
		
	def kierunki_tex(self):
		tex=u'\\multicolumn{{{0}}}{{r}}{{\\tiny $ {1} $}}'
		return tex.format(self.szerokosc, 
			' '.join([arrows[k] for k in self.kierunki_ukryte]))
					
	# return latex table
	def totex(self):
		res=u'\\begin{minipage}[t]{\\textwidth}\n\\vspace{.7cm}\n'
		res+='\\stepcounter{zagadka}\n'
		res+='\\textbf{\\Huge \\arabic{zagadka}.} \n'
		res+=self.description_tex()+'\\vspace{.3cm}\n'
		def puzzle_tex():
				fm=[u'{0}', u'\\cellcolor{{blue!25}}\\textbf{{{0}}}']
				res=u''
				for row in self.gloski:
					rowtex = [fm[g.isupper()].format(g.lower()) for g in row]
					res+=u'\t\t{0} \\\\\n'.format(u' & '.join(rowtex))			
				return res
		if self.szerokosc<25: # print list next to puzzle
			res+=u'''\\begin{{minipage}}{{.4\\textwidth}}
	\\begin{{flushleft}}\n{0}\n\\end{{flushleft}}
	\\end{{minipage}}'''.format(self.list_tex())
			res+=u'''
	\\begin{{minipage}}[t]{{.55\\textwidth}}\n\t\\begin{{tabular}}{{|{0}|}}
{1}\n\t\\hline\n'''.format(
				' '.join(['c']*self.szerokosc), self.heading_tex())
			res+=puzzle_tex()
			res+='''\t\t\\hline
		{0}
	\\end{{tabular}}
	\\end{{minipage}}
\\end{{minipage}}\n
\n\n'''.format(self.kierunki_tex())
		else: #print list right below puzzle
			res+=u'''\\begin{{center}}
	\\begin{{tabular}}{{|{1}|}}\n{0}\n\t\t\\hline\n'''.format(
			self.heading_tex(), ' '.join(['c']*self.szerokosc))
			res+=puzzle_tex()
			res+=u'''\t\t\\hline
		{1}
	\\end{{tabular}}
\\end{{center}}\n
\\end{{minipage}}\n
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
		
		
def load(filename, limit=None, maxlen=100):
	wordlist = codecs.open(filename, encoding='utf-8')
	words=[word.strip() for word in wordlist]
	shuffle(words)
	words=filter(lambda w:len(w)<=maxlen, words)
	if limit:
		words=sorted(words[:limit])
	return words
	
# return an optimized subset of word pool
def wordset(words, limit):
	if limit:
		words=[w for w in words]
		shuffle(words)
		seed=words[0]
		sub=[seed]
		fits=lambda x:sum([(-1, seed.count(l))[l in seed] for l in x]) / float(len(x))
		score=lambda x:sum([fits((x+' ')[i:-i-1]) for i in range(0,1)])
		while len(sub)<limit:
			likes=sorted(words, key=score, reverse=True)
			while likes[0] in sub:
				likes.pop(0)
			like=likes[0]
			sub+=[like]
			seed+=like
		return sorted(sub)
	else:
		return words
	
# return new instance
# filename: file containing word list (one per line)
# words: optional word list
# limit: for very long list files, limit to random subset
def zagadka(width, height, filename=None, words=None, title=None,
	limit=None, kierunki=[1,2,3]):
	if filename:
		word_list=load(filename, maxlen=max(width, height))
	if word_list:
		recall=0
		puzzle=None
		while recall<.9:
			if puzzle:
				Zagadka.undo()
			words=wordset(word_list, limit)
			puzzle = Zagadka(width, height, title=title)
			puzzle.density+=recall/3
			puzzle.hide(words, kierunki)
			puzzle.fill()
			if len(puzzle.slowa)<len(words):
				recall=float(len(puzzle.slowa))/max(width, height)
			else:
				recall=1.
			print '{0:.2f}'.format(recall)
			if randint(0,100)<2:
				width=height=max(width,height)
	else:
		puzzle = Zagadka(width, height, title=title)
	return puzzle


		
tex_template=u'''\\documentclass[a4paper,11pt]{{article}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{lmodern}}
\\usepackage[table]{{xcolor}}

\\begin{{document}}
\\setlength{{\\tabcolsep}}{{1.5pt}}\n
\sffamily 
\\newcounter{{zagadka}}\n
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

liczba = codecs.open('../slowa/liczba', encoding='utf-8')
liczba=[liczbo.strip() for liczbo in liczba]

zagadka(8, 6,filename='../slowa/miastami_polskimi',
	title=u"Miasta", limit=15)
Zagadka.instances[-1].add_description(
	u'Jest trudna. Szukasz nazwiska miastów.')
zagadka(31,14,filename='../slowa/warzywa',title="Warzywa")
zagadka(19,18,filename='../slowa/owoce',title="Owoce")
Zagadka.instances[-1].add_description(
	u'Jakie są te smaczne i zdrowe owocowy?')
zagadka(20,13,filename='../slowa/czasowniki',title="Czasowniki")
zagadka(25,17,filename='../slowa/czasowniki2',
	title="Czasowniki - Koniugacja", kierunki=[1,2,3,9])
Zagadka.last().add_description(u'Uwaga! Ma jeszcze kierunki!')
Zagadka.last().przyklad()
Zagadka.last().przyklad()
zagadka(18,13,filename='../slowa/rodzina',title="Rodzina")
Zagadka.last().przyklad()

save_tex('zagadki.tex')

for puzzle in Zagadka.instances:
	puzzle.solve()
	
save_tex('zagadki_napisalismy.tex')
