#!/usr/bin/env python3

import libtmux
from datetime import datetime
from datetime import datetime, timezone
from aw_core.models import Event
from aw_client import ActivityWatchClient

import logging as log

CLIENTNAME = 'tmux-attached'
BUCKETNAME = CLIENTNAME
EVENTTYPE = 'tmux.sessions.attached'
POLL_INTERVAL = 10
PULSETIME_INTERVAL = 15

l = log.getLogger('aw-watcher-tmux-attached')


class SessionTracker():
    def __init__(self, testing=False):
        self.srv = libtmux.server.Server()
        self.aw_client = ActivityWatchClient(CLIENTNAME, testing=testing)
        self.bucket_id = f'{BUCKETNAME}_{self.aw_client.client_hostname}'
        self.aw_client.create_bucket(self.bucket_id, event_type=EVENTTYPE)

    def update(self):
        curr_attached = [
            s.name for s in self.srv.sessions
            if s.session_attached != "0"
        ]
        if len(curr_attached) == 0:
            return

        heartbeat_data = {
            'title': ','.join(sorted(curr_attached)),
            'sessions': curr_attached,
        }
        now = datetime.now(timezone.utc)
        heartbeat_event = Event(timestamp=now, data=heartbeat_data)
        self.aw_client.heartbeat(
            self.bucket_id,
            heartbeat_event,
            pulsetime=PULSETIME_INTERVAL,
            queued=True,
        )
