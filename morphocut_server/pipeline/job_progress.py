from rq import get_current_job

from morphocut.pipeline import NodeBase


class JobProgress(NodeBase):
    """Writes the progress into the current Job. The progress is accessible via job.meta.get('progress', 0).

    Note
    ----
    Do not include the `self` parameter in the ``Parameters`` section.

    Parameters
    ----------
    msg : str
        Human readable string describing the exception.
    code : :obj:`int`, optional
        Numeric error code.

    Attributes
    ----------
    msg : str
        Human readable string describing the exception.
    code : int
        Numeric error code.

    """

    def __init__(self):
        self.current = 0

    def __call__(self, input=None):
        job = get_current_job()
        for obj in input:
            if job:
                job.meta['progress'] = self.get_progress(input)
                job.save_meta()
            yield obj

    def get_progress(self, input):
        length = input.__len__()
        if (length > 0):
            progress = (self.current / length) * 100
            self.current += 1
            return progress
        return 0
