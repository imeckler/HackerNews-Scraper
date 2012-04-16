#! /usr/bin/env python
# script for scraping and parsing data from hackernews

from urllib import *
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from collections import defaultdict
import string

def strip_punctuation(s):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in s if ch not in exclude)

def str_to_num(s):
    return int(filter(lambda c: c.isdigit(), s))

# converts a string representing a time to an integer number of minutes
def age_from_string(s):
    if 'day' in s:
        return 60 * 60 * str_to_num(s)
    elif 'hour' in s:
        return 60 * str_to_num(s)
    elif 'minute' in s:
        return str_to_num(s)

# parses a page into a list of dictionaries where each dictionary
# contains the age, submission time, number of comments, user, score,
# and title of a post
def parse_page(urlstring):
    page = urlopen(urlstring).read()
    soup = BeautifulSoup(page)

    infoblocks = soup.findAll('td', 'subtext')
    titleprelim = soup.findAll('td', 'title')
    titleblocks = titleprelim[1::2]
    nextpage    = 'http://news.ycombinator.com' + titleprelim[-1].contents[0].attrs[0][1]

    posts = []
    for iblock, tblock in zip(infoblocks,titleblocks):
        icontents = iblock.contents
        tcontents = tblock.contents

        try: age = age_from_string(icontents[3])
        except IndexError: continue

        try: comments = str_to_num(icontents[4].contents[0])
        except ValueError: comments = 0

        try: site  = tcontents[1].contents[0][2:-2]
        except (IndexError, AttributeError): site = ""

        subtime = datetime.now() - timedelta(minutes=age)
        user    = icontents[2].contents[0]
        score   = str_to_num(icontents[0].contents[0])
        title   = tcontents[0].contents[0]
        posts.append({'age':age, 
                      'time':subtime,
                      'comments':comments,
                      'user':user,
                      'score':score,
                      'title':title,
                      'site':site})
    return posts, nextpage

# generator wrapper for the parsing function
def parse_gen(n):
    curr_url = 'http://news.ycombinator.com/news2'
    for i in xrange(0,n):
        (posts, nextpage) = parse_page(curr_url)
        yield posts
        curr_url = nextpage


# from a list of words, generate all possible runs of length n 
def tokenize_words(words, n):
    tokens = []
    for i in xrange(0, len(words) - n + 1):
        tokens.append(words[i:i + n])
    return tokens


# count the frequency of each score for each token
def token_popularities(posts, token_size):
    token_popularity = defaultdict(lambda: defaultdict(int))
    for post in posts:
        title = post['title']
        score = post['score']

        if token_size == 1:
            tokens = [w for ws in tokenize_words(strip_punctuation(title).split(), 1) for w in ws]
        else:
            tokens = map(tuple, tokenize_words(strip_punctuation(title).split(), 1))

        for token in tokens:
            token_popularity[token][score] += 1

    return token_popularity

    """
    result = {}
    for token, score_freq in token_pops.iteritems():
        if not (token in bad_words or token in [w.upper() for w in bad_words]):"""
def popular_tokens(token_pops):
    bad_words = ['a', 'the', 'than', 'and', 'or', 'will', 'what', 'how', 'its']
    return {token: scores for token, scores in token_pops.iteritems()
                          if token not in bad_words and
                             token not in [w.upper() for w in bad_words] and
                             (max(scores) > 100 or len(scores) > 4)}

def sorted_by_max_score(token_pops):
    token_pops = {token: max(scores) for (token, scores) in token_pops.iteritems()} 
    return sorted(token_pops.iteritems(), key=lambda (t, s): s)


if __name__ == "__main__":
    print "Please enter the number of pages you would like parsed."
    n = int(raw_input())
    print list(parse_gen(n))