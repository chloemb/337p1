import nltk, string as str
import json
import sys
from itertools import groupby

# nltk.download('averaged_perceptron_tagger')

print("NEW RUN \n\n\n")

tweets=[]
for line in open('gg2020.json','r', encoding='utf8'):
	tweets.append(json.loads(line))



ignore_as_first_char = ['@', '#']

propers=[]
counter = 0
for line in tweets:
	#parsed = nltk.tokenize(line['text'])
	#print(parsed)
	parsed = nltk.tag.pos_tag(line['text'].split())

	counter += 1

	clean_parsed = []

	for pair in parsed:
		if pair[0].startswith(any(ignore_as_first_char)):
			clean_parsed.append(pair)

	groups = groupby(clean_parsed, key=lambda x: x[1])  # Group by tags
	names = [[w for w, _ in words] for tag, words in groups if tag == "NNP"]
	names = [" ".join(name) for name in names if len(name) >= 2]
	print(names)


	if counter == 5:
		sys.exit()
