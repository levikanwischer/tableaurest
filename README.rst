*Warning: This repo is still in a pre-v1 development phase. Breaking changes are likely to occur without warning.*


tableaurest
===========
A Python Based Tableau REST API Interface.


Installation
------------
``tableaurest`` is a Python 3.6+ based package, and can be installed through ``pip`` using the following command.

    .. code-block:: bash

        $ python -m pip install tableaurest


Issues
------
If you encounter any issues, please first search existing 'Issues' on GitHUb. If none match your issue, please create a new 'Issue' accordingly to initialize discussion. Thanks.


Examples
========

Print Count of Workbooks Owned by Login User

    .. code-block:: python

        >>> import tableaurest
        >>>
        >>> SERVER = 'YOUR_TABLEAU_URL'
        >>> USERNAME = 'YOUR_TABLEAU_USERNAME'
        >>> PASSWORD = 'YOUR_TABLEAU_PASSWORD'
        >>>
        >>> with tableaurest.TableauREST() as rest.api:
        >>>     workbooks = restapi.queryWorkbooksforUser(owner=True)
        >>>
        >>>
        >>> workbooknum = len(workbooks.keys())
        >>> print(f'{USERNAME} owns {workbooknum} workbooks on {SERVER}.')
        'Jane owns 12 workbooks on https://tableau.fakecompany.com.'


Extras
======

Contribute
----------
#. Check/Open Issue for related topics of change
#. Fork/Clone/Branch repo and make discussed/desired changes
#. Add tests (``¯\_(ツ)_/¯``) and document code w/ numpy formatting
#. Open Pull Request and notify maintainer
