import threading, time, logging, requests

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60
RETRY_MIN = 1.0
RETRY_MAX = 30.0
RETRY_MULT = 1.5
CHUNK_SIZE = 4096

class BroadcastCamera:
    """
    One upstream MJPEG connection shared by all clients.
    Clients always receive the most recent JPEG (no per-client queues).
    Slow clients skip frames instead of blocking others.
    """
    def __init__(self, upstream_url: str):
        self.upstream_url = upstream_url
        self.last_jpeg = None
        self.frame_id = 0
        self.running = False
        self._cond = threading.Condition()
        self._thread = None
        self._session = requests.Session()
        self._clients = 0

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        logging.info(f"[BroadcastCamera] Started {self.upstream_url}")

    def stop(self):
        self.running = False
        with self._cond:
            self._cond.notify_all()
        if self._thread:
            self._thread.join(timeout=5)
        self._session.close()
        logging.info(f"[BroadcastCamera] Stopped {self.upstream_url}")

    def add_client(self):
        with self._cond:
            self._clients += 1
            return self.frame_id

    def remove_client(self):
        with self._cond:
            self._clients = max(0, self._clients - 1)

    def stats(self):
        with self._cond:
            return {
                "url": self.upstream_url,
                "running": self.running,
                "clients": self._clients,
                "frame_id": self.frame_id,
                "has_frame": self.last_jpeg is not None
            }

    def _worker(self):
        retry = RETRY_MIN
        while self.running:
            try:
                resp = self._session.get(
                    self.upstream_url,
                    stream=True,
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    headers={"User-Agent": "BroadcastRelay/1.0"}
                )
                resp.raise_for_status()
                retry = RETRY_MIN
                self._parse(resp)
            except Exception as e:
                logging.error(f"[BroadcastCamera] Upstream error {self.upstream_url}: {e}")
                if not self.running:
                    break
                time.sleep(retry)
                retry = min(retry * RETRY_MULT, RETRY_MAX)

    def _parse(self, resp):
        buf = bytearray()
        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            if not self.running:
                break
            if not chunk:
                continue
            buf.extend(chunk)
            while True:
                start = buf.find(b'\xff\xd8')  # JPEG SOI
                if start == -1:
                    if len(buf) > 2_000_000:
                        buf[:] = buf[-500_000:]
                    break
                end = buf.find(b'\xff\xd9', start + 2)  # JPEG EOI
                if end == -1:
                    if len(buf) > 2_000_000:
                        buf[:] = buf[-500_000:]
                    break
                jpeg = bytes(buf[start:end+2])
                del buf[:end+2]
                self._publish(jpeg)

    def _publish(self, jpeg: bytes):
        with self._cond:
            self.last_jpeg = jpeg
            self.frame_id += 1
            self._cond.notify_all()