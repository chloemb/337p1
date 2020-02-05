import json


def read_json(year):
    tweets = []
    # for line in open('gg%s.json' % year, 'r', encoding='utf8'):
    #     print("found line")
    #     tweets.append(json.loads(line))

    with open('gg%s.json' % year, 'r', encoding='utf8') as all_tweets:
        tweets = json.load(all_tweets)
    return tweets
