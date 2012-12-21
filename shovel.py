#! /usr/bin/python2.7


import time
from shovel import task


def run_query(query, searchers):
    from lucene import QueryParser, Version, StandardAnalyzer
    analyzer = StandardAnalyzer(Version.LUCENE_36)
    for searcher in searchers:
        query = QueryParser(
            Version.LUCENE_36, "_all", analyzer).parse(query)
        hits = searcher.search(query, 1000)


def bench_query(query, searchers):
    start = -time.time()
    run_query(query, searchers)
    return start + time.time()


@task
def bench(path=None, infile='-'):
    '''Run a benchmark on all the queries in the provided infile (or - for
    stdin), using all the for lucene indexes in the data directory.'''
    import os
    import lucene
    from lucene import (
        MMapDirectory, File, IndexSearcher, Version)

    print 'Initializing lucene VM...'
    lucene.initVM()
    print 'Done.'

    # For tracking times, and all of our indexes
    query_times = []
    searchers = []

    import os
    home = os.path.abspath(path or '.')
    print 'Finding lucene indexes in %s...' % home
    paths = [i[0] for i in os.walk(home)]
    paths = [p for p in paths if p.endswith('/index')]
    print 'Found %i indexes' % len(paths)

    searchers = []
    for path in paths:
        print 'Opening %s' % path
        searchers.append(IndexSearcher(MMapDirectory(File(path))))

    print 'Running queries...'
    if infile == '-':
        # Read from stdin
        import sys
        for line in sys.stdin:
            r = bench_query(line.strip(), searchers)
            print '%s => %fs' % (line.strip(), r)
            query_times.append(r)
    else:
        with open(infile) as fin:
            for line in fin:
                r = bench_query(line.strip(), searchers)
                print '%s => %fs' % (line.strip(), r)
                query_times.append(r)

    import math
    avg = sum(query_times) / len(query_times)
    std = math.sqrt(sum(
        [pow(i - avg, 2) for i in query_times]) / len(query_times))
    print 'Query times:'
    print '    Avg: %fs' % avg
    print '    Std: %fs' % std
    print '    Min: %fs' % min(query_times)
    print '    Max: %fs' % max(query_times)


@task
def replay(date):
    '''Replay all the crawl traffic from a particular day'''
    from freshscape import s3, drop, queue
    bucket = s3.s3.conn.get_bucket('freshscape')
    for key in bucket.list('dumps/%s' % date):
        if '.dnd' in key.name:
            print 'Skipping %s' % key.name
            continue
        print 'Putting job %s' % key.name
        o = queue.master.queues['index'].put(drop.UrlDrop, {
            'did': key.name.partition('/')[2].partition('.')[0],
            'dump': key.name
        })
