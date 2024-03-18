#!/usr/bin/env python3

import signal
import libtmux
from datetime import datetime
import time
from datetime import datetime, timedelta, timezone
from aw_core.models import Event
from aw_client import ActivityWatchClient

CLIENTNAME = 'tmux-attached'
BUCKETNAME = CLIENTNAME
EVENTTYPE = 'tmux.sessions.attached'
POLL_INTERVAL = 10
PULSETIME_INTERVAL = 15

terminate = False


def sigterm_handler(signal, frame):
    global terminate
    terminate = True


signal.signal(signal.SIGTERM, sigterm_handler)


class SessionTracker():
    def __init__(self, testing=False):
        self.srv = libtmux.server.Server()
        self.aw_client = ActivityWatchClient(CLIENTNAME, testing=True)
        self.bucket_id = f'{BUCKETNAME}_{self.aw_client.client_hostname}'
        self.aw_client.create_bucket(self.bucket_id, event_type=EVENTTYPE)

    def update(self):
        curr_attached = [s.name for s in self.srv.attached_sessions]
        if len(curr_attached) == 0:
            return

        print(f'attached: {curr_attached}')

        heartbeat_data = {"sessions": curr_attached}
        now = datetime.now(timezone.utc)
        heartbeat_event = Event(timestamp=now, data=heartbeat_data)
        self.aw_client.heartbeat(
            self.bucket_id,
            heartbeat_event,
            pulsetime=PULSETIME_INTERVAL,
            queued=True,
        )


tracker = SessionTracker(testing=True)

with tracker.aw_client:
    while not terminate:
        tracker.update()
        time.sleep(POLL_INTERVAL)

print('Terminated')
