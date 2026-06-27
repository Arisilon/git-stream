CLI Reference
=============

Usage
-----

Run git-stream using the console script:

.. code-block:: console

   git-stream <command> [options]

Or run the module directly:

.. code-block:: console

   python -m git_stream <command> [options]

Commands
--------

`git-stream` supports the following commands:

- `add_parent <parent>` — add a parent branch to the current stream.
- `config [-s | --set] <key=value>` — display or update configuration values.
- `create [-p <parent>] [-t <ticket>] [-d <delivery_branch>] <name> <repo>` — create a new stream.
- `deliver [-p | --create-pr] <commit_message>` — deliver the current stream to its parent branch.
- `list` — list all configured streams.
- `rm [-c | --cleanup] <name>` — remove a configured stream; `--cleanup` also deletes the branch and local clone.
- `rm_parent <parent>` — remove a parent from the current stream.
- `set_value <parameter> <value>` — set or clear a parameter for the current stream.
- `show` — display the current stream definition.
- `update` — update the current stream from its parent branches.

Command examples
----------------

.. code-block:: console

   git-stream create -p main -t MY-123 my-feature my-org/my-repo
   git-stream list
   git-stream show
   git-stream update
   git-stream deliver "Merge feature MY-123" --create-pr

Configuration values
--------------------

Use `git-stream config` to inspect or update the active configuration file.

.. code-block:: console

   git-stream config
   git-stream config -s default_remote=git@github.com:

Top-level settings that can be modified with `config -s`:

- `default_remote` — default Git remote prefix used when `repo` does not start with `git@`.
- `default_pr_reviewer` — reviewer used when `--create-pr` is requested and no stream-specific reviewer is set.
- `delivery_branch_template` — template used to generate a delivery branch when not explicitly provided.
- `stream_branch_prefix` — prefix for new stream branches.
- `stream_home` — root directory used to store cloned stream repositories.

GitHub pull requests
--------------------

The `deliver` command can create a GitHub PR only when the stream repository URL contains `github`.

.. code-block:: console

   git-stream deliver "Deliver feature" --create-pr
