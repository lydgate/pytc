#!/usr/bin/env python2
# TODO: Incorporate the below warning into a message when
# you run the app without a proper ~/.pytc
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
from urllib2 import HTTPError
import os
import re
import sys
import tweepy

VERSION='0.3.4'
YEARS='2010-2015'

conffile = os.path.expanduser('~/.pytcrc')

# Colours
def blue(msg):
    return '\033[1;34m%s\033[0m' % msg
def gray(msg):
    return '\033[1;30m%s\033[0m' % msg
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

def version():
    print('pytc %s Copyright (C) %s Bryan Kam' % (VERSION,YEARS))

def usage():
    version()
    print('''This program comes with ABSOLUTELY NO WARRANTY; for details see COPYING.txt.
This is free software, and you are welcome to redistribute it under certain 
conditions; see COPYING.txt for details.''')
    print
    print('Usage:')
    print('  pytc <tweets>\t\tFetch home timeline')
    print('  pytc -f [users]\tFetch information about your friends')
    print('  pytc -t\t\tFetch your Timeline')
    print('  pytc -t <user>\tFetch other users\' Timeline')
    print('  pytc -c <user>\tFetch other users\' Conversation')
    print('  pytc -s <terms>\tSearch twitter')
    print('  pytc -r\t\tFetch Replies')
    print('  pytc -u <status>\tUpdate your status (optionally shorting URLs with bit.ly)')
    print('  pytc -h\t\tShow this Help message')
    print('  pytc -hb\t\tShow help on setting up bit.ly')
    print('  pytc -v\t\tShow Version of this software')

def get_input(prompt,vartype,default=''):
    import sys
    while True:
        var = raw_input(prompt)
        if var == 'q':
            sys.exit(0)
        if var == '' and default != '':
            return default
        try:
            vartype(var)
        except:
            print('%s is not valid. Expected a %s.' % (var,vartype))
            continue
        return vartype(var)

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
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif not time:
        diff = now - now
    else:
        diff = now - time # TODO: Use TZ aware timezones!
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return 'just now'

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

def pretty_print(timeline):
    for tweet in timeline:
        user = blue(tweet.user.screen_name)
        time = gray(pretty_date(tweet.created_at))
        if hasattr(tweet, 'retweeted_status'): # Check if this tweet is an RT
            # If so, print the user name in green and original twit in blue
            orig_user = green('@'+tweet.retweeted_status.user.screen_name)
            text = hilight(tweet.retweeted_status.text)

            line = '%s[%s]: %s (%s)' % (user, orig_user, text, time)
        else:
            # Otherwise, just print the name in blue and the tweet
            text = hilight(tweet.text)

            line = '%s: %s %s' % (user, text, time)
        line = re.sub(user_regex, red('\\1'), line) # Highlight username.
        line = re.sub(url, yellow('\\1'), line)
        print(remove_accents(line))

def get_userlines(usernames):
    user_detail_list = api.lookup_users(screen_names=usernames)
    userlines = ''
    for user_details in user_detail_list:
        followers = user_details.followers_count
        followed  = user_details.friends_count
        joined = pretty_date(user_details.created_at)
        if followed == 0 or followers/followed > .5:
            friends = green('%s/%s' % (followed, followers))
        else:
            friends = red('%s/%s' % (followed, followers))
        tweets = user_details.statuses_count
        if tweets < 50:
            tweets = red(tweets)
        userlines += '%s/%s (%s) %s - %s. (Created %s)\n' \
                % (blue(user_details.screen_name),
                tweets,
                user_details.location,
                friends,
                user_details.description,
                joined)
    return userlines

def get_timeline(users=None,conv=False):
    if users:
        timeline = []
        userline = get_userlines(users)
        for user in users:
            if conv: # Get more replies if you're looking for conversation.
                count = 100 
            else:
                count = 20
            try:
                timeline += api.user_timeline(user,count=count)
            except tweepy.error.TweepError:
                print('Error fetching tweets from %s.' % user)
        if len(users) > 1:
            timeline = sorted(timeline, key=lambda k: k.created_at,reverse=True)
        if conv:
            # Create a regex which includes all participants' names
            user_match = re.compile('@(' + '|'.join(users) + ')',re.IGNORECASE)
            # List comprehension to filter all tweets for only ones containing names
            timeline = [t for t in timeline if user_match.search(t.text)]
    elif usernames:
        userline = get_userlines(usernames)
        timeline = api.user_timeline()
    else:
        print('pytc -t will not work without defining your username.')
        print('Please specify your username(s) in %s in the form:' % conffile)
        print('usernames = ["user1","user2"]')
        sys.exit(1)
    print(userline)
    pretty_print(timeline)

def create_config():
    print("Could not open %s." % conffile)
    if get_input("Would you like me to create it? [y/N] ",str) == 'y':
        print('''
WARNING ABOUT OAUTH

pytc will write you a sample %s file. This will contain a
consumer_key and consumer_secret.  Since this is an open source
app, these are publicly available.  This is not a great idea, as
it means that any application can impersonate this one to Twitter.

It's included here for your convenience.  If you want to register
your own, just go to http://dev.twitter.com and register an app,
and replace the values with your own key and secret before running
pytc again.\n''' % conffile)
        if get_input("Continue? [y/N] ",str) == 'y':
            f = open(conffile,'w')
            f.write('''consumer_key = "XMmmwf1XQvtjjyZE2Cpg"
consumer_secret = "0zZ71NQjeLMMk9lRI3k8uaFBdKoPywZNpZY20QXU"\n''')
            return
    sys.exit(0) # If user doesn't confirm above twice, 

def oauth_authorize():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # User pastes this into their browser to bring back a pin number:
    print('You must authorize pytc to interact with your Twitter account.')
    print('Please paste the following URL into your browser to obtain a PIN.')
    print(auth.get_authorization_url())
    # Get the pin # from the user and get our permanent credentials:
    oauth_verifier = raw_input('What is the PIN? ')
    try:
        auth.get_access_token(oauth_verifier)
    except tweepy.TweepError:
        print('Error! failed to get access token.')
        sys.exit(1)
    oauth_token = auth.access_token.key
    oauth_token_secret = auth.access_token.secret
    f = open(conffile,'a')
    f.write('''oauth_token = "%s"
oauth_token_secret = "%s"\n''' % (oauth_token, oauth_token_secret))
    # Set up api a test API call using our new credentials
    return oauth_token, oauth_token_secret

try:
    exec(compile(open(conffile).read(), conffile, 'exec'))
except IOError:
    create_config()
    exec(compile(open(conffile).read(), conffile, 'exec'))

try:
    consumer_key, consumer_secret # Check that these are set correctly
except NameError:
    create_config()
    exec(compile(open(conffile).read(), conffile, 'exec'))

argv = sys.argv
if len(argv) > 1:
    if argv[1] == '-h': # Help
        usage()
        sys.exit(0)
    elif argv[1] == '-hb': # Show bitly help
        try:
            import bitly
        except ImportError:
            print('You need to install the python-bitly module:')
            print('https://code.google.com/p/python-bitly/')
            sys.exit(1)
        try:
            btapi = bitly.Api(login=bitly_login,apikey=bitly_apikey)
        except:
            print('You need to specify your bit.ly login and API key in ~/.pytcrc, e.g.:')
            print('bitly_login="yourname"')
            print('bitly_apikey="yourkey"')
            sys.exit(1)
        print('bit.ly appears to be configured correctly!')
        sys.exit(0)
    elif argv[1] == '-v': # Help
        version()
        sys.exit(0)

# Anything else will require authentication.
try:
    oauth_token, oauth_token_secret
except NameError:
    oauth_token, oauth_token_secret = oauth_authorize()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(oauth_token, oauth_token_secret)
api = tweepy.API(auth)
# Some regexes:
url = re.compile('(https?://([-\w\.]+)+(:\d+)?(/([\w/_\-\.]*(\?\S+)?)?)?)')
try:
    user_regex = re.compile('(@?' + '|'.join(usernames) + ')')
except NameError:
    print('No usernames key in %s. Your username won\'t be highlighted.' % conffile)
    usernames = None
    user_regex = re.compile('a^') # This never matches anything

if len(argv) > 1:
    if argv[1] == '-u': # Update status
        status = " ".join(argv[2:])
        try:
            import bitly
            try:
                btapi = bitly.Api(login=bitly_login,apikey=bitly_apikey)
                m = re.findall(url, status)
                for match in m:
                    long_url = match[0]
                    short_url = btapi.shorten(long_url)
                    status = re.sub(re.escape(long_url), short_url, status)
            except:
                pass
        except ImportError:
            pass
        print(status)
        if len(status) > 140:
            print('Error: Status too long (%s characters)' % len(status))
        else:
            api.update_status(status)
    elif argv[1] == '-r': # Fetch replies
        timeline = api.mentions_timeline()
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
            print(get_userlines(argv[2:]))
        else:
            followers = []
            for follower in list(tweepy.Cursor(api.followers).items()):
                followers.append(follower.screen_name)
                if len(followers) > 99:
                    print(get_userlines(followers))
                    followers = []
            print(get_userlines(followers))
    elif argv[1] == '-s': # Search twitter!
        if len(argv) < 3:
            print 'You need some manner of query.'
            sys.exit(1)
        else:
            q = ' '.join(argv[2:])
            search = api.search(q)
            results = []
            for status in [i.id for i in search]:
                try:
                    results.append(api.get_status(status))
                except HTTPError:
                    continue
            pretty_print(results)
    else:
        try:
            timeline = api.home_timeline(count=int(argv[1]))
            pretty_print(timeline)
        except ValueError:
            usage()
else: # Otherwise just print timeline
    timeline = api.home_timeline()
    pretty_print(timeline)
