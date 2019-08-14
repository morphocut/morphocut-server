from abc import abstractmethod

from morphocut.pipeline import NodeBase


class LogBase(NodeBase):

    def __init__(self):
        self.log_data = {}

    def __call__(self, input=None):
        for obj in input:
            self.log()
            yield obj

    def get_log(self):
        '''
        Get the log data
        '''
        return self.log_data

    @abstractmethod
    def log(self):
        """
        Process the facet and return a new one.
        """
        pass


class ObjectCountLog(LogBase):
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

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.log_data[self.name] = 0

    def log(self):
        self.log_data[self.name] += 1


class ParamsLog(LogBase):
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

    def __init__(self, name, params):
        super().__init__()
        self.name = name
        self.log_data[self.name] = params

    def log(self):
        pass
