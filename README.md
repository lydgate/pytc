    pytc 0.3.3 - a command line python twitter client
    Copyright (C) 2010-2011  Bryan Kam
    Email: pytc@vo.racio.us

  GPL v3
==========

This file is part of pytc.

pytc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pytc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pytc.  If not, see <http://www.gnu.org/licenses/>.


  Requirements
================

 - python2
 - [tweepy](http://github.com/joshthecoder/tweepy)


If you use Arch Linux, tweepy-git is in the AUR.

  Installation
================

From 0.2.3 pytc uses distutils, so on most platforms you can simply run:
  python setup.py install

  Arch Linux
===============

A PKGBUILD for Arch Linux has been included.  However, since the release 
tarballs come from Gitorious, I don't have an easy way of md5summing it until 
the release has been pushed.  My solution is to omit the md5sums key, if you 
want to run it then you can just run "makepkg -g" and paste in the md5sums 
before running "makepkg".

  Usage
=========

Usage is simple. Please see pytc -h.

Some examples:

Check your Twitter timeline;

    pytc

Show last 75 items on your Twitter timeline:

    pytc 75

Update your Twitter status:

    pytc -u "Testing out pytc. It works!"

Read fictionaluser's status:

    pytc -t fictionaluser

Search for a term:

    pytc -s searchterm

  Known Issues
================

 - There's a dirty hack in the timezone code which subtracts an
   hour. Not sure why this is necessary, must be GMT vs BST.

 - The "conversation" (-c) feature only half-works. It doesn't
   properly sort times for reasons I don't quite understand, and
   doesn't really work if one user is tweeting much more frequently
   than the other, because the responses to the tweets may be lost.

 - Public timeline doesn't seem to work with tweepy.

  Todo List
=============

Saved separately in todo.otl in this repo. It will look prettier 
with [The Vim Outliner](http://bike-nomad.com/vim/vimoutliner.html)
