from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
import datetime
import importlib
from rq import get_current_job

from morphocut.processing.pipeline import *
from morphocut.server import models, helpers
# from morphocut.server import create_app
from morphocut.server.extensions import database, migrate, redis_store, redis_queue
from morphocut.server.models import Task
# from flask import current_app


def launch_task(name, description, *args, **kwargs):
    '''
    Launches a task with the given function and args. Then launches a task which starts when the first one is finished, writing its results to the database.

    deprecated:: 14.04.2019
          `tasks.launch_task` will be removed soon, it is replaced by User.launch_task
          `tasks.write_result` will be removed soon, it is replaced by User.launch_task
    '''
    execute_and_save(name, description, 0, 0, *args, **kwargs)

    task, rq_job = current_user.launch_task(name, description, *args, **kwargs)
    database.session.commit()

    rq_job.meta['enqueued_at'] = datetime.datetime.now()

    # Need to look into this more. This should enqueue a job to write back the result right after the processing job is finished
    # but if some other job is enqueued before that, it is started before this writeback job even when this is enqueued at the front
    write_result_job = redis_queue.enqueue('morphocut.server.tasks.write_result',
                                           task.id, depends_on=rq_job, at_front=True)

    return task


def write_result(task_id):
    '''
    Writes the result of the task with the given id to the database.

    deprecated:: 14.04.2019
          `tasks.launch_task` will be removed soon, it is replaced by User.launch_task
          `tasks.write_result` will be removed soon, it is replaced by User.launch_task
    '''
    from morphocut.server import morphocut
    with morphocut.app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        rq_job = task.get_rq_job()
        if rq_job.get_status() == 'finished':
            task.complete = True
            task.result = rq_job.result
            database.session.commit()


def execute_task_and_save_result(name, *args, **kwargs):
    """Executes the function with the given name and the given *args and **kwargs and writes the result to the database afterwards.

    Parameters
    ----------
    name : str
        The full name of the function, including the modules.
    *args
        Variable length argument list. Will be passed to the function.
    *kwargs
        Arbitrary keyword arguments. Will be passed to the function.

    Returns
    -------
    None

    """
    from morphocut.server import morphocut
    with morphocut.app.app_context():
        job = get_current_job()
        if job:
            func_name = name.split('.')[-1]
            module_name = name[:-(len(func_name) + 1)]

            # Get the module which is needed to load the function
            module = importlib.import_module(module_name)

            started_at = datetime.datetime.now()

            # execute the function
            result = getattr(module, func_name)(*args, **kwargs)

            finished_at = datetime.datetime.now()

            task = Task.query.filter_by(id=job.get_id()).first()
            task.complete = True
            task.result = result
            database.session.commit()
