import nltk, numpy as np
import json
import sys

nltk.download('averaged_perceptron_tagger')

tweets=[]
for line in open('gg2020.json','r', encoding='utf8'):
	tweets.append(json.loads(line))

propers=[]
for line in tweets:
	#parsed = nltk.tokenize(line['text'])
	#print(parsed)
	parsed = nltk.tag.pos_tag(line['text'].split())
	print(type(parsed[0]))

	sys.exit()
