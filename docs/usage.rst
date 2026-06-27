Usage Guide
===========

git-stream is a command-line tool for managing Git streams which function as delivery branches.

Getting started
---------------

Install git-stream into a Python environment:

.. code-block:: console

   pip install git-stream

Run the tool using the installed console script:

.. code-block:: console

   git-stream <command>

Or run it as a Python module:

.. code-block:: console

   python -m git_stream <command>

Core commands
-------------

- `create` — create a new stream and initialize its Git repository.
- `list` — list all configured streams.
- `show` — display the current stream definition.
- `update` — update the current stream from its parent branches.
- `deliver` — deliver stream changes to the parent branch.
- `add_parent` / `rm_parent` — manage parent branches for a stream.
- `config` — show or set global git-stream configuration values.
- `set_value` — set or clear a stream property.
- `rm` — remove a stream configuration and optionally cleanup the branch.

Typical workflow
----------------

1. Create a stream from an existing repository:

.. code-block:: console

   git-stream create -p main -t MY-123 -d MY-123_feature my-feature my-org/my-repo

2. Work in the stream branch and commit changes.
3. Update the stream from parent branches:

.. code-block:: console

   git-stream update

4. Deliver the stream to its parent:

.. code-block:: console

   git-stream deliver "Deliver feature MY-123" --create-pr

5. Remove a completed stream:

.. code-block:: console

   git-stream rm --cleanup my-org-my-feature

Configuration
-------------

git-stream stores its configuration in an application config directory under the current user's environment.
The configuration file is created automatically on first run and is stored as `config.yaml`.

Use :doc:`configuration` for details.

Next steps
----------

- :doc:`cli_reference`
- :doc:`actions`
- :doc:`configuration`
