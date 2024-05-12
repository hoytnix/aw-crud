Readme
======

Because of the nature of how iterable-imports (`lib.imports`) are implemented,
there are a few requirements for building modules:

*   The top-level init-file next to `app.py` must import blueprints.
    (Which is easy enough to commit to Git and re-use with relative-imports.)
*   The blueprints-module (`hoyt.blueprints`) must import its sub-modules.
*   Blueprint sub-modules must import their view-blueprints and all models.

The latter two sound like a pain and you may ask "Why even bother with iterable-imports when they don't seem to be saving you any work?"

Well, that's when the module-generator (similar to Ember-CLI) will save a lot of
time and pain. :-)
