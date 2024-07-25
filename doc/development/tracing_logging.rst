.. _tracing_logging:

Tracing & logging
=================
As `cotainr` is a tools that wraps other tools, e.g. Singularity and Conda, quite a lot of text messages are passed around. In particular, we handle:

- Printed information from `cotainr`.
- Logging information from `cotainr`.
- Messages sent to `stdout` by subprocess, e.g. Singularity or Conda.
- Messages sent to `stderr` by subprocess, e.g. Singularity or Conda.

All of these have to be filtered, annotated, routed, and displayed on the console and/or written to files.

The `cotainr` tracing & logging setup handles all of this in a consistent way.

Cotainr logging
---------------
Logging in `cotainr` is handled using the `Python standard library logging module <https://docs.python.org/3/library/logging.html>`_. We use the standard convention of creating loggers on a per-module basis, i.e. all modules in `cotainr` include a :code:`logger = logging.getLogger(__name__)` line following any imports. Logging is then done using the module logger, e.g. :code:`logger.info("Some logged message.")`.

The `cotainr` library does not define any `logging handlers <https://docs.python.org/3/howto/logging.html#handlers>`_. This is left for the user of the library. When using the :ref:`cotainr CLI <command_line_interface>`, though, a set of handlers is defined as outlined in the description of the `Cotainr CLI tracing`_.

Cotainr CLI tracing
-------------------
When using the `cotainr CLI`, quite a lot of messages from `cotainr` and subprocesses needs to filtered, annotated, routed, and displayed on the console and/or written to files to provide the most useful information to the user. This process of providing the most useful information to the user, we refer to as "tracing." Tracing in `cotainr` is done using three separate abstractions:

- `Forwarding of stdout/stdout from subprocesses`_
- `Processing of log messages`_
- `Adding a console spinner`_

Forwarding of stdout/stdout from subprocesses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When external programs, e.g. Singularity or Conda, are called in separate subproceses, their output on `stdout` / `stderr` is captured and forwarded in real time to the main process. It may then either be directly piped to the main process `stdout` / `stderr` or further processed using the setup described in `Processing of log messages`_.

The real time forwarding of `stdout` / `stderr` is implemented by the :func:`cotainr.util.stream_subprocess` function which is used when running the subprocesses.

Processing of log messages
~~~~~~~~~~~~~~~~~~~~~~~~~~
The `Python logging <https://docs.python.org/3/library/logging.html>`_ machinery is used for advanced processing of all text messages to be displayed on the console and, optionally, written to a file.

This setup is primarily implemented by two classes :class:`cotainr.tracing.LogDispatcher` and :class:`cotainr.tracing.LogSettings`. Each subprocess is linked to a :class:`~cotainr.tracing.LogDispatcher` instance which sets up the logging machinery based on the supplied :class:`~cotainr.tracing.LogSettings`, any `filters <https://docs.python.org/3/library/logging.html#filter-objects>`_, and a `map_log_level_func` function, to:

- Determine the correct log level for loggers and handlers based on `verbosity` (as described in `Cotainr tracing log levels`_).
- Specify the logging message format based on `verbosity`.
- Setup `StreamHandlers <https://docs.python.org/3/library/logging.handlers.html#streamhandler>`_ for `stdout` / `stderr`.
- Setup `FileHandlers <https://docs.python.org/3/library/logging.handlers.html#filehandler>`_ for `stdout` / `stderr`, if requested.
- Apply any filters to modify and/or remove log messages.
- Add colored console output based on log level, as implemented in :class:`cotainr.tracing.ColoredOutputFormatter`, if requested.

The :class:`~cotainr.tracing.LogDispatcher` then defines methods :meth:`~cotainr.tracing.LogDispatcher.log_to_stdout` and :meth:`~cotainr.tracing.LogDispatcher.log_to_stderr` which may be used with subprocesses to log to `stdout` / `stderr`, respectively, at a message log level determined by the provided `map_log_level_func` function.

In order to take advantage of this machinery, CLI subcommands must:

- Implement the `--verbose` and `--quiet` arguments and map them to the `verbosity` level as described in `Cotainr tracing log levels`_.
- Implement the `--log-to-file` argument and map it to a `log_file_path`.
- Implement the `--no-color` argument.
- Instantiate a :class:`~cotainr.tracing.LogSettings` object and pass it onto any cotainr functionality that may spawn subprocesses.

An example of a subcommand implementing this is :class:`cotainr.cli.Build`.

Furthermore, `cotainr` functionality that spawn subprocesses, e.g. :class:`cotainr.container.SingularitySandbox` or :class:`cotainr.pack.CondaInstall` must:

- Implement a `map_log_level_func` function, that (attempts to) infers the correct logging level for a given message.
- Instantiate their own :class:`~cotainr.tracing.LogDispatcher`, which should be passed to :func:`cotainr.util.stream_subprocess` when spawning subprocesses.

An example of this is given in :class:`cotainr.pack.CondaInstall` which implements the static method :meth:`cotainr.pack.CondaInstall._map_log_level` and instantiates a :class:`~cotainr.tracing.LogDispatcher` in its constructor.

Similarly to the setup done by :class:`~cotainr.tracing.LogDispatcher` for subprocesses, the :class:`cotainr.cli.CotainrCLI` sets up the `cotainr` root logger for the main process based on the subcommand :class:`~cotainr.tracing.LogSettings`. This is implemented in the :meth:`cotainr.cli.CotainrCLI._setup_cotainr_cli_logging` method.

Cotainr tracing log levels
~~~~~~~~~~~~~~~~~~~~~~~~~~
Within `cotainr`, we map the subcommand `--verbose` / `--quiet` flags to a `verbosity` level, one of the `standard Python logging levels <https://docs.python.org/3/library/logging.html#logging-levels>`_ (independently for `cotainr` and :class:`~cotainr.tracing.LogDispatcher`s), and `--verbose` / `--quiet` levels for subprocesses, e.g. Singularity or Conda. Specifically the mapping is as shown in the below table:

===================  =====================  ====================  ===========================  =======================  =================
  cotainr verbose      cotainr verbosity     cotainr log level      LogDispatcher log level      Singularity verbose      Conda verbose
===================  =====================  ====================  ===========================  =======================  =================
-q                   -1                     CRITICAL              CRITICAL                     -s                       -q
<None>               0                      INFO                  WARNING                      -q                       -q
-v                   1                      INFO                  INFO                         <None>                   <None>
-vv                  2                      DEBUG                 INFO                         <None>                   -v
-vvv                 3                      DEBUG                 DEBUG                        -v                       -vv
-vvvv                4                      DEBUG                 DEBUG                        -v                       -vvv
===================  =====================  ====================  ===========================  =======================  =================

The subcommand `--verbose` / `--quiet` flags are mapped to a `verbosity` level as part of the parsing of the CLI arguments, e.g. as in :class:`cotainr.CLI.build.add_arguments`. Based on the `verbosity` level,

- the `cotainr` log level (as used for filtering messages in loggers and handlers) is set in the :meth:`cotainr.cli.CotainrCLI._setup_cotainr_cli_logging` method.
- the :class:`~cotainr.tracing.LogDispatcher` log level (as used for filtering messages in loggers and handlers) is set as part of its construction, i.e. in :meth:`cotainr.tracing.LogDispatcher._determine_log_level` method.
- the Singularity `--verbose` / `--quiet` flags are injected into Singularity subprocess commands using the :meth:`cotainr.container.SingularitySandbox._add_verbosity_arg` method.
- the Conda `-v` / `-q` flags are appended to Conda subprocess commands using the :meth:`cotainr.pack.CondaInstall._conda_verbosity_arg` method.

Note the this means that logged messages may be filtered by both the subprocess command (e.g. singularity), the logger used to log the message, and the handler used to emit the message to the console and/or a file.

Adding a console spinner
~~~~~~~~~~~~~~~~~~~~~~~~
For a given block of code, a spinner may be added to any console output to `stdout` / `stderr` from that code by running it in a :class:`cotainr.tracing.ConsoleSpinner` context.

The spinner is implemented in the :class:`cotainr.tracing.MessageSpinner` class which manages a separate thread updating the spinner for each individual message. Within the :class:`~cotainr.tracing.ConsoleSpinner` context, the spinning message is updated by monkey patching :py:meth:`sys.stdout.write`/:py:meth:`std.stderr.write` with :class:`cotainr.tracing.StreamWriteProxy` wrappers that make sure to update the spinning message whenever something is written to :py:data:`sys.stdout`/:py:data:`sys.stderr`.
