#!/usr/bin/python

import hashlib
import json
import os
import random
import sys
import zerorpc

from jinja2 import Template


"""
Simple re-configuration sequence for a cluster of NATS brokers. The actual re-configuration
(via a automaton state-machine transition) is executed if the MD5 digest of the latest set of
information we care about differs from the previous one. Right now we just care about the
broker IP addresses.

@todo what to do upon a configuration request failure?
"""

if __name__ == '__main__':

    assert 'KONTROL_PORT' in os.environ, '$KONTROL_PORT undefined (bug ?)'
    port = int(os.environ['KONTROL_PORT'])

    def _rpc(ip, cmd):
        
        try:

            #
            # - use zerorpc to request a script invokation against a given pod
            # - default on returning None upon failure
            #
            client = zerorpc.Client()
            client.connect('tcp://%s:%d' % (ip, port))
            return client.invoke(json.dumps({'cmd': cmd}))
            
        except Exception:
            return None

    #
    # - retrieve the latest state if any via $STATE
    # - retrieve the latest set of pods via $PODS
    # - extract the info we care about into a json payload
    #
    last = json.loads(os.environ['STATE']) if 'STATE' in os.environ else {'md5': None}
    pods = json.loads(os.environ['PODS'])
    peers = [pod['ip'] for pod in pods]
    payload = \
    {
        'peers': peers
    }

    #
    # - compare the latest MD5 digest for the payload with the previous one
    # - if there is no difference exit now
    #
    hasher = hashlib.md5()
    hasher.update(json.dumps(payload))
    md5 = ':'.join(c.encode('hex') for c in hasher.digest())
    if md5 == last['md5']:

        print >> sys.stderr, 'no changes detected, skipping'
        sys.exit(0)

    #
    # - we got a change
    # - fire a request to flip each nats broker automaton to 'configure'
    # - pass the payload as argument
    # - update the state by printing it to stdout
    #
    replies = [_rpc(ip, "echo WAIT configure '%s' | socat -t 60 - /tmp/sock" % json.dumps(payload)) for ip in peers]
    assert all(reply == 'OK' for reply in replies)
    state = \
    {
        'md5': md5,
        'payload': payload
    }

    print json.dumps(state)