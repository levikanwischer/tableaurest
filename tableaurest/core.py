# -*- coding: utf-8 -*-

"""Tableau REST API Interface and misc utilities.

NOTE(LEVI~20171122): This module requires users to be on Python 3.6+ and
Tableau Server API 2.5+. This is due to the usage of f-strings & 'ordered'
dictionaries in Python, as well as the use of JSON for the REST API. Outside
of those items, there really isn't any reason this package couldn't be made
backwards compatible with other versions of Python or the REST API. However,
at this time there are no plans to expand the version(s) compatibility.


See the README for further details.

"""

import functools
import logging
import sys
import time
from distutils.version import StrictVersion
from types import SimpleNamespace

import requests


# Suppress excessive logging messages from `requests`
logging.getLogger('requests').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


# TODO(LEVI~20171127): Consider changing this to a base 'Exception'
class TableauSystemExit(SystemExit):
    """Cleanly exit Tableau REST API process on error."""

    def __init__(self, msg):
        logging.critical(msg)
        super().__init__(f'{type(self).__name__}: {msg}')


def min_api_version(version):
    """Minimum API Method Version Exception decorator.

    Notes
    -----
    Usage of this method is currently set to '2.5' as a minimum for
    most all endpoints. This is due to the usage of JSON which was
    first introduced then. Methods with a version higher than '2.5'
    either include breaking changes, or were implemented after after.

    The idea for this decorator came from the TableauServerClient[0]
    code base. It is/was a completely reimplemented here, but is/was
    heavily influenced by the idea (which was a good idea - thanks).

    Links
    -----
    [0] https://github.com/tableau/server-client-python

    """
    def decorator(func):
        """Generic decorator function."""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            """Generic wrapper function."""
            minversion = StrictVersion(version)
            requestversion = StrictVersion(self.api)

            if minversion > requestversion:
                objectname = f'{type(self).__name__}.{func.__name__}'
                raise TableauSystemExit(f'Error API Version too low -> {objectname} >= {minversion}')

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


class Response(object):
    """Custom Tableau REST API JSON Response handler.

    This response object is meant for use with Official Tableau REST API
    requests designated for JSON only. This means the usability (both in
    version and preference) will be limited. Having the output in JSON
    significantly reduces the complexity of usability for returned values.

    Parameters
    ----------
    request : requests.Response
        Response object from REST API request.
    method : str, optional (default=None)
        Method name used for REST API request.

    Attributes
    ----------
    request : requests.Response
        Response object from REST API request.
    method : str
        Method name used for REST API request.
    body : dict
        Request response body as dict.
    keys : list
        List of top level keys in `body`.
    statuscode : int
        Numeric http(s) response code from request.
    ok : bool
        Flag for if `statuscode` within accepted list.
    pagination : types.SimpleNamespace
        SimpleNamespace of key/value pagination pairs.

    Methods
    -------
    validate_response_json()
        Validate request response is of 'Content-Type' JSON.
    validate_response_good()
        Validate request response is correct/expected.

    Raises
    ------
    TableauSystemExit
        If `request` header missing 'Content-Type' or is not JSON.
        If `request` response code not as expected.

    """
    _ACCEPTED_GOOD_CODES = (200, 201, 204, )

    def __init__(self, request, method=None):
        self.request = request
        self.method = method

        self.validate_response_json()

        self.body = self.request.json() if self.request.text else dict()
        self.keys = list(self.body.keys())

        self.statuscode = self.request.status_code
        self.ok = self.statuscode in self._ACCEPTED_GOOD_CODES

        self.validate_response_good()

    def validate_response_json(self):
        """Validate request response is of 'Content-Type' JSON."""
        if not self.request.text:
            logging.debug(f'Body of request was empty. (method={self.method})')

        elif 'Content-Type' not in self.request.headers:
            raise TableauSystemExit(f'Content-Type not found in request.headers {self.request.headers}')

        elif not self.request.headers['Content-Type'].lower().startswith('application/json'):
            raise TableauSystemExit(f'Content-Type is not set to JSON/UTF8 {self.request.headers}')

        return None

    def validate_response_good(self):
        """Validate request response is correct/expected."""
        result = 'Succeeded' if self.ok else 'Failed'
        logging.debug(f'Tableau REST API: {self.method} {result} (statuscode={self.statuscode})')

        error = {'error': '???', 'summary': 'Unknown error occurred.'}
        if 'error' in self.keys:
            error.update(self.body['error'])

        if not self.ok:
            raise TableauSystemExit(f'Error occurred on {self.method} ({error["code"]}: {error["summary"]})')

        return None

    @property
    def pagination(self):
        """Convert pagination results to SimpleNamespace."""
        paginate = {'pageNumber': 1, 'pageSize': 1, 'totalAvailable': 1}

        if 'pagination' in self.keys:
            pagination = self.body['pagination']
            for item, value in pagination.items():
                paginate[item] = int(value)

        return SimpleNamespace(**paginate)


class BaseTableauREST(object):
    """Base Tableau REST API Interface.

    This object implements only 'Official' REST API methods, but is in
    no was associated with, or approved by, Tableau the company. The usage
    of the word 'Official' is merely meant to convey a mapping of official
    methods, rather than 'helper' methods or 'unofficial' endpoints.

    Parameters
    ----------
    server : str
        Base url of Tableau Server to connect to.
    username : str
        Name of user to log into Tableau Server with.
    password : str
        Password of user to log into Tableau Server with.
    api : str, optional (default=self._CURRENT_API_VERION)
        API version number for Interfacing with Tableau Server.
    site : str, optional (default='')
        Content url of site to connect to Tableau Server with.

    Attributes
    ----------
    api : float
        Value of REST API version.
    site : str
        Content url of site signed into.
    server : str
        Base url of Tableau Server to connect to.
    baseapi : str
        Base url of Tableau Server plus API version.
    session : requests.Session
        Current session object for tableau interacting.

    Methods
    -------
    signIn(username, password, contenturl)
        Sign Into Tableau Server.
    signOut()
        Sign Out of Tableau Server.
    switchSite(contenturl)
        Switch Session Site on Tableau Server.
    # TODO(LEVI~20171122): Complete me...

    """
    _MIN_JSON_API_VERSION = '2.5'

    def __init__(self, server, username, password, **kwargs):
        self.api = kwargs['api'] if 'api' in kwargs else self._MIN_JSON_API_VERSION
        self.site = kwargs['site'] if 'site' in kwargs else ''

        self.userid = None
        self.siteid = None

        self.baseapi = f'{server}/api/{self.api}'

        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.session.headers.update({'Accept': 'application/json'})
        self.session.verify = False

        self.signIn(username, password, self.site)

    def __enter__(self):
        """Context manager entrance method."""
        return self

    def __exit__(self, type_, value_, traceback_):
        """Context manager exit method."""
        self.signOut()
        self.session.close()

        return None

    ########## Area: Authentication ##########
    # Additional Endpoints: None

    @min_api_version('2.5')
    def signIn(self, username, password, contenturl=''):
        """Sign Into Tableau Server.

        Parameters
        ----------
        username : str
            Name of user to log into Tableau Server with.
        password : str
            password of user to log into Tableau Server with.
        contenturl : str, optional (default='')
            Content url of site to connect to Tableau Server with.
            Default site is typically an empty string ('').

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Signing into `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/auth/signin'

        body = {'credentials': {'name': username, 'password': password}}
        body['credentials']['site'] = {'contentUrl': contenturl}

        request = self.session.post(url, json=body)
        response = Response(request, func)

        credentials = response.body['credentials']
        self.session.headers.update({'x-tableau-auth': credentials['token']})

        self.userid = credentials['user']['id']
        self.siteid = credentials['site']['id']

        return None

    @min_api_version('2.5')
    def signOut(self):
        """Sign Out of Tableau Server."""
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Signing out of `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/auth/signout'

        request = self.session.post(url)
        response = Response(request, func)

        return None

    @min_api_version('2.6')
    def switchSite(self, contenturl=''):
        """Switch Session Site on Tableau Server.

        Parameters
        ----------
        contenturl : str, optional (default='')
            Content url of site to connect to Tableau Server with.
            Default site is typically an empty string ('').

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Switching sites on `Tableau REST API` (site={contenturl})')

        url = f'{self.baseapi}/auth/switchSite'

        body = {'site': {'contentUrl': contenturl}}

        request = self.session.post(url, json=body)
        response = Response(request, func)

        credentials = response.body['credentials']
        self.session.headers.update({'x-tableau-auth': credentials['token']})

        self.userid = credentials['site']['id']
        self.siteid = credentials['user']['id']

        return None

    ########## Area: Sites ##########
    # Additional Endpoints: createSite, querySite, queryViewsforSite,
    # updateSite, deleteSite

    @min_api_version('2.5')
    def querySites(self, pagesize=1000):
        """Query Sites List on Tableau Server.

        Parameters
        ----------
        pagesize : int, optional (default=1000)
            Number of items to fetch per request.

        Returns
        -------
        sites : dict
            Dict of sites available to current user.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info('Querying sites on `Tableau REST API`')

        url = f'{self.baseapi}/sites'

        sites = dict()

        done, totalsize, pagenumber = False, 0, 1
        while not done:
            paged = f'{url}?pageSize={pagesize}&pageNumber={pagenumber}'

            request = self.session.get(paged)
            response = Response(request, func)

            pagenumber += 1  # NOTE(LEVI~20171122): Should this update from response?
            totalsize += response.pagination.pageSize
            done = response.pagination.totalAvailable <= totalsize

            for site in response.body['sites']['site']:
                siteid = site['id']
                sites[siteid] = site

        logging.debug('Found {len(sites)} sites on `Tableau REST API`')

        return sites

    ########## Area: Projects ##########
    # Additional Endpoints: createProject, updateProject, deleteProject

    @min_api_version('2.5')
    def queryProjects(self, pagesize=1000):
        """Query Site Projects List on Tableau Server.

        Parameters
        ----------
        pagesize : int, optional (default=1000)
            Number of items to fetch per request.

        Returns
        -------
        projects : dict
            Dict of projects available to current user.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying projects on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/projects'

        projects = dict()

        done, totalsize, pagenumber = False, 0, 1
        while not done:
            paged = f'{url}?pageSize={pagesize}&pageNumber={pagenumber}'

            request = self.session.get(paged)
            response = Response(request, func)

            pagenumber += 1
            totalsize += response.pagination.pageSize
            done = response.pagination.totalAvailable <= totalsize

            for project in response.body['projects']['project']:
                projectid = project['id']
                projects[projectid] = project

        logging.debug(f'Found {len(projects)} projects on `Tableau REST API` (site={self.site})')

        return projects

    ########## Area: Workbooks and Views ##########
    # Additional Endpoints: addTagstoView, queryViewsforSite, queryViewImage,
    # queryViewPreviewImage, getWorkbookRevisions, queryWorkbookPreviewImage,
    # queryWorkbooksforSite, downloadWorkbookRevision, removeWorkbookRevision,
    # deleteTagfromView, deleteTagfromWorkbook

    @min_api_version('2.5')
    def publishWorkbook(self, overwrite=False):
        raise NotImplementedError

    @min_api_version('2.5')
    def addTagstoWorkbook(self, workbookid, tags):
        """Add Tags to Workbook on Tableau Server.

        Parameters
        ----------
        workbookid : str
            ID of workbook to query information about.
        tags : list
            List of tags to add to workbook.

        Returns
        -------
        tags : list
            List of dict tags from Tableau Server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Adding tags to workbook on `Tableau REST API` (workbookid={workbookid})')

        url = f'{self.baseapi}/sites/{self.siteid}/workbooks/{workbookid}/tags'

        body = {'tags': [{'tag': {'label': tag}} for tag in tags]}

        request = self.session.put(url, json=body)
        response = Response(request, func)

        tags = response.body['tags']

        return tags

    @min_api_version('2.5')
    def queryViewsforWorkbook(self, workbookid, usagestats=True):
        """Query Workbook Views on Tableau Server.

        Parameters
        ----------
        workbookid : str
            ID of workbook to query information about.
        useagestats : bool, optional (default=True)
            Flag for including usage statistics for views.

        Returns
        -------
        views : dict
            Dict of view available to current user for workbook.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying views for workbook on `Tableau REST API` (workbook={workbookid})')

        url = f'{self.baseapi}/sites/{self.siteid}/workbooks/{workbookid}/views'
        optional = f'{url}?includeUsageStatistics={str(usagestats).lower()}'

        request = self.session.get(optional)
        response = Response(request, func)

        views = dict()
        for view in response.body['views']['view']:
            viewid = view['id']
            views[viewid] = view

        logging.debug(f'Found {len(views)} views on `Tableau REST API` (workbook={workbookid})')

        return views

    @min_api_version('2.5')
    def queryWorkbook(self, workbookid):
        """Query Workbook Information on Tableau Server.

        Parameters
        ----------
        workbookid : str
            ID of workbook to query information about.

        Returns
        -------
        workbook : dict
            Dict of workbook details from Tableau Server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying workbook on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/workbooks/{workbookid}'

        request = self.session.get(url)
        response = Response(request, func)

        workbook = response.body['workbook']

        return workbook

    @min_api_version('2.5')
    def queryWorkbookConnections(self, workbookid):
        """Query Workbook Connections on Tableau Server.

        Parameters
        ----------
        workbookid : str
            ID of workbook to query information about.

        Returns
        -------
        response : dict
            Dict of workbook connections from Tableau Server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying workbook connections on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/workbooks/{workbookid}/connections'

        request = self.session.post(url)
        response = Response(request, func)

        connections = dict()
        for connection in response.body['connections']['connection']:
            connectionid = connection['id']
            connections[connectionid] = connection

        logging.debug(f'Found {len(connections)} connections on `Tableau REST API` (workbook={workbookid})')

        return connections

    @min_api_version('2.5')
    def queryWorkbooksforSite(self):
        raise NotImplementedError

    @min_api_version('2.5')
    def queryWorkbooksforUser(self, owner=True, pagesize=1000):
        """Query Viewable Workbooks on Tableau Server for User.

        Parameters
        ----------
        owner : bool, optional (default=True)
            Flag for limiting results to user owned workbooks only.
        pagesize : int, optional (default=1000)
            Number of items to fetch per request.

        Returns
        -------
        workbooks : dict
            Dict of viewable workbooks on server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying workbooks for user on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/users/{self.userid}/workbooks'

        workbooks = dict()

        done, totalsize, pagenumber = False, 0, 1
        while not done:
            paged = f'{url}?ownedBy={owner}&pageSize={pagesize}&pageNumber={pagenumber}'

            request = self.session.get(paged)
            response = Response(request, func)

            pagenumber += 1
            totalsize += response.pagination.pageSize
            done = response.pagination.totalAvailable <= totalsize

            for workbook in response.body['workbooks']['workbook']:
                workbookid = workbook['id']
                workbooks[workbookid] = workbook

        logging.debug(f'Found {len(workbooks)} workbooks on `Tableau REST API` (site={self.site})')

        return workbooks

    @min_api_version('2.5')
    def downloadWorkbook(self):
        raise NotImplementedError

    @min_api_version('2.5')
    def updateWorkbook(self):
        raise NotImplementedError

    @min_api_version('2.5')
    def updateWorkbookConnection(self, workbookid, connectionid, details):
        """Update Workbook Connection Details on Tableau Server.

        Parameters
        ----------
        workbookid : str
            ID of workbook to update connection of.
        connectionid : str
            ID of Connection to update details of.
        details : dict
            Connection details to update the server with.
            Form -> serverAddress, serverPort, userName, password, embedPassword

        # NOTE(LEVI~20171122): Does user need help with `details`?

        Returns
        -------
        connection : dict
            Connection details after updating server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Updating workbook connections on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/workbooks/{workbookid}/connections/{connectionid}'

        request = self.session.put(url, json=details)
        response = Response(request, func)

        connection = response.body['connection']

        return connection

    @min_api_version('2.5')
    def deleteWorkbook(self):
        raise NotImplementedError

    ########## Area: Data sources ##########
    # Additional Endpoints: publishDatasource, addTagstoDatasource,
    # deleteTagfromDatasource, getDatasourceRevisions, downloadDatasource,
    # downloadDatasourceRevision, updateDatasource, updateDatasourceConnection,
    # deleteDatasource, removeDatasourceRevision

    @min_api_version('2.5')
    def queryDatasource(self):
        raise NotImplementedError

    @min_api_version('2.5')
    def queryDatasources(self):
        raise NotImplementedError

    @min_api_version('2.5')
    def queryDatasourceConnections(self):
        raise NotImplementedError

    ########## Area: Users and Groups ##########
    # Additional Endpoints: createGroup, addUsertoGroup, addUsertoSite,
    # getUsersinGroup, getUsersonSite, queryGroups, queryUserOnSite,
    # updateGroup, updateUser, removeUserfromGroup, removeUserfromSite,
    # deleteGroup

    ########## Area: Revisions ##########
    # Additional Endpoints: getDatasourceRevisions, getWorkbookRevisions,
    # downloadDatasourceRevision, downloadWorkbookRevision,
    # removeDatasourceRevision, removeWorkbookRevision

    ########## Area: Permissions ##########
    # Additional Endpoints: addDatasourcePermissions, addProjectPermissions,
    # addDefaultPermissions, addWorkbookPermissions, queryDatasourcePermissions,
    # queryProjectPermissions, queryDefaultPermissions, queryWorkbookPermissions,
    # deleteDatasourcePermission, deleteProjectPermission, deleteDefaultPermission,
    # deleteWorkbookPermission

    ########## Area: Jobs, Tasks, and Schedules ##########
    # Additional Endpoints: createSchedule, queryExtractRefreshTasks,
    # updateSchedule, deleteSchedule

    @min_api_version('2.5')
    def queryJob(self, jobid):
        """Get information about a specific job on Tableau Server,

        Parameters
        ----------
        jobid : str
            ID of job to check status/details for.

        Returns
        -------
        job : dict
            Dict of current job details & notes on server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying Job Details on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/jobs/{jobid}'

        request = self.session.get(url)
        response = Response(request, func)

        job = response.body['job']

        return job

    @min_api_version('2.6')
    def getExtractRefreshTask(self, taskid):
        """Query Single Refresh Task on Tableau Server.

        Returns
        -------
        task : dict
            Dict of viewable extract refresh tasks on server.

        # NOTE(LEVI~20171122): Cannot access as non-admin (Why Tableau?)

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Getting Extract Refresh Task on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/tasks/extractRefreshes/{taskid}'

        request = self.session.get(url)
        response = Response(request, func)

        task = response.body['task']['extractRefresh']

        return task

    @min_api_version('2.6')
    def getExtractRefreshTasks(self):
        """Query Viewable Refresh Tasks on Tableau Server.

        Returns
        -------
        tasks : dict
            Dict of viewable extract refresh tasks on server.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Getting Extract Refresh Tasks on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/tasks/extractRefreshes'

        request = self.session.get(url)
        response = Response(request, func)

        tasks = dict()
        for task in response.body['tasks']['task']:
            taskid = task['extractRefresh']['id']
            tasks[taskid] = task['extractRefresh']

        logging.debug(f'Found {len(tasks)} tasks on `Tableau REST API` (site={self.site})')

        return tasks

    @min_api_version('2.5')
    def querySchedules(self):
        raise NotImplementedError

    @min_api_version('2.6')
    def runExtractRefreshTask(self, taskid):
        """Run Refresh Extract Tasks on Tableau Server.

        Parameters
        ----------
        taskid : str
            ID of task to run extract refresh on.

        Returns
        -------
        connection : dict
            Connection details after updating server.

        Notes
        -----
        (Below comes from API Documentation)
        This method runs the scheduled task for the data source extract or the
        published workbook that connects to the data extract. You must first
        schedule the task for the extract refresh. You can do this using the
        Create Schedule method to create the task. To get information about the
        extract refresh task, use the Get Extract Refresh Tasks method, which
        returns the extractRefresh ID that you use as the task-id.

        The method adds the refresh task to the backgrounder queue, at the
        default priority. Depending upon the backgrounder load, the task might
        not run immediately. The method returns information about the backgrounder
        job responsible for running the extract refresh task. Note that the job
        returned cannot currently be queried from the Query Job method.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Running Refresh Extract Task on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/sites/{self.siteid}/tasks/extractRefreshes/{taskid}/runNow'

        request = self.session.post(url, json=dict())
        response = Response(request, func)

        job = response.body['job']

        return job

    ########## Area: Subscriptions ##########
    # Additional Endpoints: createSubscription, querySubscription,
    # querySubscriptions, updateSubscription, deleteSubscription

    ########## Area: Favorites ##########
    # Additional Endpoints: addDatasourcetoFavorites, addViewtoFavorites,
    # addWorkbooktoFavorites, deleteDatasourcefromFavorites,
    # deleteViewfromFavorites, deleteWorkbookfromFavorites, getFavoritesforUser

    ########## Area: Publishing ##########
    # Additional Endpoints: initiateFileUpload, appendtoFileUpload,
    # publishDatasource, publishWorkbook, updateSite

    ########## Area: Server ##########
    # Additional Endpoints: None

    @min_api_version('2.5')
    def serverInfo(self):
        """Fetch server version and information on Tableau Server.

        Returns
        -------
        server : dict
            Server version(s) information.

        """
        func = sys._getframe().f_code.co_name  # pylint: disable=protected-access
        logging.info(f'Querying Server Information on `Tableau REST API` (site={self.site})')

        url = f'{self.baseapi}/serverinfo'

        request = self.session.get(url, json=dict())
        response = Response(request, func)

        server = response.body['serverInfo']

        return server


class TableauREST(BaseTableauREST):
    """Base Tableau REST API Interface w/ Helper Methods."""

    def __init__(self, server, username, password, **kwargs):
        super().__init__(server, username, password, **kwargs)
        self.api = self.serverInfo()['restApiVersion']

    def runExtractRefreshTaskSync(self, taskid, sync=False, frequency=60):
        """Helper method to ensure Refresh completions.

        This is a 'private' method as it does not directly reflect a
        specific API call, but rather attempts to replicate the sync
        functionality of the tabcmd refresh method.

        Parameters
        ----------
        taskid : str
            Id of task to run refresh extract on.
        sync : bool, optional (default=False)
            Flag for awaiting completion of workbook refresh.
        frequency : int, optional (default=60)
            How often (seconds) it should check workbook status.
            i.e. How many seconds should it sleep for between checks?

        Notes
        -----
        The `sync` functionality doesn't actually validate the refresh
        task job has been complete. As of 10.4 (API 2.7), there doesn't
        appear to be a way to validate the jobs status. Instead this
        compares 'updatedAt' values for a given workbook before and after
        running the `runExtractRefreshTask` method. In general, this
        should be 'close enough'. Just don't update a workbook while it
        is refreshing.

        # NOTE(LEVI~20171127): It appears as though using `updatedAt`
        # may not work as it seems moving from the queue to active
        # changes the field value? Need to look into this.

        """
        # FIXME(LEVI~20171122): Can refresh task be queried by `queryJob`?
        # If yes, this should be switched to `queryJob` to get around below
        # flaws. Documentation currently says no however.

        # NOTE(LEVI~20171122): Stupid workaround for non-admin right issue
        task = self.getExtractRefreshTasks()[taskid]

        workbookid = task['workbook']['id']
        original = self.queryWorkbook(workbookid)

        logging.info(f'Beginning Sync Refresh Extract for {original["contentUrl"]}')

        self.runExtractRefreshTask(taskid)

        while sync and self.queryWorkbook(workbookid)['updatedAt'] == original['updatedAt']:
            logging.debug(f'{taskid} for {workbookid} not complete (sleeping={frequency}secs)')
            time.sleep(frequency)

        logging.info(f'Completing Sync Refresh Extract for {original["contentUrl"]}')

        return None
