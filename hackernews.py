#! /usr/bin/env python
# script for scraping and parsing data from hackernews

from urllib import *
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta

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
        except (IndexError, AttributeError): site  = ""
        
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

# example usage follows
print "Please enter the number of pages you would like parsed."
n = int(raw_input())
print list(parse_gen(n))