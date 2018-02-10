#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

import re

from threading import Lock
from requests import Session, HTTPError
from time import time
from xml.etree.ElementTree import XML, ParseError

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)


class ArubaError(Exception):
    """Generic error related to communication with Aruba WiFi controllers."""


class Aruba(object):
    # <url> ? command @@ timestamp & UIDARUBA=session-id
    COMMAND_URL = 'https://{host}:4343/screens/cmnutil/execCommandReturnResult.xml'

    # POST opcode, url, needxml, uid, passwd
    LOGIN_URL = 'https://{host}:4343/screens/wms/wms.login'

    def __init__(self, host, username, password):
        """Store address and credentials for later."""

        self.host = host
        self.username = username
        self.password = password

        self.session = Session()

        self.login_url = self.LOGIN_URL.format(host=host)
        self.command_url = self.COMMAND_URL.format(host=host)

    def request(self, command):
        s = self.session.cookies.get('SESSION', '')
        p = '{0}@@{1}&UIDARUBA={2}'.format(command, int(time()), s)
        r = self.session.get(self.command_url, verify=False, params=p)

        # The controller shamelessly retains ASCII control characters and
        # some users are able to inject them through their login names.
        data = re.sub(b'[\x00-\x09\x11-\x12\x14-\x1f]',
                      lambda m: ('\\x%.2x' % m.group(0)[0]).encode('utf8'),
                      r.text.encode('utf8', 'xmlcharrefreplace'))

        if data:
            try:
                return XML(data)
            except ParseError:
                raise ArubaError('Response is not a valid XML element')

    def request_table(self, command):
        r = self.request(command)

        if r.find('t') is None:
            raise ArubaError('Response does not contain a table')

        return [[(c.text.strip() if c.text is not None else '') for c in row] \
                for row in r.find('t')[1:]]

    def request_dict(self, command):
        return {row[0]: row[1] for row in self.request_table(command)}

    def login(self):
        if self.request('show roleinfo').find('data'):
            return

        r = self.session.post(self.login_url, verify=False, data={
            'opcode': 'login',
            'url': '/',
            'needxml': '0',
            'uid': self.username,
            'passwd': self.password,
        })

        if 'Authentication complete' not in r.text:
            raise ArubaError('Login failed')


# vim:set sw=4 ts=4 et:
