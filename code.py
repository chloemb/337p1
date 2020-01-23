import nltk, numpy as np
import json

tweets=[]
for line in open('gg2020.json','r', encoding='utf8'):
	tweets.append(json.loads(line))



print(tweets[100])