.. _contributing:

Contributing
============

|travis| |coveralls|

Contributions of any form are always welcome, whether it is general feedback on
the use of PyWayland, bug reports, or pull requests.  All development is done
through GitHub_.

If you wish to develop PyWayland, it is recommended that you follow the outline
given in :ref:`install-source`.  A few things to be aware of when writing code:

- Continuous integration testing in done with Travis_, and tests are run
  against all supported Python versions (currently 3.6+ and PyPy 3).  You can
  check that your changes pass locally by running ``py.test`` from the root
  directory (this requires installing pytest_).  Currently, the tests also run
  with nose_, however, they may not always in the future.

- Code coverage is assessed using Coveralls_.  Currently, coverage is fairly
  low, any work to help this would be greatly appreciated.

- Code quality is assessed in the tests with flake8_, be sure any new code
  meets Python standards.

- Type annotations are included in much of the codebase and checked with mypy.
  Additional checks using other type checkers are appreciated.

.. _Coveralls: https://coveralls.io/r/flacjacket/pywayland
.. _GitHub: https://github.com/flacjacket/pywayland/
.. _Travis: https://travis-ci.org/flacjacket/pywayland
.. _flake8: https://flake8.readthedocs.org
.. _nose: https://nose.readthedocs.org
.. _pytest: https://pytest.org

.. |travis| image:: https://travis-ci.org/flacjacket/pywayland.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/flacjacket/pywayland
.. |coveralls| image:: https://coveralls.io/repos/flacjacket/pywayland/badge.svg?branch=master
    :alt: Build Coverage
    :target: https://coveralls.io/r/flacjacket/pywayland
