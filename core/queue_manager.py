from collections import deque
from config import QUEUE_MAX_SIZE

queue = deque()

def enqueue(item):
    if len(queue) >= QUEUE_MAX_SIZE:
        return False
    queue.append(item)
    return True

def dequeue():
    if queue:
        return queue.popleft()
    return None
