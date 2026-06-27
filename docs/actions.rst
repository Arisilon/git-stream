Command Reference
=================

This document describes git-stream commands and stream management workflow.

Creating a stream
-----------------

Create a new stream for an existing Git repository:

.. code-block:: console

   git-stream create -p main -t MY-123 -d MY-123_feature my-feature my-org/my-repo

The `create` command initializes a stream clone under the configured `stream_home`
path and stores the stream definition in `config.yaml`.

Managing stream parents
-----------------------

Add or remove parent branches from the current stream:

.. code-block:: console

   git-stream add_parent develop
   git-stream rm_parent develop

Updating a stream
-----------------

Update the current stream from its parent branches:

.. code-block:: console

   git-stream update

Delivering changes
------------------

Deliver the stream changes to the parent branch and optionally create a GitHub PR:

.. code-block:: console

   git-stream deliver "Merge feature MY-123" --create-pr

If the repository URL contains `github`, git-stream can create a PR using the
GitHub CLI.

Inspecting and modifying configuration
--------------------------------------

Use `git-stream config` to inspect or update global settings. Only top-level settings
can be changed with `config -s`; `schema` and `streams` are read-only.

.. code-block:: console

   git-stream config
   git-stream config -s stream_home=/home/alice/git/streams

Listing and removing streams
---------------------------

List configured streams:

.. code-block:: console

   git-stream list

Remove a stream definition and optionally clean up its local clone:

.. code-block:: console

   git-stream rm --cleanup repo-alice-feature-x
