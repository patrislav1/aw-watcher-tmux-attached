#!/usr/bin/env python3

import argparse
import importlib.metadata
import logging
import signal
import time

from .watch_tmux_attached import SessionTracker, POLL_INTERVAL

terminate = False


def sigterm_handler(signal, frame):
    global terminate
    terminate = True


def main():
    parser = argparse.ArgumentParser(
        description='ActivityWatch watcher for attached Tmux sessions'
    )

    parser.add_argument('-t', '--testing',
                        action='store_true',
                        help='connect to ActivityWatch testing server')

    parser.add_argument('-v', '--verbosity',
                        type=int,
                        help='set verbosity (0=quiet, 1=info, 2=debug)'
                        )

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' +
                        importlib.metadata.version('aw-watcher-tmux-attached')
                        )

    args = parser.parse_args()

    verbosity = args.verbosity if args.verbosity is not None else 0
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        level=[logging.WARNING, logging.INFO, logging.DEBUG][verbosity]
    )
    log = logging.getLogger('aw-watcher-tmux-attached')

    signal.signal(signal.SIGTERM, sigterm_handler)

    tracker = SessionTracker(testing=args.testing)

    try:
        with tracker.aw_client:
            while not terminate:
                tracker.update()
                time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log.info('Interrupted')

    log.info('Terminated')


if __name__ == '__main__':
    main()
