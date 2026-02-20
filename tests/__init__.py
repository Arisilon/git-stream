"""This is the unit test driver module."""
import sys
from pathlib import Path

# Ensure the local source tree takes precedence over any installed version
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Force reimport of git_stream from the local source
if 'git_stream' in sys.modules:
    # Remove all git_stream submodules from the cache
    for mod_name in list(sys.modules):
        if mod_name == 'git_stream' or mod_name.startswith('git_stream.'):
            del sys.modules[mod_name]
