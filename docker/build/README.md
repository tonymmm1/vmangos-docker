# Build image

This image compiles the pinned VMaNGOS submodule for the selected client build,
uses the persistent compiler cache under `src/ccache`, and stages the binaries
and their non-system runtime libraries under `vmangos/`.

Run it through `./setup.py`; the script supplies the selected client,
parallelism, and source revision metadata.
