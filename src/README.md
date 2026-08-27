# Source and generated data

- `core/` is the pinned [VMaNGOS core](https://github.com/vmangos/core)
  submodule.
- `database/` is the pinned world-database submodule and generated migration
  workspace.
- `data/` holds locally extracted DBC, map, vmap, and mmap client data. It is
  intentionally not committed.
- `ccache/` is the local compiler cache. It is intentionally not committed.

Use `git submodule update --init --recursive` to restore the pinned source
revisions; do not update submodules with `--remote` during a reproducible build.
