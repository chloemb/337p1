import nltk, string as str
import json
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
		if pairs[counter][1].startswith(('VB', 'VBZ', 'VBN', 'VBG', 'VBD')):
			# print(0)
			# print("found a verb", pairs[counter][0])
			return pairs[counter][0]
		counter += 1
	return ""


def full_nnp(pairs):
	counter = 0
	name = ""
	while counter < len(pairs) and pairs[counter][1] == 'NNP':
		name += " " + pairs[counter][0]
		counter += 1
	return name, counter


ignore_as_first_char = ('@', '#')

propers=[]

awardnames=set()
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
			if "best" in this_phrase or "Best" in this_phrase:
				awardnames.add(this_phrase)
			counter += noun_len
			# print("found proper noun", this_phrase)
			next_verb = find_next_verb(clean_parsed[counter: length])
			if next_verb != "":
				this_phrase += " " + next_verb
				print(this_phrase)
		counter += 1

print(awardnames)

	# groups = groupby(clean_parsed, key=lambda x: x[1])  # Group by tags
	# names = [[w for w, _ in words] for tag, words in groups if tag == "NNP"]
	# names = [" ".join(name) for name in names if len(name) >= 2]
	# print(names)
