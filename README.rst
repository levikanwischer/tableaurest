*Warning: This package is still in a pre-v1 development phase. Breaking changes are likely to occur without warning.*


tableaurest
===========
A Python based Tableau REST API interface.

Installation
------------
``tableaurest`` is a Python 3.6+ based package, and can be installed through ``pip`` using the following command.

    .. code-block:: bash

        $ python -m pip install tableaurest


Examples
========

Print count of Workbooks Owned by Login User.

    .. code-block:: python

        >>> from tableaurest import TableauREST
        >>>
        >>> SERVER = 'YOUR_TABLEAU_URL'
        >>> USERNAME = 'YOUR_TABLEAU_USERNAME'
        >>> PASSWORD = 'YOUR_TABLEAU_PASSWORD'
        >>>
        >>> with TableauREST(SERVER, USERNAME, PASSWORD) as restapi:
        >>>     workbooks = restapi.queryWorkbooksforUser(owner=True)
        >>>
        >>> print(f'{USERNAME} owns {len(workbooks)} workbooks on {SERVER}.')
        'YOUR_TABLEAU_USERNAME owns 4 workbooks on YOUR_TABLEAU_URL.'


Extras
======

Contribute
----------
#. Check/Open Issue for related topics of change
#. Fork/Clone/Branch repo and make discussed/desired changes
#. Add tests (``¯\_(ツ)_/¯``) and document code w/ numpy formatting
#. Open Pull Request and notify maintainer
