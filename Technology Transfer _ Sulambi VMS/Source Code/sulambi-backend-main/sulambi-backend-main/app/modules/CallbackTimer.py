from datetime import datetime
import threading
import time

def executeDelayedAction(targetEpochInSecs: int, callback, execAnyway=False):
  currentEpoch = int(datetime.now().timestamp()) * 1000
  timeDelay = (targetEpochInSecs - currentEpoch) / 1000

  if (timeDelay < 0 and (not execAnyway)):
    return

  # exec with no time-delay
  if (execAnyway):
    th = threading.Thread(target=callback)
    th.daemon = True
    th.start()

  # callback template to be executed
  def threadableCallback():
    time.sleep(timeDelay)
    callback()

  th = threading.Thread(target=threadableCallback)
  th.daemon = True
  th.start()