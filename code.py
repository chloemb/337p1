import nltk
import string as str
import re
import urllib.request
import sys
import time
import unidecode
from bs4 import BeautifulSoup
import read_json
from nltk.metrics import edit_distance

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']


# WE MAY NEED TO UNCOMMENT THIS?
# nltk.download('averaged_perceptron_tagger')

start_time = time.time()
# print("\n\n\nNEW RUN")

searched_pairs = []


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
    # print("here?", len(pairs),pairs[counter][1])
    name = ""
    while counter < len(pairs) and pairs[counter][1] == 'NNP':
        name += " " + depunctuate(pairs[counter][0])
        # print(name)
        counter += 1
    # print(name)
    return name, counter


def depunctuate(stringy):
    return stringy.partition(".")[0].partition(',')[0].partition("!")[0].partition("?")[0].partition("http")[0]


def find_next_award(pairs):
    counter = 0
    award = ""
    #print(counter, pairs)
    while counter < len(pairs):
        if pairs[counter][0] == 'best' or pairs[counter][0] == 'Best':
            #print("runs")
            award="Best"
            counter+=1
            #print("yo",counter, len(pairs), pairs[counter][1])
            while counter < len(pairs) and pairs[counter][1].startswith('N'):
                #print("follows:")
                award += " " + pairs[counter][0]
                #print(award)
                counter += 1
            return depunctuate(award)
        counter += 1
    return depunctuate(award)


def find_next_award_hardcoded(pairs):
    # find closest official award name
    raw_award = find_next_award(pairs)
    found = False
    for real_award in OFFICIAL_AWARDS_1315:
        potential_award = combine_award(raw_award, real_award)
        if potential_award:
            raw_award = potential_award
            found = True
            break
    if not found:
        return False
    return raw_award


def actor_name(name):
    # found urllib.request and BeautifulSoup packages from the repo cited below
    # citation: https://github.com/rkm660/GoldenGlobes/blob/master/gg.py

    # take the url for a search by a particular name

    # remove punctuation, accents, replace spaces with +
    name = re.sub(r'[^\w\s]', '', name)
    name = unidecode.unidecode(name)
    # Add movies later
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


def industry_name(name):
    # searches through the imdb database of actors names, name.basics.tsv which is found at https://datasets.imdbws.com/
    name = name.lower()
    with open("name.basics.tsv") as basics:
        for line in basics:
            if name in line.lower():
                return name
        return "Not A Relevant Person"


def media_name(title):
    # searches through the imdb database of film names, title.akas.tsv which is found at https://datasets.imdbws.com
    title = title.lower()
    with open("title.akas.tsv") as basics:
        for line in basics:
            if title in line.lower():
                return title
        return "Not A Movie"


def combine_award(name1, name2):
    if name1 == name2:
        return name1
    if len(name1) >= len(name2):
        big = name1
        smol = name2
    else:
        big = name2
        smol = name1

    prominent_synonyms = [("tv", "television", "series"), ("motion", "picture", "film", "movie")]

    smolwords = smol.split()
    bigwords = big.split()
    for smolword in smolwords:
        matched = False
        for bigword in bigwords:
            if bigword in prominent_synonyms[0] and smolword in prominent_synonyms[0] or bigword in prominent_synonyms[1] and smolword in prominent_synonyms[1]:
                matched = True
                break
            if edit_distance(smolword, bigword, transpositions=True) < 3:
                matched = True
                break
        if not matched:
            return False
    return big


masterlist = []


def update_master(award, person, verb):
    # print("updating",award,person,verb)

    for listaward, presenters, actors, winners in masterlist:
        if award == listaward:
            if any(word in verb for word in ("present", "host", "announ")):
                presenters.add(person)
                return
            if any(word in verb for word in ("won", "win", "accept", "receive", "award")):
                winners.append(person)
                return
            actors.add(person)
            return
    if any(word in verb for word in ("present", "host", "announ")):
        newset = set()
        newset.add(person)
        masterlist.append((award,newset,set(),[]))
    if any(word in verb for word in ("won", "win", "accept", "receive", "award")):
        masterlist.append((award, set(), set(),[]))
    else:
        actorset = set()
        actorset.add(person)
        masterlist.append((award, set(), actorset, []))


def main_loop(year):
    print("start")
    tweets = read_json.read_json(year)
    ignore_as_first_char = ('@', '#')
    tweet_counter = 0

    for line in tweets:
        # print(line)
        if tweet_counter == 50000:
            # print("ending")
            nominees, winners, presenters = wrapup()
            end_time = time.time()
            # print(nominees, winners, presenters)
            print("Runtime:", end_time - start_time, "seconds")
            return nominees, winners, presenters

        if "best" not in line['text'].lower():
            tweet_counter += 1
            continue

        clean_parsed = []
        parsed = nltk.tag.pos_tag(line['text'].split())
        
        for pair in parsed:
            if not pair[0].startswith(ignore_as_first_char):
                clean_parsed.append(pair)

        # now, match proper nouns to verbs
        length = len(clean_parsed)
        counter = 0
        while counter < length:
            # find every group of words labeled NNP

            if clean_parsed[counter][1] == 'NNP':
                potential_actor, noun_len = full_nnp(clean_parsed[counter: length])
                counter += noun_len

                # find the next verb for each NNP group
                next_verb, verb_ind = find_next_verb(clean_parsed[counter: length])
                if next_verb != "":
                    next_verb = next_verb.lower()
                    if not any(word in next_verb for word in ("present", "win", "announ", "won", "host", "accept")):
                        counter += 1
                        break
                    new_counter = counter + verb_ind

                    # find the next group of nouns starting with 'best'
                    award = find_next_award_hardcoded(clean_parsed[new_counter: length])
                    if award:
                        # check if it's a real actor's name
                        try:
                            this_actor = actor_name(potential_actor)
                        except:
                            break
                        if this_actor != "":
                            # print("updating master")
                            update_master(award, this_actor, next_verb)
            else:
                counter += 1

        tweet_counter += 1

    # wrapup()
    # end_time = time.time()
    # print("Runtime:", end_time - start_time, "seconds")


def wrapup():
    print("wrapping up", time.time()-start_time)
    # print("MASTER LIST IS", masterlist)
    cutoff_symbols =[",",".","!","?","http","www"]

    nominees_dict = {}
    winners_dict = {}
    presenters_dict = {}



    for award, presenters, nominees, winners in masterlist:
        for symbol in cutoff_symbols:
            if symbol in award:
                award = award.split(symbol)[0]
            for presenter in presenters:
                if symbol in award:
                    presenter = presenter.split(symbol)[0]
            for nominee in nominees:
                if symbol in nominee:
                    nominee = nominee.split(symbol)[0]
            combined_winners=[]
            searched_winners = []
            for winner in winners:
                newname = winner
                if symbol in winner:
                    newname = winner.split(symbol)[0]

        searched_winners=[]
        combined_winners=[]
        for winner in winners:
            if winner in searched_winners:
                continue
            searched_winners.append(winner)
            count = 0
            for swinner in winners:
                if swinner == winner:
                    count +=1
            combined_winners.append(winner,count)
        winners = combined_winners
                  

    awardlist=[]
    for award, presenters, nominees, winners in masterlist:
        append = True
        for premio, huespedes, nominados, ganadores in awardlist:
            if award.lower() in premio.lower():
                append = False
                huespedes = huespedes.union(presenters)
                nominados = nominados.union(nominees)
                for winner, count in winners:
                    ad = True
                    for ganador, conteo in ganadores:
                        if ganador in winner or winner in ganador:
                            ad = False
                            conteo += count
                    if ad:
                        ganadores.append((winner,count))
                break
            elif premio.lower() in award.lower():
                append = False
                premio = award
                huespedes = huespedes.union(presenters)
                nominados = nominados.union(nominees)
                for winner, count in winners:
                    ad = True
                    for ganador, conteo in ganadores:
                        if ganador in winner or winner in ganador:
                            ad = False
                            conteo += count
                    if ad:
                        ganadores.append((winner,count))
                break
        if append:
            # print("appending", award, presenters, nominees, winners)
            awardlist.append((award, presenters, nominees, winners))

    for award, presenters, nominees, winners in awardlist:
        if winners == []:
            winners = "unknown"
            continue
        most = (winners[0])
        for winner, count in winners:
            if count > most[1]:
                most =(winner,count)
            nominees. add(winner)
        winners = most[0]

    for award, presenters, nominees, winner in awardlist:
        nominees_dict[award] = nominees
        winners_dict[award] = winner
        presenters_dict[award] = presenters
        # print("Award:", award, "Presented by:", presenters, "Nominated:", nominees, "winner:", winner)

    return nominees_dict, winners_dict, presenters_dict

#main_loop(2013)
