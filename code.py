import nltk, string as str
import json
import urllib.request
from bs4 import BeautifulSoup
import sys
from itertools import groupby

# nltk.download('averaged_perceptron_tagger')

print("NEW RUN \n\n\n")

tweets=[]
for line in open('gg2020.json','r', encoding='utf8'):
    tweets.append(json.loads(line))

def find_next_verb(pairs):
    # print("finding next verb from", pairs)
    counter = 0
    while counter < len(pairs):
        if pairs[counter][1].startswith('VB'):
            # print(0)
            # print("found a verb", pairs[counter][0])
            return pairs[counter][0], counter
        counter += 1
    return "", counter


def full_nnp(pairs):
    counter = 0
    name = ""
    while counter < len(pairs) and pairs[counter][1] == 'NNP':
        name += " " + pairs[counter][0]
        counter += 1
    return name, counter


def find_next_award(pairs):
    counter = 0
    award = ""
    while counter < len(pairs):
        if pairs[counter][0] == 'best' or pairs[counter][0] == 'Best':
            while counter < len(pairs) and pairs[counter][1].startswith('N'):
                award += " " + pairs[counter][0]
                counter += 1
            return award
        counter += 1
    return award


def actor_name(name):
    #found urllib.request and BeautifulSoup packages from the repo cited below
    #citation: https://github.com/rkm660/GoldenGlobes/blob/master/gg.py

    #take the url for a search by a particular name
    url = "https://www.imdb.com/find?s=nm&q="+name.replace(" ", "+")+"&ref_=nv_sr_sm"
    red = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(red, features="lxml")
    existence = soup.find_all("tr", {"class": "findResult odd"})
    actor = ""
    if len(existence) > 1:
        actor = existence[0].find_all("a")[1].string
    else:
        print("Not an Actor")
    print(actor)


actor_name("jared leto")

ignore_as_first_char = ('@', '#')

propers=[]
counter = 0
for line in tweets:
    #parsed = nltk.tokenize(line['text'])
    #print(parsed)

    # first, run part-of-speech tagger
    parsed = nltk.tag.pos_tag(line['text'].split())

    counter += 1

    # next, remove words that start with anything in ignore_as_first_char
    clean_parsed = []

    for pair in parsed:
        if not pair[0].startswith(ignore_as_first_char):
            clean_parsed.append(pair)

    # now, match proper nouns to verbs
    counter = 0
    length = len(clean_parsed)
    while counter < length:
        if clean_parsed[counter][1] == 'NNP':
            this_phrase, noun_len = full_nnp(clean_parsed[counter: length])
            counter += noun_len
            # print("found proper noun", this_phrase)
            next_verb, verb_ind = find_next_verb(clean_parsed[counter: length])
            if next_verb != "":
                this_phrase += " " + next_verb
                new_counter = counter + verb_ind
                award = find_next_award(clean_parsed[new_counter: length])
                if award != "":
                    this_phrase += " " + award
                    print(this_phrase)
        counter += 1


    # groups = groupby(clean_parsed, key=lambda x: x[1])  # Group by tags
    # names = [[w for w, _ in words] for tag, words in groups if tag == "NNP"]
    # names = [" ".join(name) for name in names if len(name) >= 2]
    # print(names)


    # if counter == 50:
    # 	sys.exit()