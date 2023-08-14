#!/bin/bash

# clean up
find . -regex '^.*\(__pycache__\|\.py[co]\)$' -delete

# make ankiaddon
zip -r ankicord.ankiaddon \
    __init__.py \
    config.json \
    config.md \
    manifest.json \
    README.md \
    src
