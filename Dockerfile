# Don’t forget to change the version tag v0.19.0
# to the version you were working with locally when creating your notebooks.
# See https://hub.docker.com/r/manimcommunity/manim/tags
FROM docker.io/manimcommunity/manim:v0.19.0

COPY --chown=manimuser:manimuser . /manim