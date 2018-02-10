#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

from csv import reader
from datetime import datetime
from hashlib import sha1
from ldap3 import Server, Connection, ALL
from os import walk
from os.path import join, basename

from status.util.aruba import Aruba


__all__ = ['WifiImport']


class WifiImport:
    table = 'wifi_stations'
    columns = ['ts', 'dev', 'affi', 'ap', 'essid', 'phy']

    def __init__(self, ldap_host, ldap_bind, ldap_pass, ldap_base, ldap_attr,
                       ldap_filter, import_path):
        self.ldap_host = ldap_host
        self.ldap_bind = ldap_bind
        self.ldap_pass = ldap_pass
        self.ldap_base = ldap_base
        self.ldap_attr = ldap_attr
        self.ldap_filter = ldap_filter
        self.import_path = import_path

    def collect(self):
        ldap = Connection(self.ldap_host, self.ldap_bind, self.ldap_pass,
                          auto_bind=True)

        cache = {}
        rows = []

        for path, _dirs, fnames in walk(self.import_path):
            for fname in fnames:
                if not fname.endswith('.csv'):
                    continue

                print(' - {!r}'.format(join(path, fname)))

                time = fname.split('.')[0].replace('-', ':')
                now = basename(path) + ' ' + time

                with open(join(path, fname)) as fp:
                    rd = reader(fp)
                    r = list(rd)[1:]

                for mac, name, role, age, auth, ap, essid, phy, remote, profile in r:
                    if not name:
                        continue

                    dev = sha1(mac.encode('utf8')).hexdigest()[:16]
                    affi = ''

                    if '@' in name:
                        affi = '@' + name.rsplit('@', 1)[1]

                    elif name in cache:
                        affi = cache[name]

                    else:
                        filter = self.ldap_filter.format(name=name)
                        ldap.search(self.ldap_base, filter,
                                    attributes=[self.ldap_attr])

                        if len(ldap.entries) > 0:
                            attr = getattr(ldap.entries[0], self.ldap_attr)

                            if attr is not None and len(attr) > 0:
                                affi = '/'.join(attr)

                        cache[name] = affi

                    rows.append([now, dev, affi, ap, essid, phy])

        return self.table, self.columns, rows


# vim:set sw=4 ts=4 et:
