#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

from datetime import datetime
from hashlib import sha1
from ldap3 import Server, Connection, ALL

from status.util.aruba import Aruba


__all__ = ['Wifi']


class Wifi:
    table = 'wifi_stations'
    columns = ['ts', 'dev', 'affi', 'ap', 'essid', 'phy']

    def __init__(self, wifi_host, wifi_user, wifi_pass,
                       ldap_host, ldap_bind, ldap_pass, ldap_base, ldap_attr,
                       ldap_filter):
        self.wifi_host = wifi_host
        self.wifi_user = wifi_user
        self.wifi_pass = wifi_pass
        self.ldap_host = ldap_host
        self.ldap_bind = ldap_bind
        self.ldap_pass = ldap_pass
        self.ldap_base = ldap_base
        self.ldap_attr = ldap_attr
        self.ldap_filter = ldap_filter

    def collect(self):
        aruba = Aruba(self.wifi_host, self.wifi_user, self.wifi_pass)
        aruba.login()

        ldap = Connection(self.ldap_host, self.ldap_bind, self.ldap_pass,
                          auto_bind=True)

        rows = []
        now = datetime.now()
        r = aruba.request_table('show station-table')

        for mac, name, role, age, auth, ap, essid, phy, remote, profile in r:
            if not name:
                continue

            dev = sha1(mac.encode('utf8')).hexdigest()[:16]
            affi = ''

            if '@' in name:
                affi = '@' + name.rsplit('@', 1)[1]

            else:
                filter = self.ldap_filter.format(name=name)
                ldap.search(self.ldap_base, filter,
                            attributes=[self.ldap_attr])

                if len(ldap.entries) > 0:
                    attr = getattr(ldap.entries[0], self.ldap_attr)

                    if attr is not None and len(attr) > 0:
                        affi = '/'.join(attr)

            rows.append([now, dev, affi, ap, essid, phy])

        return self.table, self.columns, rows


# vim:set sw=4 ts=4 et:
