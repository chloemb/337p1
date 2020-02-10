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
import cProfile

start_time = time.time()

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

people_awards = []
real_awards = []

# WE MAY NEED TO UNCOMMENT THIS?
# nltk.download('averaged_perceptron_tagger')

# print("\n\n\nNEW RUN")

searched_pairs = []
searched_people = []
searched_media = []

mentions = {}

not_person = []
not_movie = []

basic_names = []
basic_titles = []

masterlist = []

badawardnames=dict()
def list_actors():
    with open("new_name_updated.tsv") as basics:
        for line in basics:
                basic_names.append(line.lower().split('\n')[0])


def list_movies():
    with open("new_title_updated.tsv") as basics:
        for line in basics:
                basic_titles.append(line.lower().split('\n')[0])


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

def find_next_award_maria(pairs, best_index):
    counter = 0
    award = []
    while counter < len(pairs)-best_index:
        if pairs[counter+best_index-1][0] == 'cecil':
            return ['cecil']
        if pairs[counter+best_index-1][0] == 'best':
            award = ['best']
            # counter += 1
            removeything = 0
            while counter < len(pairs)-best_index and pairs[counter+best_index][1] in ['RBS','NN','VBG', 'JJS', 'IN']:
                award.append(depunctuate(pairs[counter+best_index][0]))
                if pairs[counter+best_index][1] in ['IN','RBS','VBG','JJS']:
                    removeything+=1
                else:
                    removeything=0
                counter += 1
            award = award[:len(award)-removeything-1]
            return award
        counter += 1
    return award

def full_nnp(pairs):
    counter = 0
    # print("here?", len(pairs),pairs[counter][1])
    name = []
    while counter < len(pairs) and pairs[counter][1] == 'NNP':
        name.append(depunctuate(pairs[counter][0]))
        # print(name)
        counter += 1
    # print(name)
    name = ' '.join(name)
    return name, counter


def depunctuate(stringy):
    return stringy.partition(".")[0].partition(',')[0].partition("!")[0].partition("?")[0].partition("http")[0]


def find_next_award(pairs, best_index):
    counter = 0
    award = []
    while counter < len(pairs)-best_index:
        if pairs[counter+best_index-1][0] == 'cecil':
            return ['cecil']
        if pairs[counter+best_index-1][0] == 'best':
            award = ['best']
            # counter += 1
            while counter < len(pairs)-best_index and pairs[counter+best_index][1].startswith(('N', 'VB', 'JJ')):
                award.append(depunctuate(pairs[counter+best_index][0]))
                counter += 1
            # print("returning award", award)
            return award
        counter += 1
    return award


def find_next_award_hardcoded(pairs, best_index):
    # find closest official award name
    tweet = [pair[0] for pair in pairs]
    raw_award = find_next_award(pairs, best_index)
    # print("JUST FOUND AN AWARD:", raw_award, "from", tweet)
    found = False

    keywords = ("drama", "musical", "comedy", "picture", "series", "tv", "television", "motion", "movie")
    contained_keywords = []
    for keyword in keywords:
        if keyword in tweet:
            contained_keywords.append(keyword)
    if contained_keywords:
        for keyword in contained_keywords:
            if keyword not in raw_award:
                raw_award.append(keyword)

    raw_award = ' '.join(raw_award)

    for real_award in real_awards:
        potential_award = combine_award(raw_award, real_award)
        if potential_award:
            raw_award = potential_award
            found = True
            break
    if not found:
        return False
    return raw_award


def industry_name(name):
    # searches through the imdb database of actors names, name.basics.tsv which is found at https://datasets.imdbws.com/
    # print(searched_people)

    if name in not_person:
        return "not found"
    if name in searched_people:
        return name
    if name in basic_names:
        searched_people.append(name)
        return name

    not_person.append(name)
    return "not found"


def media_name(title):
    # searches through the imdb database of film names, title.akas.tsv which is found at https://datasets.imdbws.com

    if title in not_movie:
        return "not found"
    if title in searched_media:
        return title
    if title in basic_titles:
        searched_media.append(title)
        return title

    not_movie.append(title)
    return "not found"


def combine_award(name1, name2):
    if name1.lower() == name2.lower():
        return name1.lower()
    if len(name1) >= len(name2):
        big = name1.lower()
        smol = name2.lower()
    else:
        big = name2
        smol = name1

    prominent_synonyms = [("tv", "television", "series"), ("motion", "picture", "film", "movie")]

    smolwords = smol.split()
    bigwords = big.split()
    for smolword in smolwords:
        matched = False
        for bigword in bigwords:
            if any(bigword in syn_list and smolword in syn_list for syn_list in prominent_synonyms):
                matched = True
                break
            if smolword == bigword:
                matched = True
                break
            # if edit_distance(smolword, bigword, transpositions=True) < 3:
            #     matched = True
            #     break
        if not matched:
            return False
    return big


def can_combine_item_set(item, answers):
    for set_item in answers:
        can_combine = combine_award(item, set_item)
        if can_combine:
            return can_combine
    return item


def update_master(award, item, verb):
    present_verbs = ("present", "host", "announ")
    win_verbs = ("won", "win", "accept", "receive", "award", "got", "get")

    if any(word in verb for word in present_verbs) or award in people_awards:
        # print(award, verb, "is a person")
        item = industry_name(item)
    else:
        # print(award, verb, "is a movie")
        # print("searching for movie", item)
        item = media_name(item)
        # print(item)

    if item == "not found":
        return

    for listaward, presenters, nominees, winners in masterlist:
        if award == listaward:
            if any(word in verb for word in present_verbs):
                item = can_combine_item_set(item, presenters)
                try:
                    presenters[item] += 1
                except:
                    presenters[item] = 1
                return

            nom_item = can_combine_item_set(item, nominees)
            try:
                nominees[nom_item] += 1
            except:
                nominees[nom_item] = 1

            if any(word in verb for word in win_verbs):
                item = can_combine_item_set(item, winners)
                try:
                    winners[item] += 1
                except:
                    winners[item] = 1
            return

    newdict = dict({item: 1})
    if any(word in verb for word in present_verbs):
        # newset = set()
        # newset.add(item)
        masterlist.append((award, newdict, dict(), dict()))
        return
    if any(word in verb for word in win_verbs):
        # newdict = dict()
        # newdict[item] = 1
        masterlist.append((award, dict(), newdict, newdict))
    else:
        # newdict = dict()
        # newdict[item] = 1
        masterlist.append((award, dict(), newdict, dict()))


def main_loop(year, these_awards):
    print("start")
    tweets = read_json.read_json(year)
    print(len(tweets))
    ignore_as_first_char = ('@', '#', 'RT')
    tweet_counter = 0

    list_actors()
    print("listed actors in", time.time() - start_time)
    # print("basic names", basic_names)
    list_movies()
    print("listed movies in", time.time() - start_time)

    for award in these_awards:
        if any(people_word in award for people_word in ("perform", "direct", "cecil")):
            people_awards.append(award)
        real_awards.append(award)

    for line in tweets:
        if tweet_counter % 10000 == 0:
            print(tweet_counter)

        if tweet_counter == len(tweets) - 1:
            # print("ending")
            nominees, winners, presenters, hosts = wrapup()
            end_time = time.time()
            # print(nominees, winners, presenters)
            # print("NOMINEES:", nominees)
            # print("WINNERS:", winners)
            # print("PRESENTERS:", presenters)
            # print("MENTIONS:", mentions)
            print("RUNTIME:", end_time - start_time, "seconds. (", (end_time - start_time) / 60, "minutes.)")
            return nominees, winners, presenters, hosts

        if not any(cont_word in line['text'].lower() for cont_word in ("best", "cecil", "monologue")):
            tweet_counter += 1
            continue

        monologue = True if "monologue" in line['text'].lower() else False

        cleaned = []
        for word in line['text'].split():
            if not word.startswith(ignore_as_first_char):
                cleaned.append(word)

        tagged = nltk.tag.pos_tag(cleaned)

        lower_tagged = [(item[0].lower(), item[1]) for item in tagged]
        # print(clean_parsed)

        congrats_found = False

        for i in lower_tagged:
            if "ongrat" in i[0]:
                congrats_found = True

        # print(lower_tagged)

        # now, match proper nouns to verbs
        length = len(lower_tagged)
        counter = 0
        while counter < length:
            # find every group of words labeled NNP

            if lower_tagged[counter][1] == 'NNP' and "ongrat" not in lower_tagged[counter][0]:
                potential_item, noun_len = full_nnp(lower_tagged[counter: length])
                counter += noun_len

                # try:
                #     mentions[potential_item] += 1
                # except:
                #     mentions[potential_item] = 1

                if monologue:
                    # pot_host = industry_name(potential_item)
                    # if pot_host != "not found":
                    try:
                        mentions[potential_item] += 1
                    except:
                        mentions[potential_item] = 1
                    continue

                # find the next verb for each NNP group
                next_verb, verb_ind = find_next_verb(lower_tagged[counter: length])
                if next_verb != "":
                    if not any(word in next_verb for word in (("won", "win", "accept", "receive", "award", "got",
                                                               "get", "present", "announ", "honor"))):
                        counter += 1
                        break
                    new_counter = counter + verb_ind + 1

                    # find the next group of nouns starting with 'best'
                    badaward = find_next_award_maria(clean_parsed,new_counter)
                    newbadaward = ""
                    for word in badaward:
                        newbadaward=newbadaward+word+" "
                    try:
                        badawardnames[newbadaward] += 1
                    except:
                        badawardnames[newbadaward] = 1

                    award = find_next_award_hardcoded(lower_tagged, new_counter)
                    # print("found award", award)
                    if award:
                        # print("updating master", award, potential_item, next_verb)
                        update_master(award, potential_item, next_verb)
                        if congrats_found:
                            update_master(award, potential_item, next_verb)
            else:
                counter += 1

        tweet_counter += 1


def wrapup():
    newbadawards=dict()
    for award,counter in badawardnames.items():
        matched = False
        for otheraward,othercounter in newbadawards.items():
            try:
                newbadawards[combine_award(award, otheraward)]
                matched = True
                othercounter += counter
                break
            except:
                if combine_award(award,otheraward) == award:
                    matched = True
                    newbadawards.pop(otheraward)
                    newbadawards[award]=counter + othercounter
                    break
        if not matched:
            newbadawards[award] = counter
    removelist=[]
    for award, counter in newbadawards.items():
        if counter ==1:
            removelist.append(award)
    for award in removelist:
        newbadawards.pop(award)
    print(newbadawards)
    print("wrapping up", time.time()-start_time)
    # print("MASTER LIST IS", masterlist)
    cutoff_symbols =[",",".","!","?","http","www"]

    # print("MASTERLIST IS", masterlist)

    nominees_dict = {}
    winners_dict = {}
    presenters_dict = {}

    sorted_men = sorted(mentions.items(), key=lambda x: x[1], reverse=True)
    final_men = []
    host_count = 0
    host_search_index = 0
    while host_count < 2:
        pot_host = industry_name(sorted_men[host_search_index][0])
        if pot_host != "not found":
            final_men.append(pot_host)
            host_count += 1
        host_search_index += 1

    pythonwhy = []
    for award, presenters, nominees, winners in masterlist:
        final_winner = []
        final_noms = []
        final_pres = []

        if winners.items():
            most = (0, 0)
            for winner, count in winners.items():
                if most == (0, 0):
                    most = (winner, count)
                if count > most[1]:
                    most = (winner, count)
                nominees[winner] = count
            final_winner = most[0]
        if nominees.items():
            if nominees.get(final_winner):
                del nominees[final_winner]
            if len(nominees) >= 4:
                sorted_noms = sorted(nominees.items(), key=lambda x: x[1], reverse=True)
                final_noms = list(pair[0] for pair in sorted_noms)[:4]
            else:
                final_noms = list(nominees.keys())
        if presenters.items():
            if len(nominees) >= 2:  # SHOULD THIS STAY LIKE THIS?
                sorted_pres = sorted(presenters.items(), key=lambda x: x[1], reverse=True)
                final_pres = list(pair[0] for pair in sorted_pres)[:2]
            else:
                final_pres = list(presenters.keys())

        pythonwhy.append((award, final_pres, final_noms, final_winner))

    for award, presenters, nominees, winner in pythonwhy:
        nominees_dict[award] = nominees
        winners_dict[award] = winner
        presenters_dict[award] = presenters

    return nominees_dict, winners_dict, presenters_dict, final_men

