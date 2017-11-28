# -*- coding: utf-8 -*-

"""tableaurest.cli

This module contains command line utilities for `tableaurest`.


See the README for further details.

"""

import getpass
import logging

import click

import tableaurest
from tableaurest.core import TableauSystemExit


@click.group()
@click.version_option(version=tableaurest.__version__)
def main():
    """
    tableaurest - A Python Based Tableau REST API Interface.

        USAGE:
        $ tableaurest --help

    See the README for further details.
    """
    pass


@main.command()
@click.option('--server', '-s', help='Base url of Tableau Server to connect to.')
@click.option('--username', '-u', help='Name of user to log into Tableau Server with.')
@click.option('--password', '-p', default=None, help='Password of user to log into Tableau Server with.')
@click.option('--site', '-t', default='', help='Content url of site to connect to Tableau Server with.')
@click.option('--api', '-a', default='2.5', help='API version number for Interfacing with Tableau Server.')
@click.option('--project', help='Name of project workbooks/datasource exists in.')
@click.option('--url', help='Name of workbook as it appears in URL.')
@click.option('--workbook', help='Name of workbook to refresh.')
@click.option('--datasource', help='Name of datasource containing extracts to refresh.')
@click.option('--synchronous', is_flag=True, help='Flag for awaiting completion of workbook refresh.')
def refreshextracts(server, username, password, **options):
    """Run Extract Refreshes on workbook/datasource.

    Performs a full refresh on 'scheduled' extract for a given workbook/datasource.

    This utility is similar to that provided by `tabcmd refreshextracts`, however
    it instead utilizes the official REST API. This also means a few sacrifices
    were needed, as the current (2.7) REST API does not provide complete duplicable
    functionality. The first major difference is that a workbook/datasource must be
    scheduled for refresh (even if that means it is disabled). The second is that
    login/logout will be handled by this method, and will not persist between commands.

    Notes
    -----
    If no '--password' is provided, a prompt will follow the command asking for one.
    If '--synchronous' is provided, method attempts to report back when refresh complete.
    Only one of the following is required {url, workbook, datasource}.

    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(module)s - %(levelname)s - %(funcName)s - %(message)s'
    )

    requires = ('url', 'workbook', 'datasource', )
    if set(options.keys()).isdisjoint(set(requires)):
        raise TableauSystemExit(f'At least one of {requires} must be given.')

    if password is None:
        password = getpass.getpass('Enter Password: ')

    with tableaurest.TableauREST(server, username, password, **options) as restapi:

        if set(options.keys()) & set(requires[:2]):
            args = ('contentUrl', 'url') if 'url' in options.keys() else ('name', 'workbook')

            workbooks = restapi.queryWorkbooksforUser()
            workbooks = {k: v for k, v in workbooks.items() if k[args[0]] == options[args[1]]}

        else:
            datasources = restapi.queryDatasources()
            workbooks = {k: v for k, v in datasources.items() if k['name'] == options['datasource']}

        if 'project' in options.keys():
            workbooks = {k: v for k, v in workbooks.items() if v['project']['name'] == options['project']}

        if len(workbooks.keys()) != 1:
            raise TableauSystemExit(f'Matched workbooks was not 1 (Found == {len(workbooks.keys())}')

        tasks = restapi.getExtractRefreshTasks()
        tasks = {k: v for k, v in tasks.items() if v['datasource']['id'] == workbooks.keys()[0]}

        if len(tasks.keys()) != 1:
            raise TableauSystemExit(f'Matched tasks was not 1 (Found == {len(tasks.keys())}')

        restapi.runExtractRefreshTaskSync(tasks.keys()[0], sync=options['synchronous'], frequency=15)


if __name__ == '__main__':
    main()
