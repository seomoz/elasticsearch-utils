Elasticsearch Utilities
=======================
This contains some notes, scripts, snippets, etc. from investigating the slow
query performance we were seeing with our elasticsearch cluster.

Pylucene
========
We wanted to eliminate elasticsearch as a culprit for adding overhead that was
slowing down our queries. To that end, we decided to try to use pylucene to
directly query the shards to either blame elasticsearch or the lucene indexes
or the underlying environment. Check out the `pylucene/README.md` for install
details.

Freshscape Configuration
========================
If you start up a single-node elasticsearch cluster, you can reconfigure 
`/etc/freshscape.conf` to point to `localhost:9200` as the sole elasticsearch
node. In addition, for replaying traffic, it's helpful to start up a local
redis server and then you can insert jobs to into the `index` stage to replay
crawl traffic.

Replaying Traffic
=================
The `shovel replay` utility lists out all the crawl drops for a given date in
the `YYYY-MM-DD` format and inserts `index` jobs to the configured freshscape
queue. From there, you can spin up some qless workers in a screen session:

    qless-py-worker --host localhost:6379 -w 50 -q index -d /media/raid/qless

Benchmarks
==========
There's alsow now the `shovel bench` utility that accepts a path and an input
file. Each line in the input file is interpreted as a query, or it defaults to
read `stdin`. The path should contain one or more lucene indexes (which it
attempts to find recursively). For example, if you have your elasticsearch data
stored in `/media/raid/data`, you could invoke it:

```bash
# Query all the indexes for 'hello'
echo 'hello' | shovel bench --path /media/raid/data
# Run a bunch of queries on a particular index
cat queries | shovel bench --path /media/raid/data/cluster/nodes/0/indices/2012-12-21/0/
