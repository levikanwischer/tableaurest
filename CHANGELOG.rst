Changelog
=========

All notable changes to this project will be documented in this file.


Develop_
--------

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


Unreleased_
-----------


v0.2.3_
-------

Changed
~~~~~~~
- Correct queryWorkbookConnections to use GET method
- Correct queryDatasourceConnections to use GET method
- Add 'connection' dict wrapper updateWorkbookConnection details


v0.2.2_
-------

Changed
~~~~~~~
- Correct userid/siteid updating on switchSite method


v0.2.1_
-------

Changed
~~~~~~~
- Some light cleanup around formatting, logging, & bug fixes


.. _Develop: https://github.com/levikanwischer/tableaurest/compare/master...develop
.. _Unreleased: https://github.com/levikanwischer/tableaurest/compare/v0.2.3...master
.. _v0.2.3: https://github.com/levikanwischer/tableaurest/compare/v0.2.2...v0.2.3
.. _v0.2.2: https://github.com/levikanwischer/tableaurest/compare/v0.2.1...v0.2.2
.. _v0.2.1: https://github.com/levikanwischer/tableaurest/compare/v0.2.0...v.0.2.1
