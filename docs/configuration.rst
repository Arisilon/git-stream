Configuration Reference
=======================

git-stream stores its configuration in a YAML file located in the user application config directory.
The configuration file is created automatically on first run and is named `config.yaml`.

Configuration location
----------------------

The configuration file is stored under the operating system application config directory for the
current user. For example:

- Linux: `~/.config/git-stream/config.yaml`
- macOS: `~/Library/Application Support/git-stream/config.yaml`
- Windows: `%APPDATA%\git-stream\config.yaml`

Schema
------

The configuration file must include a top-level `schema` value.
The supported schema for this release is `1`.

If the file uses an unsupported schema, git-stream exits with an error.

Global settings
---------------

The top-level configuration settings are:

- `default_remote`
  - Default Git remote prefix used when the `repo` argument does not begin with `git@`.
  - Default: `git@github.com:`.
- `default_pr_reviewer`
  - Default GitHub PR reviewer used when creating a PR and no stream-specific reviewer is set.
  - Default: an empty string.
- `delivery_branch_template`
  - Template used to compute the delivery branch when one is not supplied explicitly.
  - Supports placeholders:
    - `%t` — ticket
    - `%d` — description
  - Default: `%t_%d`.
- `stream_branch_prefix`
  - Prefix for new stream branches.
  - Default: `<username>/`.
- `stream_home`
  - Root directory used to store cloned stream repositories.
  - Default: `~/git/streams`.
- `streams`
  - Mapping of configured stream names to stream metadata.
  - `git-stream` manages this section automatically.

Example configuration
---------------------

.. code-block:: yaml

   schema: 1
   default_remote: git@github.com:
   default_pr_reviewer: ''
   delivery_branch_template: '%t_%d'
   stream_branch_prefix: 'alice/'
   stream_home: '/home/alice/git/streams'
   streams:
     repo-alice-feature-x:
       repo: git@github.com:alice/repo.git
       description: feature-x
       branch: alice/feature-x
       parents:
         - main
       schema: 1
       delivery_branch: MY-123_feature-x
       ticket: MY-123
       pr_reviewer: bob

Stream definition fields
------------------------

Each configured stream includes metadata fields such as:

- `repo` — the Git repository URL.
- `description` — the friendly stream name.
- `branch` — the stream branch name.
- `parents` — list of parent branches used for updates and deliveries.
- `schema` — stream schema version.
- `delivery_branch` — explicit branch name used when delivering changes.
- `ticket` — ticket identifier used by templated delivery branch generation.
- `pr_reviewer` — GitHub reviewer used when creating a pull request.

Managing configuration
----------------------

Use the `git-stream config` command to inspect or change top-level settings. The
`schema` and `streams` values are read-only and cannot be updated with `config -s`.

.. code-block:: console

   git-stream config
   git-stream config -s default_remote=git@github.com:
