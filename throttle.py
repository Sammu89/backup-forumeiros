import asyncio

class ThrottleController:
    """
    Controls dynamic back-off and concurrency for HTTP requests.
    Adjusts delay and worker count based on response status codes.
    """
    def __init__(self, config):
        self.base_delay = config.base_delay
        self.min_delay = config.min_delay
        self.max_delay = config.max_delay
        self.max_workers = config.workers

        self.current_delay = self.base_delay
        self.current_workers = config.workers
        self._success_count = 0

    async def before_request(self):
        """
        Await the current delay before making the next HTTP request.
        """
        await asyncio.sleep(self.current_delay)

    def after_response(self, status_code: int):
        """
        Adjust delay and worker count based on the status code.
        - On 429 or 5xx: exponential back-off (delay x2 up to max_delay) and reduce workers by 1 (min 1).
        - On 2xx successes: after 30 consecutive, decrease delay by 0.1s (min_min_delay)
          and increase workers by 1 (up to max_workers).
        """
        # Handle rate limiting and server errors
        if status_code == 429 or (500 <= status_code < 600):
            self.current_delay = min(self.current_delay * 2, self.max_delay)
            self.current_workers = max(self.current_workers - 1, 1)
            self._success_count = 0
        # Handle successful responses
        elif 200 <= status_code < 300:
            self._success_count += 1
            if self._success_count >= 30:
                self.current_delay = max(self.current_delay - 0.1, self.min_delay)
                self.current_workers = min(self.current_workers + 1, self.max_workers)
                self._success_count = 0

    def get_current_delay(self) -> float:
        """
        Return the current inter-request delay.
        """
        return self.current_delay

    def get_current_workers(self) -> int:
        """
        Return the current recommended number of concurrent workers.
        """
        return self.current_workers
