# -*- coding: iso-8859-1 -*-
# LanguageTool -- A Rule-Based Style and Grammar Checker
# Copyright (C) 2004 ....
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# usage python stem.py
#
#  file test.txt contains are for example:
#   carried
#   worked
#    play
#
#  example aff file (dtest.aff)
# SFX D Y 4
# SFX D 0 e d             # abate->abated
# SFX D y ied [^aeiou]y   # carry -> carried
# SFX D 0 ed [^ey]        # work -> worked
# SFX D 0 ed [aeiuu]y     # play -> played
#
#  example dic file (dtest.dic)
# 3
# carry/D
# work/D
# play/D
#
# reads words from the file test.txt
#
# Speed up 9 times by helding different 
#  append endings in different arrays  3.July, 2004
#
#  Speed improvement by 30% by doing the above
#   also with the prefixes, and by helding
#   affixes and prefixes in different lists. 4. July, 2004
#

import array
import codecs
import os
import Tagger
from string import *
import time
import sys


#aff_file = "dtest.aff"
#dic_file = "dtest.dic"
test_file = "test.txt"
yesno = {}
comment = "#"
condlist = []
condlist1 = []
alfab_conddic = {}
palfab_conddic = {}
alfab_condlist_group = []
szodic = {}
typdic = {}

class Wfinder:

	encoding = "latin1"

	def __init__(self, textlanguage):
#		print time.strftime('%X %x %Z')
		self.is_initialized = 0
		self.textlanguage = textlanguage
		return

	def aff_read(self):
	 	self.aff_file = os.path.join(sys.path[0], "data", Tagger.affFile)
		condlist = []
		alfab_condlist_group = []
		faff = codecs.open(self.aff_file, "r", self.encoding)
		l = " "
		for i in range(0,256,1):
			alfab_conddic[i] = []
			palfab_conddic[i] = []
		while l != "":
  			l = faff.readline()
  			ll =  l.split()
  			if len(ll) <= 1:
  				continue
  			if ll[0][0] in comment:
				continue
			if ll[0][1:3] == "FX":
				arrname = ll[1]
				prefix = 0
				if ll[0][0] == 'P':
					prefix = 1
				yesno[arrname] = ll[2]
				for i in range(0, int(ll[3])):
					l = faff.readline()
					bb = l.split()
#					print "l:%s bb[2]:%s arrname:%s" %(l,bb[2], arrname)
					strip = bb[2]
					if bb[2] == '0':
						strip = '';
					appnd = bb[3]
					if bb[3] == '0':
						appnd = ''
						appnd_last = '0'
					else:
						if prefix == 0:
							appnd_last = appnd[-1]
						else:
							appnd_last = appnd[0]
					if bb[4] != '.':
						jj = 0
						while(jj < len(bb[4])):
							condarr = array.array('B',range(256))
							insbit = 1;
							for iii in range(0,256,1):
								condarr[iii] = 0
							if bb[4][jj] == '[':
								kk = 0;
								jj = jj + 1
								if bb[4][jj] == '^':
									jj = jj+1
									insbit = 0;
									for iii in range(0,256,1):
										condarr[iii] = 1
								while bb[4][jj] != ']':
									condarr[ord(bb[4][jj])] = insbit;
									jj = jj + 1
								if bb[4][jj] == ']':
									jj = jj +1
							else:
								condarr[ord(bb[4][jj])] = insbit;
								jj = jj +1
							condlist.append(condarr)
					alfab_condlist_group.append(condlist)
					alfab_condlist_group.append(strip)
					alfab_condlist_group.append(appnd)
					alfab_condlist_group.append(arrname)
					if prefix == 0:
						alfab_conddic[ord(appnd_last)].append(alfab_condlist_group)
					else:
						palfab_conddic[ord(appnd_last)].append(alfab_condlist_group)
#					print "appended %s to  %s %d" %(appnd.encode('latin1'), appnd_last.encode('latin1'), ord(appnd_last))
					condlist = []
					alfab_condlist_group = []
		faff.close()
#		for i in range (0,255,1):
#		  print len(alfab_conddic[i])
#		print alfab_conddic[ord('a')]

#
# Now read the dictionary
#
	def dic_read(self):
	 	self.dic_file = os.path.join(sys.path[0], "data", Tagger.dicFile)
		szoszam = 0;
		fdic = codecs.open(self.dic_file, "r", self.encoding)
		l = " "
		szolista = []
		ujlista = []
		l = fdic.readline()
		szoszam = int(l)
		while l != "":
			l = fdic.readline()
			szolista = l.split("/")
			for szo in szolista:
				szo = szo.strip('\n \t')
				ujlista.append(szo)
			if len(ujlista) > 1:
				szodic[ujlista[0]] = ujlista[1]
			else:
				szodic[ujlista[0]] = ""
			if len(ujlista) > 2:
				typdic[ujlista[0]] = ujlista[2]
			else:
				typdic[ujlista[0]] = ""
			ujlista = []
		fdic.close()

	def do_keytest(self,l):
		if l == "":
			return ""
		if szodic.has_key(l):
			return "+ %s" %l
		else:
			return "- %s" %l

		
	def do_test(self,l):
		if l == "":
			return ""
		else:
#			print "not found %s" %l
			oldword = l
			found = 0
			for windex in ord(l[-1]), ord('0'):
				for elem in alfab_conddic[windex]:
# elem0: condlist, elem1: strip elem2 = append, elem3 = arrname 
					if found:
						break
			#
			#  search first only suffixes
			#  since prefix is optional
			#
					appnd    = elem[2]
					if len(appnd):
						if l[-len(appnd):] != appnd:
							continue
#					if len(appnd):
						restoredWord = l[0:len(l)-len(appnd)]
					else:
						restoredWord = l
					condlist = elem[0]
					strip    = elem[1]
					if len(strip):
						restoredWord = restoredWord + strip
					break_it = 0
					if len(condlist) > 0 and len(restoredWord) >= len(condlist): #tktk
						substr = restoredWord[-len(condlist):]
						for i in range(0, len(condlist), 1): #tktk
							if condlist[i][ord(substr[i])] != 1:
								break_it = 1
								break
						if break_it:
							continue
					if szodic.has_key(restoredWord):
						flags = szodic[restoredWord]
						if flags == "": # tktk
							continue
						else:
							if find(flags, elem[3]) == -1:
								continue
						return "++ %s %s" %(l,restoredWord)
						found = 1
						break
#
# searched all suffixes and not found
# now try to combine all prefixes with all suffixes
# that allow combinations
#
		if found:
			return "+found %s" %oldword
		for windex in ord(l[0]), ord('0'):
			for elem in palfab_conddic[windex]:
				if found:
					break
				appnd    = elem[2]
				if appnd == l[:len(appnd)]:  # cut the matching prefix
					l1 = l[len(appnd):]
				else:
					continue
				condlist = elem[0]
				strip    = elem[1]
				if len(strip):
					l1 = strip + l1
				break_it = 0
				if len(condlist) > 0 and len(l1) >= len(condlist): #tktk
					substr = l1[0:len(condlist)]
					for i in range(0, len(condlist), 1): #tktk
						if condlist[i][ord(substr[i])] != 1:
							break_it = 1
							break
					if break_it:
						continue
			#
			# prefix without suffix
			#
				arrname = elem[3]
				if szodic.has_key(l1):
					flags1 = szodic[l1]
					if flags1 != "":
						if find(flags1, arrname) == -1:
							continue
						return "++ %s  %s" %(l,l1)
						found = 1
						break
						
				if lower(yesno[arrname]) == 'n':
					continue
#
#			check if this unprefixed word 
#				is a valid suffixed one
#
				for windex1 in ord(l1[-1]), ord('0'):
					for elem1 in alfab_conddic[windex1]:
# elem0: condlist, elem1: strip elem2 = append, elem3 = arrname 
						if found:
							break
						arrname1 = elem1[3]
						if lower(yesno[arrname1]) == 'n':
							continue
						appnd1    = elem1[2]
						if len(appnd1):
							if l1[-len(appnd1):] != appnd1:
								continue
#						if len(appnd):
							restoredWord1 = l1[0:len(l1)-len(appnd1)]
						else:
							restoredWord1 = l1
						condlist1 = elem1[0]
						strip1    = elem1[1]
						if len(strip1):
							restoredWord1 = restoredWord1 + strip1
						break_it = 0
						if len(condlist1) > 0 and len(restoredWord1) >= len(condlist1): #tktk
							substr = restoredWord1[-len(condlist1):]
							for i1 in range(0, len(condlist1), 1): #tktk
								if condlist1[i1][ord(substr[i1])] != 1:
									break_it = 1
									break
							if break_it:
								continue
						if szodic.has_key(restoredWord1):
							flags1 = szodic[restoredWord1]
							if flags1 == "": # tktk
								continue
							else:
								if find(flags1, arrname1) == -1:
									continue
								if find(flags1, arrname) == -1:
									continue
							return "+++ %s %s %s" %(l, l1,restoredWord1)
							found = 1
							break
						
		if found == 0:
			return "- %s" % oldword

	def test_it(self,l):
		if self.is_initialized == 0:
			self.aff_read()
			self.dic_read()
			self.is_initialized = 1
		lcasetest = 0
		result = self.do_keytest(l)
		if result[0] == '-':
			lu = l[0]
			if lu != lu.lower():
				l1 = lu[0].lower()+l[1:]
				if l1 != l:
					lcasetest = 1;
					result = self.do_keytest(l1)
					#
					# in languages not German more likely to find
					# a lower case word than an uppercase
					#
					if result[0] == '-' and self.textlanguage != 'de':
						tmp = l1
						l1 = l
						l = tmp
		if result[0] == '-':
			result = self.do_test(l)
		if result[0] == '-' and lcasetest == 1:
			result = self.do_test(l1)
		typ = ''
		if result[0] != '-':
			src = result.split()
			word = src[len(src) - 1]
			oword = src[1]
			typ =  typdic[word]
#			print typ + " " + oword[-1:] + " " +oword[-2:]
#
# Here are the language specific rules of each language
#
			if self.textlanguage == 'de':
				if typ != "":
					if typ == 'V' or typ == 'HV':
						if oword[-4:] == 'ende' or oword[-5:-1] == 'ende':
							typ = 'ADJV'
					if typ == 'V' or typ == 'HV':
						if oword[-1:] == 'e':
							typ =  typ + '11'
						elif oword[-2:] == 'st':
							typ = typ + '12'
						elif oword[-2:] == 'en':
							typ = typ + '14'
						elif oword[-2:] == 'et':
							typ = typ + '15'
						elif oword[-1:] == 't':
							typ = typ + '13'
					elif typ == 'ADJ':
						if oword[-2:] == 'er':
							typ = 'ADJER'
						elif oword[-2:] == 'en':
							typ = 'ADJEN'
						elif oword[-2:] == 'em':
							typ = 'ADJEM'
						elif oword[-2:] == 'es':
							typ = 'ADJES'
						elif oword[-1:] == 'e':
							typ = 'ADJE'
					elif typ == 'NMS':
						if oword[-2:] == 'in':
							typ = 'NFS'
						elif oword[-5:] == 'innen':
							typ = 'NF'
					if typ[0] == 'N':
						if word != oword and typ[-1:] == 'S':
							typ = typ[0:-1]
			elif self.textlanguage == 'hu':
#				print word+" "+oword+" "+typ
				dif = len(oword) - len(word)
				if (typ[0] == 'V' or typ[0:2] == 'SI') and word != oword:
					ik = ''
					telo = 'SI'
					if typ[0] == 'V':
						telo = 'V'
					if oword[0:2] != word[0:2]:
						ik = 'IK'
					if oword[-3:]  in (u'i�k','iuk', 'nak', 'nek','tak', 'tek') or oword[-2:] in (u'�k', u'�k'):
						typ = ik + telo + '6'
					elif oword[-3:]  in ('tok','tek', u't�k'):
						typ = ik + telo + '5'
					elif oword[-3:]  in (u'�nk','unk', u'�nk', u'�nk') or oword[-2:] in ('uk', u'�k'):
						typ = ik + telo + '4'
					elif oword[-2:]  in ('sz','od', 'ed', u'�d',u'�d','ad',u'�d'):
						typ = ik + telo + '2'
					elif oword[-2:]  in ('ok','ek',u'�k','om','em',u'�m', u'�m', u'�m', 'am'):
						typ = ik + telo + '1'
					elif oword[-2:] in ('va', 've') or oword[-3:] in (u'v�n', u'v�n'):
						typ = 'ADV'
					elif oword[-2:]  == 'ni':
						typ = 'INF'
					else:
						typ = ik + telo + '3'
				elif typ[0:3] == 'PP4':
					if oword != 'mi':
						typ = 'ADV'
				elif typ[0:3] == 'ADJ':
					if oword[-2:]  in ('ek','ok', 'ak', u'�k', u'�k') and dif > 0 and (dif < 3 or ((word[0:1] != oword[0:1]) and dif < 9)):
						typ = 'ADJP'
					elif oword[-1:]  in (u'�',u'�') and dif > 0 and (dif < 5 or ((word[0:1] != oword[0:1]) and dif < 12)):
						typ = 'ADV'
					elif oword[-2:] in ('an', 'en', 'bb','ul',u'�l') and dif == 2:
						typ = 'ADV'
					elif dif != 0:
						typ = 'ADV'
				elif typ[0] == 'N':
					if oword[-2:]  in ('ek','ok', 'ak', u'�k', u'�k', u'�k',u'�k',u'�k',u'�k') and dif > 0 and dif < 3 :
						typ = 'NP'
					elif oword[-1:] == 'i' and dif == 1:
						typ = 'DNA'
					elif (oword[-1:] in(u'�', u'�') and dif == 1) or (oword[-2:] in (u'j�', u'j�')  and dif == 2):
						typ = 'ADJS'
					elif typ == 'N':
						if oword[-1] == 'k' and oword == word:
							typ = 'NP'
						else:
							typ = 'NS'
					elif  dif >= 2:
						typ = 'N'
				if typ[0] == 'N' and oword == word and word[-1] != 'k':
						typ = typ+'N'
#
# end of language specific rules for new languages
#
#			print typ
			result = result + " " + typ
#		print result
		return result


