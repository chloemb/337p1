import nltk
import time
import read_json
from textblob import TextBlob

start_time = time.time()

# people awards are awards that are won by people (instead of media)
people_awards = []
real_awards = []

# keeping track of things that have been searched
searched_people = []
searched_media = []
not_person = []
not_movie = []

# keeping track for hosts and awards
mentions = {}
badawardnames = {}

# lists of names and titles from IMDB to search for
basic_names = []
basic_titles = []

fashion_list = {}

fashion_dict = ["dress", "gown", "strap", "tux", "suit", "skirt", "shoe", "lace",
                "sheer", "sequin", "designer", "bracelet", "wearing",
                "fashion"]

# master list of all presenters, winners, nominees
masterlist = []

# word bags
win_verbs = ["won", "win", "accept", "receive", "award", "got", "get", "honor"]
pres_verbs = ["present", "host", "announ", "give", "gave"]
all_verbs = win_verbs + pres_verbs

# if a tweet has any of these words, it will be parsed
pass_words = ["best", "cecil", "monologue", "ongrat"]


def list_actors():
    with open("new_name_updated.tsv", 'r', encoding='utf-8') as basics:
        for line in basics:
                basic_names.append(line.lower().split('\n')[0])


def list_movies():
    with open("new_title_updated.tsv", 'r', encoding='utf-8') as basics:
        for line in basics:
                basic_titles.append(line.lower().split('\n')[0])


def find_next_verb(pairs):
    counter = 0
    while counter < len(pairs):
        if pairs[counter][1].startswith('VB'):
            return pairs[counter][0], counter
        counter += 1
    return "", counter


def find_next_award_maria(pairs, best_index):
    counter = 0
    award = []
    while counter < len(pairs)-best_index:
        if pairs[counter+best_index-1][0] == 'best':
            award = ['best']
            removeything = 0
            while counter < len(pairs)-best_index and pairs[counter+best_index][1] in ['RBS', 'NN', 'VBG', 'JJS', 'IN']:
                if depunctuate(pairs[counter+best_index][0]) == '' or depunctuate(pairs[counter+best_index][0])==' ':
                    counter += 1
                    continue
                award.append(depunctuate(pairs[counter+best_index][0]))

                if pairs[counter+best_index][1] in ['IN','RBS','VBG','JJS']:
                    removeything += 1
                else:
                    removeything=0
                counter += 1
            award = award[:len(award)-removeything]
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
    name = ' '.join(name)
    return name, counter


def depunctuate(stringy):
    return stringy.partition(".")[0].partition(',')[0].partition("!")[0].partition("?")[0].partition("http")[0].replace(
        "'s", "")


def find_next_award(pairs, best_index):
    counter = 0
    award = []
    while counter < len(pairs)-best_index:
        if pairs[counter+best_index-1][0] == 'cecil':
            return ['cecil']
        if pairs[counter+best_index-1][0] == 'best':
            award = ['best']
            while counter < len(pairs)-best_index and pairs[counter+best_index][1].startswith(('N', 'VB', 'JJ')):
                award.append(depunctuate(pairs[counter+best_index][0]))
                counter += 1
            return award
        counter += 1
    return award


def find_next_award_hardcoded(pairs, best_index):
    # find closest official award name
    tweet = [pair[0] for pair in pairs]
    raw_award = find_next_award(pairs, best_index)
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
    name1 = name1.lower()
    name2 = name2.lower()
    if name1 == name2:
        return name1
    if name1 in name2:
        return name2
    if name2 in name1:
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
            if any(bigword in syn_list and smolword in syn_list for syn_list in prominent_synonyms):
                matched = True
                break
            if smolword == bigword:
                matched = True
                break
        if not matched:
            return False
    return big


def can_combine_item_set(item, answers):
    for set_item in answers:
        can_combine = combine_award(item, set_item)
        if can_combine:
            return can_combine
    return item


def update_master(award, item, verb, negated):

    if any(word in verb for word in pres_verbs) or award in people_awards:
        item = industry_name(item)
    else:
        item = media_name(item)
    if item == "not found":
        return

    for listaward, presenters, nominees, winners in masterlist:
        if award == listaward:
            if any(word in verb for word in pres_verbs):
                item = can_combine_item_set(item, presenters)
                presenters.setdefault(item, 0)
                presenters[item] += 1
                return

            nom_item = can_combine_item_set(item, nominees)
            nominees.setdefault(nom_item, 0)
            if negated:
                nominees[nom_item] += 2
            else:
                nominees[nom_item] += 1

            if any(word in verb for word in win_verbs) and not negated:
                item = can_combine_item_set(item, winners)
                winners.setdefault(item, 0)
                winners[item] += 1
            return

    newdict = dict({item: 1})
    if any(word in verb for word in pres_verbs):
        masterlist.append((award, newdict, dict(), dict()))
        return
    if any(word in verb for word in win_verbs):
        masterlist.append((award, dict(), newdict, newdict))
    else:
        masterlist.append((award, dict(), newdict, dict()))


def main_loop(year, these_awards):
    tweets = read_json.read_json(year)
    ignore_as_first_char = ('RT', '@', '#')
    # remove_as_first_char = ('@', '#')
    tweet_counter = 0

    list_actors()
    list_movies()

    for award in these_awards:
        if any(people_word in award for people_word in ("perform", "direct", "cecil")):
            people_awards.append(award)
        real_awards.append(award)

    for line in tweets:
        if tweet_counter % 10000 == 0:
            print(tweet_counter)

        if tweet_counter == len(tweets) - 1:
            nominees, winners, presenters, hosts, awards, fashion = wrapup()
            end_time = time.time()
            # print(nominees, winners, presenters)
            # print("NOMINEES:", nominees)
            # print("WINNERS:", winners)
            # print("PRESENTERS:", presenters)
            # print("MENTIONS:", mentions)
            # print("RUNTIME:", end_time - start_time, "seconds. (", (end_time - start_time) / 60, "minutes.)")
            return nominees, winners, presenters, hosts, awards, fashion

        lower_text = line['text'].lower()

        if not any(cont_word in lower_text for cont_word in (pass_words + fashion_dict)):
            tweet_counter += 1
            continue

        monologue = True if "monologue" in lower_text else False
        congrats_found = True if "ongrat" in lower_text else False

        fashion = True if any(cont_word in line['text'].lower() for cont_word in fashion_dict) else False

        cleaned = []
        for word in line['text'].split():
            if not word.startswith(ignore_as_first_char):
                # if word.startswith(remove_as_first_char) and len(word) > 1:
                #     word = word[1:]
                # print(word)
                cleaned.append(word)

        tagged = nltk.tag.pos_tag(cleaned)

        lower_tagged = [(item[0].lower(), item[1]) for item in tagged]
        # print(clean_parsed)


        # for i in lower_tagged:
        #     if "ongrat" in i[0]:
        #         congrats_found = True

        # print(lower_tagged)

        # now, match proper nouns to verbs
        length = len(lower_tagged)
        counter = 0
        while counter < length:
            # find every group of words labeled NNP

            if lower_tagged[counter][1] == 'NNP' and "ongrat" not in lower_tagged[counter][0]:
                potential_item, noun_len = full_nnp(lower_tagged[counter: length])
                counter += noun_len

                if monologue:
                    mon_item = can_combine_item_set(potential_item, mentions)
                    try:
                        mentions[mon_item] += 1
                    except:
                        mentions[mon_item] = 1
                    continue

                if fashion:
                    fashion_list.setdefault(potential_item, (0, 1, []))
                    fashion_list[potential_item][2].append(line['text'])
                    blank = fashion_list[potential_item][2]
                    fashion_list[potential_item] = (0,
                                                    fashion_list[potential_item][1] + 1,
                                                    blank)
                    continue

                # find the next verb for each NNP group
                next_verb, verb_ind = find_next_verb(lower_tagged[counter: length])
                if next_verb != "":
                    if not any(word in next_verb for word in all_verbs):
                        counter += 1
                        break
                    new_counter = counter + verb_ind + 1

                    if any(lower_tagged[new_counter - 2][0] == negate_word
                           for negate_word in ("didn't", "didnt", "not")):
                        negated = True
                    else:
                        negated = False

                    # find the next group of nouns starting with 'best'
                    badaward = find_next_award_maria(lower_tagged, new_counter)
                    newbadaward = ""

                    # add award
                    for word in badaward:
                        newbadaward = newbadaward+word+" "
                    try:
                        badawardnames[newbadaward] += 1
                    except:
                        badawardnames[newbadaward] = 1

                    # find the associated award name
                    award = find_next_award_hardcoded(lower_tagged, new_counter)
                    if award:
                        update_master(award, potential_item, next_verb, negated)
                        if congrats_found:
                            update_master(award, potential_item, next_verb, True)
            else:
                counter += 1

        tweet_counter += 1


def wrapup():
    # print("wrapping up", time.time() - start_time)

    newbadawards = dict()
    for award, counter in badawardnames.items():
        matched = False
        for otheraward, othercounter in newbadawards.items():
            if newbadawards.get(combine_award(award, otheraward)):
                matched = True
                othercounter += counter
                break
            else:
                if combine_award(award, otheraward) == award:
                    matched = True
                    newbadawards.pop(otheraward)
                    newbadawards[award] = counter + othercounter
                    break
        if not matched:
            newbadawards[award] = counter
    removelist = []
    for award, counter in newbadawards.items():
        if counter == 1:
            removelist.append(award)
    for award in removelist:
        newbadawards.pop(award)

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
    dlt = [key for key in fashion_list if fashion_list[key][1] < 60]
    total_sentiment = 0
    total_mentions = 0
    for key in dlt:
        del fashion_list[key]
    for potentials in fashion_list:
        for tweets in fashion_list[potentials][2]:
            blob = TextBlob(tweets)
            fashion_list[potentials] = (blob.sentences[0].sentiment.polarity+fashion_list[potentials][0],
                                        fashion_list[potentials][1], fashion_list[potentials][2])
        fashion_list[potentials] = (fashion_list[potentials][0]/fashion_list[potentials][1],
                                        fashion_list[potentials][1])
        total_sentiment += fashion_list[potentials][0]
        total_mentions += fashion_list[potentials][1]
    sorted_fashion = sorted(fashion_list.items(), key=lambda x: x[1][0], reverse=True)
    avg_sentiment = total_sentiment/total_mentions
    final_fashion = []
    counter_forward = 0
    counter_reverse = len(sorted_fashion) - 1
    while len(final_fashion) == 0:
        pot_icon = industry_name(sorted_fashion[counter_forward][0])
        if pot_icon != "not found":
            final_fashion.append(pot_icon)
        counter_forward += 1
    while len(final_fashion) == 1:
        pot_drab = industry_name(sorted_fashion[counter_reverse][0])
        if pot_drab != "not found":
            final_fashion.append(pot_drab)
        counter_reverse -= 1
    dlt_2 = [key for key in fashion_list if fashion_list[key][1] < 100]
    for key in dlt_2:
        del fashion_list[key]
    sorted_fashion_2 = sorted(fashion_list.items(), key=lambda x: abs(x[1][0] - avg_sentiment), reverse=False)
    counter_forward = 0
    while len(final_fashion) == 2:
        pot_con = industry_name(sorted_fashion_2[counter_forward][0])
        if pot_con != "not found":
            final_fashion.append(pot_con)
        counter_forward += 1


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
            if len(presenters) >= 2:
                sorted_pres = sorted(presenters.items(), key=lambda x: x[1], reverse=True)
                final_pres = list(pair[0] for pair in sorted_pres)[:2]
            else:
                final_pres = list(presenters.keys())

        pythonwhy.append((award, final_pres, final_noms, final_winner))

    for award, presenters, nominees, winner in pythonwhy:
        nominees_dict[award] = nominees
        winners_dict[award] = winner
        presenters_dict[award] = presenters

    final_awards = list(pair[0] for pair in newbadawards.items())

    return nominees_dict, winners_dict, presenters_dict, final_men, final_awards, final_fashion

