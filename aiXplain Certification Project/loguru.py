"""
Lightweight compatibility shim for `from loguru import logger`.

If the real `loguru` package is installed in the environment, prefer it.
Otherwise this module provides a minimal `logger` with the methods used
by the project (`info`, `debug`, `warning`, `error`, `success`, `exception`).
"""
try:
    # If the real loguru is available, re-export its logger
    from loguru import logger  # type: ignore
except Exception:
    import logging

    class _SimpleLogger:
        def __init__(self):
            self._logger = logging.getLogger("policy_navigator")
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                fmt = logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
                )
                handler.setFormatter(fmt)
                self._logger.addHandler(handler)
                self._logger.setLevel(logging.INFO)

        def info(self, msg, *args, **kwargs):
            self._logger.info(msg, *args, **kwargs)

        def debug(self, msg, *args, **kwargs):
            self._logger.debug(msg, *args, **kwargs)

        def warning(self, msg, *args, **kwargs):
            self._logger.warning(msg, *args, **kwargs)

        def error(self, msg, *args, **kwargs):
            self._logger.error(msg, *args, **kwargs)

        def exception(self, msg, *args, **kwargs):
            self._logger.exception(msg, *args, **kwargs)

        def success(self, msg, *args, **kwargs):
            # `success` doesn't exist in stdlib logger; map to info
            self._logger.info(msg, *args, **kwargs)

        def remove(self, handler_id=None):
            """Remove handlers. If handler_id is None, remove all handlers."""
            if handler_id is None:
                for h in list(self._logger.handlers):
                    try:
                        self._logger.removeHandler(h)
                    except Exception:
                        pass
            else:
                # Not tracking numeric ids; ignore gracefully
                return

        def add(self, sink, level="INFO", format=None, **kwargs):
            """Add a handler. `sink` can be a stream (like sys.stderr) or a
            filename. Accepts extra kwargs (`rotation`, `retention`, etc.) used
            by real loguru; these are ignored by this shim. Returns a dummy
            handler id (None).
            """
            try:
                if hasattr(sink, 'write'):
                    handler = logging.StreamHandler(sink)
                else:
                    handler = logging.FileHandler(str(sink))

                # If a format is provided, try to map loguru style to standard
                # python format or use it directly.
                if format:
                    try:
                        handler.setFormatter(logging.Formatter(format))
                    except Exception:
                        # ignore formatting issues
                        pass

                # Map level strings to logging levels
                lvl = getattr(logging, str(level).upper(), logging.INFO)
                handler.setLevel(lvl)
                self._logger.addHandler(handler)
                # loguru returns a handler id; shim returns None
                return None
            except Exception:
                return None

    logger = _SimpleLogger()
