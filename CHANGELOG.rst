Changelog
=========

All notable changes to this project will be documented in this file.


Develop_
--------

Added
-----
- Expose ``impersonate`` param to ``BaseTableauREST`` initialization


Unreleased_
-----------


v0.3.0_
-------

Added
~~~~~
- All methods added for: Authentication, Sites, Projects, Subscriptions, Server

Changed
~~~~~~~
- Remove excessive (useless) dict.keys() usage from codebase
- Allow user to specify ssl verify on TableauREST init (default=True)
- Remove auth token from session header on signOut
- Update self.site (contenturl) on signIn
- Add user impersonation to signIn

Removed
~~~~~~~
- Remove custom logger(s) from submodules


v0.2.3_
-------

Changed
~~~~~~~
- Correct queryWorkbookConnections to use GET method
- Correct queryDatasourceConnections to use GET method
- Add 'connection' dict wrapper updateWorkbookConnection details
- Correct userid/siteid updating on switchSite method
- Some light cleanup around formatting, logging, & bug fixes


v0.1.0
------
- Initial release version


.. _Develop: https://github.com/levikanwischer/tableaurest/compare/master...develop
.. _Unreleased: https://github.com/levikanwischer/tableaurest/compare/v0.3.0...master
.. _v0.3.0: https://github.com/levikanwischer/tableaurest/compare/v0.2.3...v0.3.0
.. _v0.2.3: https://github.com/levikanwischer/tableaurest/compare/v0.1.0...v0.2.3
