import nltk, string as str, re, json, urllib.request, sys, time, unidecode
from bs4 import BeautifulSoup

import gg_api

# WE MAY NEED TO UNCOMMENT THIS?
# nltk.download('averaged_perceptron_tagger')

start_time = time.time()
#print("wtf")
print("NEW RUN \n\n\n")

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

tweets=[]
searched_pairs=[]
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
        name += " " + depunctuate(pairs[counter][0])
        counter += 1
    #print(name)
    return name, counter

def depunctuate(stringy):
    return stringy.partition(".")[0].partition(',')[0].partition("!")[0].partition("?")[0].partition("http")[0]

def find_next_award(pairs):
    counter = 0
    award = ""
    while counter < len(pairs):
        if pairs[counter][0] == 'best' or pairs[counter][0] == 'Best':
            while counter < len(pairs) and pairs[counter][1].startswith('N'):
                award += " " + pairs[counter][0]
                counter += 1
            return depunctuate(award)
        counter += 1
    return depunctuate(award)

def find_next_award_hardcoded(pairs):
    return 0


def actor_name(name):
    #print("This ran somehow???")
    # found urllib.request and BeautifulSoup packages from the repo cited below
    # citation: https://github.com/rkm660/GoldenGlobes/blob/master/gg.py

    # take the url for a search by a particular name

    # remove punctuation, accents, replace spaces with +
    name = re.sub(r'[^\w\s]', '', name)
    name = unidecode.unidecode(name)
    #Add movies later
    for trial, match in searched_pairs:
        if trial == name:
            return match
    url = "https://www.imdb.com/find?s=nm&q="+name.replace(" ", "+")+"&ref_=nv_sr_sm"

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
    searched_pairs.append((name,actor))
    return actor

masterlist=[]
def update_master(award,person,verb):
    #print("updating")
    for listaward,presenters,actors in masterlist:
        if award == listaward:
            if "present" in verb or "host" in verb or "announ" in verb:
                for presenter,instances in presenters:
                    if presenter ==person:
                        instances+=1
                        return
                presenters.append((person,1))
                return
            actors.add(person)
            return
    if "present" in verb or "host" in verb or "announ" in verb:
        masterlist.append((award,[(person,1)],set()))
    else:
        actorset=set()
        actorset.add(person)
        masterlist.append((award,[],actorset))

def main_loop():
    print("start")
    ignore_as_first_char = ('@', '#')
    counter1 = 0
    for line in tweets:
        new_trio = []
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
            #print(counter1)
            # find every group of words labeled NNP
            if clean_parsed[counter][1] == 'NNP':
                potential_actor, noun_len = full_nnp(clean_parsed[counter: length])
                counter += noun_len
                # print("proper noun found:", this_phrase)
                # find the next verb for each NNP group
                next_verb, verb_ind = find_next_verb(clean_parsed[counter: length])
                if next_verb != "":
                    if "present" not in next_verb and "win" not in next_verb and "announ" not in next_verb and "won" not in next_verb and "host" not in next_verb and "accept" not in next_verb:
                        counter+= 1
                        break
                    new_counter = counter + verb_ind

                    # find the next group of nouns starting with 'best'
                    award = find_next_award(clean_parsed[new_counter: length])
                    if award != "":
                        # check if it's a real actor's name
                        try:
                            this_actor = actor_name(potential_actor)
                        except:
                            break
                        if this_actor != "":
                            # print(this_phrase, "returns as actor:", this_actor)
                            update_master(award,this_actor,next_verb)
            counter += 1

        if counter1 == 138000:
            end_time = time.time()


            print("Runtime:", counter1, "tweets in", end_time - start_time, "seconds")
            print(masterlist)
            sys.exit()

main_loop()