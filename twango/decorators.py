from twisted.internet import threads
import logging

logger = logging.getLogger(__file__)


def call_in_thread_ignore_return(function):
    """
    Decorator: Calls the decorated function in a thread.

    Any errors will be logged using Python's logging module.
    """
    def threaded(*args, **kwargs):
        d = threads.deferToThread(function, *args, **kwargs)
        def error(failure):
            logger.error('%(error_line)s - %(error_type)s: %(error_msg)s' % {
                'error_type': str(failure.type).split("'")[1],
                'error_line': failure.getBriefTraceback().split()[-1],
                'error_msg': failure.getErrorMessage(),
            })
        d.addErrback(error)
        # returning defered so user can do what he wants
        return d
    return threaded


def call_in_thread(success_callback=None, error_callback=None):
    """
    Decorator: Calls the decorated function in a thread.

    The success_callback argument must be a callable which will be called
    with the return value of the original function. For errors, the
    error_callback keyword can be a callable which will be called with a
    twisted.python.failure.Failure instance.

    Any errors will be logged using Python's logging module.
    """
    if success_callback is not None and not callable(success_callback):
        raise ValueError("success_callback must be callable")
    def new(function):
        if success_callback == function:
            raise ValueError("success_callback cannot be the same as "
                "the decorated function")
        def threaded(*args, **kwargs):
            d = threads.deferToThread(function, *args, **kwargs)
            def error(failure):
                logger.error('%(error_line)s - %(error_type)s: %(error_msg)s' % {
                    'error_type': str(failure.type).split("'")[1],
                    'error_line': failure.getBriefTraceback().split()[-1],
                    'error_msg': failure.getErrorMessage(),
                })
                if callable(error_callback):
                    error_callback(failure)

            if success_callback is not None:
                d.addCallback(success_callback)
            d.addErrback(error)
            # returning defered so user can do what he wants
            return d
        return threaded
    return new


