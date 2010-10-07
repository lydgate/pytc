#!/usr/bin/env python
#
# WARNING
#
# This code doesn't yet work as it needs more generalized oauth
# support. Previously I hard-coded in my own consumer_key,
# consumer_secret, oauth_token, and oauth_token_secret.  Obviously,
# since this is becoming an open source application, that will
# no longer fly.
#
# TODO: Incorporate the below warning into a message when
# you run the app without a proper ~/.pytc
#
# WARNING ABOUT OAUTH
#
# The consumer key and consumer secret in this file are publicly
# available.  This is not a great idea, as any application can
# impersonate this one to twitter.  But it's included here for your
# convenience.  If you want to register your own, just go to
# http://dev.twitter.com and register an app, and replace the below
# with your own key and secret before running pytc.
#
# This file is part of pytc.
#
# pytc is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pytc is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pytc.  If not, see <http://www.gnu.org/licenses/>.
from oauthtwitter import OAuthApi
from time import strftime
from sys import argv
from urllib2 import HTTPError
import datetime
import os
import re

execfile(os.path.expanduser('~/.pytcrc'))

# Colours
def blue(msg):
    return '\033[1;34m%s\033[0m' % msg
def green(msg):
    return '\033[0;32m%s\033[0m' % msg
def red(msg):
    return '\033[0;31m%s\033[0m' % msg
def ul(msg):
    return '\033[4;37m%s\033[0m' % msg
def yellow(msg):
    return '\033[0;33m%s\033[0m' % msg
def white(msg):
    return '\033[1;37m%s\033[0m' % msg

# Some regexes:
url = re.compile('(https?://([-\w\.]+)+(:\d+)?(/([\w/_\-\.]*(\?\S+)?)?)?)')
user_regex = re.compile('(@?' + '|'.join(usernames) + ')')

def usage():
    print 'Usage:'
    print '  pytc <tweets>\t\tFetch public timeline'
    print '  pytc -f [users]\tFetch information about your friends'
    print '  pytc -t\t\tFetch your Timeline'
    print '  pytc -b\t\tFetch puBlic timeline'
    print '  pytc -t <user>\tFetch other users\' Timeline'
    print '  pytc -c <user>\tFetch other users\' Conversation'
    print '  pytc -s <terms>\tSearch twitter'
    print '  pytc -r\t\tFetch Replies'
    print '  pytc -u <status>\tUpdate your status'
    print '  pytc -h\t\tShow this Help message'

def remove_accents(str):
    import unicodedata
    nkfd_form = unicodedata.normalize('NFKD', unicode(str))
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    from datetime import timedelta
    from pytz import timezone
    now = datetime.now()
    utc = timezone('UTC')
    #now = now.replace(tzinfo=utc)
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif not time:
        diff = now - now
    else:
        diff = now - time - timedelta(hours=1) # TODO: Use TZ aware timezones!
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 14:
        return str(day_diff/7) + " week ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 60:
        return str(day_diff/30) + " month ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    if day_diff < 730:
        return str(day_diff/365) + " year ago"
    return str(day_diff/365) + " years ago"
def hilight(text):
    text = re.sub('(@.*?)(\W|$)',green('\\1')+'\\2',text)
    text = re.sub('(#.*?)(\W|$)',white('\\1')+'\\2',text)
    return text

def twdate_to_datetime(string):
    return datetime.datetime.strptime(string, '%a %b %d %H:%M:%S +0000 %Y')

def pretty_print(timeline):
    for tweet in timeline:
        user = blue(tweet['user']['screen_name'])
        time = pretty_date(twdate_to_datetime(tweet['created_at']))
        if 'retweeted_status' in tweet: # Check if this tweet is an RT
            # If so, print the user name in green and original twit in blue
            orig_user = green('@'+tweet['retweeted_status']['user']['screen_name'])
            text = hilight(tweet['retweeted_status']['text'])

            line = '%s: RT %s (via %s) (%s)' % (user, text, orig_user, time)
        else:
            # Otherwise, just print the name in blue and the tweet
            text = hilight(tweet['text'])

            line = '%s: %s (%s)' % (user, text, time)
        line = re.sub(user_regex, red('\\1'), line) # Highlight username.
        line = re.sub(url, yellow('\\1'), line)
        print remove_accents(line)

def get_userlines(options):
    user_detail_list = api.ApiCall('users/lookup','GET',options)
    userlines = ''
    for user_details in user_detail_list:
        followers = user_details['followers_count']
        followed  = user_details['friends_count']
        joined = pretty_date(twdate_to_datetime(user_details['created_at']))
        if followed == 0 or followers/followed > .5:
            friends = green('%s/%s' % (followed, followers))
        else:
            friends = red('%s/%s' % (followed, followers))
        tweets = user_details['statuses_count']
        if tweets < 50:
            tweets = red(tweets)
        userlines += '%s/%s (%s) %s - %s. (Created %s)\n' \
                % (blue(user_details['screen_name']),
                tweets,
                user_details['location'],
                friends,
                user_details['description'],
                joined)
    return userlines

def get_timeline(users=None,conv=False):
    if users:
        timeline = []
        options = {'screen_name':','.join(users)}
        userline = get_userlines(options)
        for user in users:
            if conv: # Get more replies if you're looking for conversation.
                options = {'screen_name':user,'count':100}
            else:
                options = {'screen_name':user}
            try:
                timeline += api.GetUserTimeline(options)
            except HTTPError:
                print 'Error fetching tweets from %s.' % user
        if len(users) > 1:
            timeline = sorted(timeline, key=lambda k: k['created_at'],reverse=True)
        if conv:
            # Create a regex which includes all participants' names
            user_match = re.compile('@(' + '|'.join(users) + ')',re.IGNORECASE)
            # List comprehension to filter all tweets for only ones containing names
            timeline = [t for t in timeline if user_match.search(t['text'])]
    else:
        options = {'screen_name':','.join(usernames)}
        userline = get_userlines(options)
        timeline = api.GetUserTimeline()
    print userline
    pretty_print(timeline)


api = OAuthApi(consumer_key, consumer_secret, oauth_token, oauth_token_secret)
if len(argv) > 1:
    if argv[1] == '-u': # Update status
        status = " ".join(argv[2:])
        if len(status) > 139:
            print 'Error: Status too long (%s characters)' % len(status)
        else:
            api.UpdateStatus(status)
    elif argv[1] == '-r': # Fetch replies
        timeline = api.ApiCall('statuses/mentions','GET')
        pretty_print(timeline)
    elif argv[1] in ('-t','-c'): # Fetch a timeline
        if len(argv) < 3:
            get_timeline()
        else:
            if argv[1] == '-c':
                get_timeline(argv[2:],conv=True)
            else:
                get_timeline(argv[2:])
    elif argv[1] == '-f': # Fetch friendlist
        if len(argv) > 2:
            options = {'screen_name':','.join(argv[2:])}
            print get_userlines(options)
        else:
            options = {'cursor':-1}
            followers = []
            userlines = ''
            while options['cursor'] != 0:
                ret = api.GetFollowers(options)
                chunk = [u['screen_name'] for u in ret['users']]
                options2 = {'screen_name':','.join(chunk)}
                userlines += get_userlines(options2)
                options['cursor'] = ret['next_cursor']
            print userlines
    elif argv[1] == '-s': # Search twitter!
        if len(argv) < 3:
            error('You need some manner of query.')
        else:
            q = ' '.join(argv[2:])
            options = {'q':q,'lang':'en'}
            search = api.ApiCall('search','GET',options)
            results = []
            for status in search['statuses']:
                try:
                    results.append(api.ApiCall('statuses/show/%s' % status,'GET'))
                except HTTPError:
                    continue
            pretty_print(results)
    elif argv[1] == '-b': # Public timeline
        timeline = api.GetPublicTimeline()
        pretty_print(timeline)
    elif argv[1] == '-h': # Help
        usage()
    else:
        try:
            options = {'count':int(argv[1])}
            timeline = api.GetHomeTimeline(options)
            pretty_print(timeline)
        except ValueError:
            usage()
else: # Otherwise just print timeline
    timeline = api.GetHomeTimeline()
    pretty_print(timeline)
