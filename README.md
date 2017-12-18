# DOMjudge-ext
Some extensions and scripts for DOMjudge for regional contest.

## Event feed exporter
located at /feed 

Modified from DOMjudge master branch. Compatible for DOMJudge v5.3.0.

Need to modify manually:

1. Delete <?xml> part
2. ```<contest-id/>``` need to fill, for example, ```<contest-id>1</contest-id>```
3. Delete all team without affiliation

Author: @dailongao, licensed under GPL v2.

## event-feed-to-result.py
located at /scripts

Transform event-feed.xml to result.xml for icpc.baylor.edu.

Author: @TsReaper, licensed under MIT.

## Stress-test

Use https://github.com/ubergeek42/domjudge-gatling

Notice:

1. Remove CSRF part.
2. Modify the last part of script to enable stress test instead of testing one single pass.
3. Use clean database to test.

Take a look of our competition document to get ready for stress test.



