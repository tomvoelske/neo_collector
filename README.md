# neo_collector
A full system for accessing a variety of different network devices, retrieving information, and handling it

This is a bespoke system developed for Vodafone. It has been anonymised so several aspects of the code will not function properly if simply used elsewhere, though the concepts work. It is ran on a schedule via the neo_collector_nexus.py file, which runs through all of the others in sequence. Approximately 2000 devices are polled.

First, a copy of the configuration files are taken and stored on a remote server, for purposes of resilience. The data is then taken, assessed, and stored largely as JSON data. This is then sent to another remote server which then interprets it to create management dashboards and KPIs (also coded by myself, in a combination of HTML/CSS/JavaScript/PHP).

Examples of information which is extracted is: hostname, serial numbers, uptime, model and version numbers (useful for lifecycle management), etc.

Finally, there is a full progress and error reporting suite. The main process is multithreaded for the sake of performance.
