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
	
	# title: optional title
	def __init__(self, szerokosc, wysokosc, title=None):
		self.szerokosc=szerokosc
		self.wysokosc=wysokosc
		self.gloski=[['_']*szerokosc for rubryka in range(0,wysokosc)]
		self.kierunki=[[0]*szerokosc for rubryka in range(0,wysokosc)]
		self.part_of=[[[None] for col in range(szerokosc)]
			for rubryka in range(0,wysokosc)]
		self.kierunki_ukryte=sorted(kierunki)
		self.gdzie_jest={gloska:[] for gloska in alfabet}
		self.czestoscie={gloska:10 for gloska in alfabet}
		self.options={}
		self.hidden=[]
		self.uncovered=[]
		self.description=[]
		if title:
			self.title=title
		else:
			self.title=''
		self.density=.1
		Zagadka.instances+=[self]

	# returns last instance created
	def get():
		if len(Zagadka.instances)>0:
			return Zagadka.instances[-1]
		print "Error: can't retrieve puzzle instance!"
		return None
	
	# returns the word that can be placed at the highest score with
	# the most options
	def best_placable(self):
		words = filter(lambda w:not w in self.hidden, self.slowa)
		words = filter(lambda w:len(self.options[w])>0, words)
		if len(words)<1:
			return None
		highest_score = max([max(self.options[w].keys()) for w in words])
		words = filter(lambda w:highest_score in self.options[w], words)
		
		flexibility=lambda w:sum([len(o[1]) for o in self.options[w][highest_score] ])
		words = sorted(words, key=len, reverse=True)
		words = sorted(words, key=flexibility)
		words.reverse()
		print words
		return words[0]


	# ukrych slowa
	def hide(self, words):
		words = filter(lambda w:re.findall('[()-]', w) == [], words)
		self.slowa = [slowo for slowo in words]
		# statistics
		for word in self.slowa:
			for gloska in word.lower():
				self.czestoscie[gloska]+=1
		self.czestoscie[' ']=0
		ogolem=sum(self.czestoscie.values())
		self.prawdopodobienstwa={gloska:float(self.czestoscie[gloska])/ogolem 
			for gloska in alfabet}

		#popular=lambda x:sum([self.czestoscie[g.lower()] for g in x])
		
		#self.compute_positions()
		scoring=lambda x:max(0,self.options[x].keys())
		while len(self.hidden)<len(self.slowa):
			self.compute_positions()
			words=[w for w in self.slowa if not w in self.hidden]
			word = self.best_placable()
			print 'Ukryję słowo', word
			self.ukryc_slowo(word)

		
		
	def compute_positions(self):
		for word in filter(lambda x:not x in self.hidden, self.slowa):
			todo=filter(lambda x: not x in self.hidden, self.slowa)
			pos={}
			kierunki={}
			for row in range(0, self.szerokosc):
				for col in range(0, self.wysokosc):
					score = len(self.kierunki_ukryte)
					for kier in self.kierunki_ukryte:
						crossing = self.odpowiedni(word.lower(), (col, row), kier)
						score += crossing
						if crossing > -1:
							kierunki[(col,row)]=kierunki.get((col, row), [])+[kier]
					pos[score] = pos.get(score,[])+[(col,row)]
			print 'Evaluating: ', word, 
#			for score in pos.keys():
#				if score > -3:
#					print u'{0}-star spots: {1}{2}'.format(score, pos[score][:3],
#						('.', '...')[len(pos[score])>3])
			pos = {s:[(p,kierunki[p]) for p in pos[s]] 
				for s in pos.keys() if s > 0}
			#for score in pos.keys():
				#if score > -3:
					#print u'{0}-star spots: {1}{2}'.format(score, pos[score][:3],
						#('.', '...')[len(pos[score])>3])
			if len(pos)>0:
				print '*'*max(pos.keys())
			else:
				print
			self.options[word] = pos 
		self.slowa = filter(lambda w:len(self.options[w])>0, self.slowa)
					
	# picks what seems to be the best choice of placement for this word
	def pick_position(self, slowo):
		print 'pick one of best places for', slowo
		#TODO: best direction
		pos=self.options[slowo]
		if len(pos.keys())>0:
			best_score=max(pos.keys())
			pos = pos[best_score]
			print 'options: ', pos
			if len(pos)<1:
				return (None, None, None)
			shuffle(pos)
			pos, kierunki = pos.pop(0)
			if best_score>0:
				shuffle(kierunki)
				kierunki=kierunki.pop(0)
			else:
				kierunki=0
			return (pos, kierunki, best_score)
		else:
			return (None, None, None)
		
	# hide single word
	def ukryc_slowo(self, slowo): #hide word
		arg_slow=slowo
		if slowo:
			if '-' in arg_slow:
				print "Omit word for illegal character: ", arg_slow
				self.slowa.remove(arg_slow)
				return
		else:
			return
		position, kier, score = self.pick_position(slowo)
		print position, kier, score
		if position and score>0:
			print u'place {0} at {1}.\n'.format(slowo, position)
			self.pisac(arg_slow, position, kier)
			return
		print "ERROR: could not place word: ", arg_slow
		self.slowa.remove(arg_slow)
					
					


	# determine whether a word fits at a given position with certain
	# alignment
	def odpowiedni(self, slowo, pozycja, kierunek):
		if self.gloska_w(self.isc_tylem(pozycja, kierunek, 1))[1] == kierunek:
			return -1		
		col, row = pozycja
		matches=0
		for gloska in slowo:
			g, k, _ = self.gloska_w((col, row))
			if k>15:
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
	def pisac(self, slowo, pozycja, kierunek):
		col, row = pozycja
		for gl in slowo.lower():
			self.ukryc_gloske(gl, (col, row), kierunek)
			self.part_of[row][col] += [slowo]
			col += kierunek & 1 # move right if lowest bit is set
			row += kierunek / 2 & 1 # move down if second bit is set
			col -= kierunek / 4 & 1 # move left if third bit is set
			row -= kierunek / 8 & 1 # move up if fourth bit is set
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
		res+=tex.format(self.szerokosc, sublabel)
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
					tex+=u'\t\t\\item \\underline{{{0}\\hspace{{.07\\linewidth}}}}\n'.format(
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
	#words=sorted(words, key=len)
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
		score=lambda x:sum([fits((x+' ')[i:-i-1]) for i in range(0,len(x)/2)])
		while len(sub)<limit:
			likes=sorted(words, key=score, reverse=True)
			while likes[0] in sub:
				likes.pop(0)
			like=likes[0]
			sub+=[like]
			seed+=like
		#for s in sub:
		#	print s
		#exit()
		return sorted(sub)
	else:
		return words
	
# return new instance
# filename: file containing word list (one per line)
# words: optional word list
# limit: for very long list files, limit to random subset
def zagadka(width, height, filename=None, words=None, title=None,
	limit=None):
	if filename:
		word_list=load(filename, maxlen=max(width, height))
	if word_list:
		recall=0
		while recall<.8:
			words=wordset(word_list, limit)
			#if filename:
			#	words=load(filename, limit, max(width, height))
			puzzle = Zagadka(width, height, title=title)
			puzzle.density+=recall/3
			puzzle.hide(words)
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

liczba = codecs.open('liczba', encoding='utf-8')
liczba=[liczbo.strip() for liczbo in liczba]

kierunki=[1,2,3]

zagadka(4, 4,filename='slowa/miastami_polskimi',
	title=u"Miasta", limit=5)
Zagadka.instances[-1].add_description(u'Jest niska.')

#zagadka(30,20,filename='slowa/warzywa',title="Warzywa")
#zagadka(23,16,filename='slowa/owoce',title="Owoce")
#Zagadka.instances[-1].add_description(
#	u'Jakie są te smaczne i zdrowe owocowy?')
#Zagadka.instances[-1].przyklad()
#Zagadka.instances[-1].przyklad()
#zagadka(20,13,filename='slowa/czasowniki',title="Czasowniki")
#zagadka(25,17,filename='slowa/czasowniki2',title="Czasowniki - Koniugacja")
#zagadka(34,28,filename='slowa/bardzo_dlugo_exc2',
#	title=u"Bardzo długa słowa")
#Zagadka.instances[-1].kierunki_ukryte+=[9]
#Zagadka.instances[-1].add_description(
#	u'Ta jest bardzo trudna! Słowa są długo i dużo.')
#zagadka(34, 28,filename='slowa/miastami_polskimi',
#	title=u"Miastami polskimi", limit=45)
#zagadka(10, 7,filename='slowa/miastami_polskimi',
#	title=u"Miastami polskimi 2", limit=15)
#Zagadka.instances[-1].add_description(u'Jest łatwa.')

save_tex('zagadki.tex')

for puzzle in Zagadka.instances:
	puzzle.solve()
	
save_tex('zagadki_napisalismy.tex')
