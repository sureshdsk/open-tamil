# -*- coding: utf-8 -*-
# (C) 2016 Muthiah Annamalai
# 
# This file is part of 'open-tamil' package tests
# 
from __future__ import print_function
from solthiruthi.suggestions import norvig_suggestor
from solthiruthi.dictionary import DictionaryBuilder, TamilVU
import tamil
import sys
import codecs 

TVU_dict = None
user_dict = set()

def speller(filename):
    global user_dict
    new_document = []
    data = codecs.open(filename,u"r",u"utf-8")
    lines = data.readlines()
    for line in lines:
        words = tamil.utf8.get_words( tamil.utf8.get_letters(line) )
        for word  in words:
            # FIXME : handle punctuation
            #word = filter( tamil.utf8.is_tamil_unicode_predicate, word )
            ok,suggs = check_word_and_suggest( word )
            if not ok:
                option = suggs[0]
                # take user input.
                # FIXME: User optiions to include DONTREPLACE/KEEP, DELETE WORD, etc.
                option_str = u",".join( [ u"%d) %s"%(itr,wrd) for itr,wrd in enumerate(suggs)] )
                print(u"In line, \"%s\""%line.strip())
                
                print(u" Replace word %s \n\t Options => %s\n"%(word, option_str))
                try:
                    choice = input(u"option [-1 ignore, 0-%d replace]: "%(len(suggs)-1))
                    if choice == -1:
                        print(u"Not replacing word")
                        option = word
                        user_dict.add(word)
                    else:
                        option = suggs[choice]
                except Exception as ie:
                    print (str(ie))
                print(u" replacing word %s -> %s\n"%(word,option))
                new_document.append( unicode(option) )
            else:
                new_document.append( word )
        new_document.append(u"\n")
    print(u"*********** cleaned up document **********")
    print(u" ".join(new_document))
    

def check_word_and_suggest( word ): 
    global TVU_dict
    global user_dict
    letters = tamil.utf8.get_letters(word)
    in_user_dict = word in user_dict
    if in_user_dict or TVU_dict.isWord(word):
        return (True,[])
    
    # Consider splitting the word and see if it has 2 sub-words
    # e.g. செயல்பட => செயல் + பட
        
    # suggestions at edit distance 1
    norvig_suggests = filter( TVU_dict.isWord, norvig_suggestor( word, None, 1))
    combinagram_suggests = list(tamil.wordutils.combinagrams(word,TVU_dict)) 
    pfx_options = TVU_dict.getWordsStartingWith( u"".join( letters[:-1] ) )

    # FIXME: score  the options
    options = norvig_suggests
    options.extend( combinagram_suggests )
    options.extend( pfx_options )
    
    return (False, options )

def initialize():
    global TVU_dict
    TVU_dict,_ = DictionaryBuilder.create(TamilVU)

if __name__ == u'__main__':
    if len(sys.argv) < 2:
        print(u"usage: python spell.py <filename 1>  ... <filename n>")
        sys.exit(0)
    initialize()
    for file_name in sys.argv[1:]:        
        speller(file_name)