import json


def read_json(year):
    tweets = []
    # THIS IS CORRECT
    with open('gg%s.json' % year, 'r', encoding='utf8') as all_tweets:
        tweets = json.load(all_tweets)

    # THIS WORKS FOR 2020
    # for line in open('gg%s.json' % year, 'r', encoding='utf8'):
    #     tweets.append(json.loads(line))
    return tweets
