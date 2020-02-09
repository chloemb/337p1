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

searched_people = []

searched_media = []

not_person = []

not_movie = []

basic_names = []

basic_titles = []

masterlist = []

people_awards = ['cecil b. demille award', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']


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
    while counter < len(pairs):
        if pairs[counter][0] == 'best' or pairs[counter][0] == 'Best':
            award = "Best"
            counter += 1
            while counter < len(pairs) and pairs[counter][1].startswith('N'):
                award += " " + pairs[counter][0]
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


def industry_name(name):
    # searches through the imdb database of actors names, name.basics.tsv which is found at https://datasets.imdbws.com/
    # print(searched_people)

    name = name.lower()
    if name.startswith(" "):
        name = name[1:]

    if name in not_person:
        return "not found"

    if name in searched_people:
        return name
    # for trial in potential_movies:
    #     if trial == name:
    #         return "not found"

    if name in basic_names:
        searched_people.append(name)
        return name
    # potential_movies.append(name)
    # print("didn't find", name)

    not_person.append(name)
    return "not found"


def media_name(title):
    # searches through the imdb database of film names, title.akas.tsv which is found at https://datasets.imdbws.com
    # print("SEARCHED MEDIA IS", searched_media)
    # print("searching for", title)

    title = title.lower()
    if title.startswith(" "):
        title = title[1:]
    # for trial in nothing:
    #     if trial == title:
    #         return "not found"

    if title in not_movie:
        return "not found"

    if title in searched_media:
        return title
    if title in basic_titles:
        searched_media.append(title)
        # print("found media named", title)
        return title
    # nothing.append(title)

    not_movie.append(title)
    return "not found"


def combine_award(name1, name2):
    if name1 == name2:
        return name1
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
            # if bigword in prominent_synonyms[0] and smolword in prominent_synonyms[0] or bigword in prominent_synonyms[1] and smolword in prominent_synonyms[1]:
                matched = True
                break
            if edit_distance(smolword, bigword, transpositions=True) < 3:
                matched = True
                break
        if not matched:
            return False
    return big


def can_combine_item_set(item, answers):
    for set_item in answers:
        can_combine = combine_award(item, set_item)
        if can_combine:
            # print("can combine", item, set_item, "into", can_combine)
            return can_combine
    return item


def update_master(award, item, verb):
    present_verbs = ("present", "host", "announ")
    win_verbs = ("won", "win", "accept", "receive", "award")

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
                item = can_combine_item_set(item, presenters)
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


def main_loop(year):
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

    for line in tweets:

        if tweet_counter % 1000 == 0:
            print(tweet_counter)

        if tweet_counter == len(tweets) - 1:
            # print("ending")
            nominees, winners, presenters = wrapup()
            end_time = time.time()
            # print(nominees, winners, presenters)
            # print("NOMINEES:", nominees)
            # print("WINNERS:", winners)
            # print("PRESENTERS:", presenters)
            print("RUNTIME:", end_time - start_time, "seconds. (", (end_time - start_time) / 60, "minutes.)")
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
                potential_item, noun_len = full_nnp(clean_parsed[counter: length])
                counter += noun_len

                # find the next verb for each NNP group
                next_verb, verb_ind = find_next_verb(clean_parsed[counter: length])
                if next_verb != "":
                    next_verb = next_verb.lower()
                    if not any(word in next_verb for word in ("present", "win", "announ", "won", "host", "accept")):
                        counter += 1
                        break
                    new_counter = counter + verb_ind + 1

                    # find the next group of nouns starting with 'best'
                    award = find_next_award_hardcoded(clean_parsed[new_counter: length])
                    if award:
                        # # check if it's a real actor's name
                        # this_actor = industry_name(potential_actor)
                        # #try:
                        #     #this_actor = actor_name(potential_actor)
                        # #except:
                        #     #break
                        # if this_actor != "Not A Relevant Person":
                        #     # print("updating master", award, this_actor, next_verb)
                        #     update_master(award, this_actor, next_verb)
                        # else:
                        #     this_actor = media_name(potential_actor)
                        #     if this_actor != "Not A Movie":
                        #         update_master(award, this_actor, next_verb)
                        update_master(award, potential_item, next_verb)
            else:
                counter += 1

        tweet_counter += 1


def wrapup():
    print("wrapping up", time.time()-start_time)
    # print("MASTER LIST IS", masterlist)
    cutoff_symbols =[",",".","!","?","http","www"]

    print("MASTERLIST IS", masterlist)

    nominees_dict = {}
    winners_dict = {}
    presenters_dict = {}

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
            if len(nominees) >= 4:
                sorted_noms = sorted(nominees.items(), key=lambda x: x[1], reverse=True)
                final_noms = list(pair[0] for pair in sorted_noms)[:4]
            else:
                final_noms = list(nominees.keys())
        if presenters.items():
            if len(nominees) >= 2:  # SHOULD THIS STAY LIKE THIS?
                sorted_pres = sorted(presenters.items(), key=lambda x: x[1], reverse=True)
                final_pres = list(pair[0] for pair in sorted_pres)[:4]
            else:
                final_pres = list(presenters.keys())

        pythonwhy.append((award, final_pres, final_noms, final_winner))

    for award, presenters, nominees, winner in pythonwhy:
        nominees_dict[award] = nominees
        winners_dict[award] = winner
        presenters_dict[award] = presenters
        # print("Award:", award, "Presented by:", presenters, "Nominated:", nominees, "winner:", winner)

    return nominees_dict, winners_dict, presenters_dict

# main_loop()


# list_actors()
# print(len(basic_names))
# print(industry_name(" Um"))
# print(industry_name(" Bill Murray"))
#
# list_movies()
# print(len(basic_titles))
# print(media_name("homeland"))
# print(media_name("brave"))
# print(media_name("the breakfast club"))
