'''Version 0.35'''
import nltk


OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
answer_file_name = 'our_answers'

# FIGURE OUT YEAR
# this_year = '2013'

import code
import json

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    hosts = []
    with open(answer_file_name + str(year) + '.json') as json_file:
        data = json.load(json_file)
        hosts = data["Host"]
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    # FIX THIS
    with open(answer_file_name + str(year) + '.json') as json_file:
        data = json.load(json_file)
        awards = data["Awards"]
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees = {}
    with open(answer_file_name + str(year) + '.json') as json_file:
        data = json.load(json_file)
        for item in data:
            if item in OFFICIAL_AWARDS_1315:
                nominees[item] = data[item]["Nominees"]
    # print(nominees)
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners = {}
    with open(answer_file_name + str(year) + '.json') as json_file:
        data = json.load(json_file)
        for item in data:
            if item in OFFICIAL_AWARDS_1315:
                winners[item] = data[item]["Winner"]
    # print(winners)
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    presenters = {}
    with open(answer_file_name + str(year) + '.json') as json_file:
        data = json.load(json_file)
        for item in data:
            if item in OFFICIAL_AWARDS_1315:
                presenters[item] = data[item]["Presenters"]
    # print(winners)
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    nltk.download('averaged_perceptron_tagger')
    print("Pre-ceremony processing complete.")
    return

def create_ans_file(nominees, winners, presenters, hosts, awards, year, official_awards):
    all_answers = {
        "Host": hosts,
        "Awards": awards
    }
    for award_name in official_awards:
        all_answers[award_name] = {
            "Presenters": [presenter for presenter in presenters.get(award_name)] if presenters.get(award_name) else [],
            "Nominees": [nominee for nominee in nominees.get(award_name)] if nominees.get(award_name) else [],
            "Winner": winners.get(award_name) if winners.get(award_name) else []
        }
    with open(answer_file_name + year + '.json', 'w') as f:
        json.dump(all_answers, f)

    with open('human_readable_' + year + '.txt', 'w') as f:
        f.write('Hosts: ' + ', '.join(hosts) + '\n\n')
        f.write('Our extracted awards: ' + ', '.join(awards) + '\n\n')
        for real_award in official_awards:
            f.write(real_award + ': ' + '\n')
            f.write('\t' + 'Presenters: ' + (', '.join([presenter for presenter in presenters.get(real_award)]) + '\n'
                    if presenters.get(real_award) else 'Not found' + '\n'))
            f.write('\t' + 'Nominees: ' + (', '.join([nominee for nominee in nominees.get(real_award)]) + '\n'
                    if nominees.get(real_award) else 'Not found' + '\n'))
            f.write('\t' + 'Winner: ' + (winners.get(real_award) + '\n\n' if winners.get(real_award)
                    else 'Not found' + '\n\n'))

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here

    # FIGURE OUT HOW TO DEAL WITH YEAR

    this_year = input("Please enter the year you'd like to run, or 'c' to run both 2013 and 2015:  ")

    if this_year == 'c':
        years = ['2013', '2015']
        for year in years:
            nominees, winners, presenters, hosts, awards = code.main_loop(year, OFFICIAL_AWARDS_1315)
            create_ans_file(nominees, winners, presenters, hosts, awards, year, OFFICIAL_AWARDS_1315)
    elif this_year == '2013' or this_year == '2015':
        nominees, winners, presenters, hosts, awards = code.main_loop(this_year, OFFICIAL_AWARDS_1315)
        create_ans_file(nominees, winners, presenters, hosts, awards, this_year, OFFICIAL_AWARDS_1315)
    else:
        nominees, winners, presenters, hosts, awards = code.main_loop(this_year, OFFICIAL_AWARDS_1819)
        create_ans_file(nominees, winners, presenters, hosts, awards, this_year, OFFICIAL_AWARDS_1819)


if __name__ == '__main__':
    main()
