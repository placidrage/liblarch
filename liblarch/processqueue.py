# -*- coding: utf-8 -*-
"""
    liblarch.processqueue
    ~~~~~~~~~~~~~~~~~~~~~

    .. todo:: module level docstring should contain description

    :copyright: Copyright (c) 2011-2012 by the liblarch team, see AUTHORS.
    :license: LGPLv3 or later, see LICENSE for details.
"""

import threading
from gi.repository import GObject


class SyncQueue(object):
    """
    Synchronized queue for processing requests
    """

    def __init__(self):
        """
        Initialize synchronized queue.

        :callback: function for processing requests
        """
        self._low_queue = []
        self._queue = []
        self._vip_queue = []
        self._handler = None
        self._lock = threading.Lock()
        self._origin_thread = threading.current_thread()

        self.count = 0

    def process_queue(self):
        """
        Process requests from queue
        """
        for action in self.process():
            func = action[0]
            func(*action[1:])
        # return True to process other requests as well
        return True

    def push(self, *element, **kwargs):
        """
        Add a new element to the queue.

        Process actions from the same thread as the thread which created
        this queue immediately. What does it mean? When I use liblarch
        without threads, all actions are processed immediately. In GTG,
        this queue is created by the main thread which process GUI. When
        GUI callback is triggered, process those actions immediately because
        no protection is needed. However, requests from synchronization
        services are put in the queue.

        Application can choose which kind of priority should have an update.
        If the request is not in the queue of selected priority, add it and
        setup callback.
        """

        if self._origin_thread == threading.current_thread():
            func = element[0]
            func(*element[1:])
            return

        priority = kwargs.get('priority')
        if priority == 'low':
            queue = self._low_queue
        elif priority == 'high':
            queue = self._vip_queue
        else:
            queue = self._queue

        self._lock.acquire()
        if element not in queue:
            queue.append(element)
            if self._handler is None:
                self._handler = GObject.idle_add(self.process_queue)

        self._lock.release()

    def process(self):
        """
        Return elements to process

        At the moment, it returns just one element. In the future more
        elements may be better to return (to speed it up).

        If there is no request left, disable processing.
        """

        self._lock.acquire()
        if len(self._vip_queue) > 0:
            toreturn = [self._vip_queue.pop(0)]
        elif len(self._queue) > 0:
            toreturn = [self._queue.pop(0)]
        elif len(self._low_queue) > 0:
            toreturn = [self._low_queue.pop(0)]
        else:
            toreturn = []

        if len(self._queue) == 0 and len(self._vip_queue) == 0 and\
                                        len(self._low_queue) == 0 and\
                                        self._handler is not None:
            GObject.source_remove(self._handler)
            self._handler = None
        self._lock.release()
        return toreturn

# -----------------------------------------------------------------------------
