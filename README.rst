CWA integration
===============

This is a plugin for `pretix`_. It integrates pretix with the German Corona Warn App (CWA) by making it easy for event
organizers to generate event QR codes while at the same time making it really easy for attendees to use them and remind
them of using it.

It currently supports the following features:

* Generate a QR code that can be used to check in to the event using the CWA. The QR code can be displayed as a
  self-refreshing website, printed to paper, or embedded into a digital signage system as a PNG or SVG image.

* Automatically send a link that allows to check-in using the CWA as soon as the attendee arrived. This is sent via email
  immediately after the event ticket has been scanned at the entrance. This way, people are actively reminded of doing
  the check-in (even if they do it only afterwards), but the link is only shared with people who actually show up.

We decided against printing the CWA qr code on tickets since the `CWA FAQ`_
recommend to not make it available for people not physically present to avoid misuse.

The configuration of the plugin allows to control whether a new QR codes is generated with every time slot, or just once
per day.

It is built based on `MaZderMind's implementation`_ of the `CWA event registration spec`_.

Development setup
-----------------

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.

This plugin has CI set up to enforce a few code style rules. To check locally, you need these packages installed::

    pip install flake8 isort black docformatter

To check your plugin for rule violations, run::

    docformatter --check -r .
    black --check .
    isort -c .
    flake8 .

You can auto-fix some of these issues by running::

    docformatter -r .
    isort .
    black .

To automatically check for these issues before you commit, you can run ``.install-hooks``.

License
-------

Copyright 2021 pretix team

Released under the terms of the Apache License 2.0


.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html
.. _CWA FAQ: https://www.coronawarn.app/de/faq/#check_in_misuse
.. _MaZderMind's implementation: https://github.com/MaZderMind/cwa-qr
.. _CWA event registration spec: https://github.com/corona-warn-app/cwa-documentation/blob/c0e2829/event_registration.md
