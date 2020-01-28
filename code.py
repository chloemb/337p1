import nltk, string as str, re, json, urllib.request, sys, time, unidecode
from bs4 import BeautifulSoup

import gg_api

# WE MAY NEED TO UNCOMMENT THIS?
# nltk.download('averaged_perceptron_tagger')

start_time = time.time()

print("NEW RUN \n\n\n")

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

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

def find_next_award_hardcoded(pairs):
    return 0


def actor_name(name):
    # found urllib.request and BeautifulSoup packages from the repo cited below
    # citation: https://github.com/rkm660/GoldenGlobes/blob/master/gg.py

    # take the url for a search by a particular name

    # remove punctuation, accents, replace spaces with +
    name = re.sub(r'[^\w\s]', '', name)
    name = unidecode.unidecode(name)
    url = "https://www.imdb.com/find?q="+name.replace(" ", "+")+"&s=nm&exact=true&ref_=fn_nm_ex"

    # search
    red = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(red, features="lxml")
    existence = soup.find_all("tr", {"class": "findResult odd"})
    actor = ""
    if len(existence) > 1:
        actor = existence[0].find_all("a")[1].string
    # else:
    #     print("Not an Actor")
    # print(actor)
    return actor


# actor_name("jared leto")

def main_loop():
    ignore_as_first_char = ('@', '#')
    counter1 = 0
    for line in tweets:
        # first, run part-of-speech tagger
        parsed = nltk.tag.pos_tag(line['text'].split())

        counter1 += 1

        # next, remove words that start with anything in ignore_as_first_char
        clean_parsed = []

        for pair in parsed:
            if not pair[0].startswith(ignore_as_first_char):
                clean_parsed.append(pair)

        # now, match proper nouns to verbs
        counter = 0
        length = len(clean_parsed)
        while counter < length:
            # find every group of words labeled NNP
            if clean_parsed[counter][1] == 'NNP':
                this_NNP_phrase = ""
                potential_actor, noun_len = full_nnp(clean_parsed[counter: length])
                counter += noun_len
                # print("proper noun found:", this_phrase)
                # find the next verb for each NNP group
                next_verb, verb_ind = find_next_verb(clean_parsed[counter: length])
                if next_verb != "":
                    this_NNP_phrase += potential_actor + " " + next_verb
                    new_counter = counter + verb_ind

                    # find the next group of nouns starting with 'best'
                    award = find_next_award(clean_parsed[new_counter: length])
                    if award != "":
                        # check if it's a real actor's name
                        this_actor = actor_name(potential_actor)
                        if this_actor != "":
                            # print(this_phrase, "returns as actor:", this_actor)
                            this_NNP_phrase += " " + award
                            print(this_NNP_phrase)
            counter += 1

        if counter1 == 20000:
            end_time = time.time()
            print("Runtime:", counter1, "tweets in", end_time - start_time, "seconds")
            sys.exit()

main_loop()