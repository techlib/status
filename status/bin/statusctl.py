#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-

import io
import sys

import click

from collections import OrderedDict
from configparser import ConfigParser
from csv import writer, DictWriter
from importlib import import_module
from psycopg2 import connect, sql
from tabulate import tabulate
from traceback import print_exc


__all__ = ['cli']


class Model:
    def __init__(self, config):
        # Parse in the configuration file.
        ini = ConfigParser()
        ini.read_file(config)

        # This does not actually connect to the database right away...
        # Only when we actually need it, i.e. for `save`.
        self.db = connect(ini.get('general', 'db'))

        # Collection of module drivers.
        self.drivers = {}

        for section in ini.sections():
            if section == 'general':
                continue

            kwargs = dict(ini.items(section))
            module, klass = kwargs.pop('driver').split(':', 1)
            Driver = getattr(import_module(module), klass)
            self.drivers[section] = Driver(**kwargs)


pass_model = click.make_pass_decorator(Model)

@click.group()
@click.option('--config', '-c', default='/etc/ntk/status.ini',
              metavar='PATH', help='Load a configuration file.',
              type=click.File('r'))
@click.version_option('0.1.0')
@click.pass_context
def cli(ctx, config):
    """
    Status command-line utility.

    Can be used to gather the statistical data using customized plugins and
    store them in a PostgreSQL database.
    """

    # Prepare the domain model.
    model = Model(config)

    # Pass the our model onto the sub-commands.
    ctx.obj = model


@cli.command('list')
@pass_model
def cli_list(model):
    """
    List known drivers.
    """

    for module in model.drivers:
        print(module)


@cli.command('test')
@click.option('--csv', '-C', is_flag=True, help='Format output as CSV.')
@click.argument('module', type=str)
@pass_model
def cli_test(model, module, csv=False):
    """
    Test a single data collection driver.
    """

    driver = model.drivers[module]
    _table, columns, rows = driver.collect()
    print_table(columns, rows, csv=csv)


@cli.command('save')
@click.argument('modules', type=str, nargs=-1)
@pass_model
def cli_save(model, modules):
    """
    Gather data and save them to the database.
    """

    if not modules:
        modules = list(model.drivers)

    for module in modules:
        if not module in model.drivers:
            print('No such module: {!r}'.format(module), file=sys.stderr)
            exit(1)

    status = 0

    for module in modules:
        driver = model.drivers[module]

        try:
            print('Save {!r}'.format(module))
            table, columns, rows = driver.collect()

            fp = io.StringIO()
            wr = writer(fp, dialect='unix')

            for row in rows:
                wr.writerow(row)

            fp.seek(0)

            cq = ', '.join(['{}' for c in columns])
            q = 'copy {} (%s) from stdin with csv' % (cq,)

            cols = [sql.Identifier(c) for c in columns]
            copy = sql.SQL(q).format(sql.Identifier(table), *cols)

            model.db.cursor().copy_expert(copy, fp)
            model.db.commit()

        except:
            print_exc()
            status = 1

    print('Done.')
    exit(status)


def print_table(headers, rows, csv=False):
    if csv:
        w = writer(sys.stdout, dialect='unix')
        w.writerow([h.lower() for h in headers])

        for row in rows:
            w.writerow(row)

    else:
        print(tabulate(rows, headers))


if __name__ == '__main__':
    cli()


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
