###
# Copyright (c) 2011, Clint Savage
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import os
import time
import string
import datetime

import PyRSS2Gen

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Irc2rss(callbacks.Plugin):
    """Add the help for "@plugin help Irc2rss" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Irc2rss, self)
        self.__parent.__init__(irc)
        self.path = self.registryValue('basepath' )

    def _generateFeed(self):
        # generate the rss.xml

        self.rsstitle = self.registryValue('title') % {'user': self.nick}
        self.rsslink = self.registryValue('link') % {'user': self.nick}
        self.rssdesc = self.registryValue('description')
        self.pubdate = datetime.datetime.now()

        f = open("%s/%s/rss.in" % (self.path, self.nick), 'r')

        item_list = []
        for line in f:
            t, u, d, dt = line.split("|")
#            time.sleep(2)

#            irc.reply("t: %s, u: %s, dt: %s, d: %s" % (t, u, dt, d))
            item = PyRSS2Gen.RSSItem(title = t, link = u, description = d, guid = PyRSS2Gen.Guid(u + dt), pubDate = dt)
            item_list.append(item)

        f.close()
 
        rss = PyRSS2Gen.RSS2( title = self.rsstitle, link = self.rsslink, description = self.rssdesc, lastBuildDate = self.pubdate, items = item_list)        
        file("%s/%s/rss.xml" % (self.path, self.nick), 'w+').write(rss.to_xml())

    def genrss(self, irc, msg, args, text):

        self.nick = msg.nick
        self._generateFeed()
        irc.reply("rss feed for '%s' generated" % self.nick)

    genrss = wrap(genrss, [optional('something')])

    def add2rss(self, irc, msg, args, text):

        self.nick = msg.nick
        dateformat = self.registryValue('dateFormat')

        if not os.path.exists(u"%s/%s/rss.in" % (self.path, self.nick)):
            if not os.path.isdir(u"%s/%s" % (self.path, self.nick)):
                os.makedirs(u"%s/%s" % (self.path, self.nick), 0775)

        f = open("%s/%s/rss.in" % (self.path, self.nick), 'a')

        itemmessage = string.join(text)
        itemlink = self.registryValue('link') % {'user': self.nick}
        itemdesc = "%s's status on %s" % (self.nick, self.pubdate)

        f.write("%s|%s|%s|%s\n" % (itemmessage, itemlink, itemdesc, self.pubdate))

        irc.reply("status '%s' added" % itemmessage)

        f.close()

        self._generateFeed()

    add2rss = wrap(add2rss, [many('something')])

Class = Irc2rss


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
