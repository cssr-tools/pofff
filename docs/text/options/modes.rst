Execution modes
===============

``single`` generates files, runs OPM Flow, creates benchmark data, and optionally creates figures. ``files`` creates inputs only and cannot use ``-f all``. ``data`` processes an existing simulation. ``ert`` and ``everest`` run their corresponding history-matching workflows. ``fair`` uses fixed benchmark comparison settings and rejects conflicting input, figure, time, and experiment options. ``none`` skips simulation work and is useful for plotting existing results.
