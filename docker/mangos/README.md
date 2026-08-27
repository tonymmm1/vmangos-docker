# World-server image

This is the minimal, non-root runtime image for `mangosd`. At startup it renders
a private configuration file from the tracked template and mounted database
secret. Client-derived DBC, map, vmap, and mmap data is mounted read-only.
