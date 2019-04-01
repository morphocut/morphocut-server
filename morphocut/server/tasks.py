from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

from morphocut.processing.pipeline import *
from morphocut.server import models, helpers, morphocut
from morphocut.server.extensions import database, migrate, redis_store, redis_queue
from morphocut.server.models import Task
from morphocut.server import morphocut


def launch_task(name, description, *args, **kwargs):
    '''
    Launches a task with the given function and args. Then launches a task which starts when the first one is finished, writing its results to the database.
    '''
    task, rq_job = current_user.launch_task(name, description, *args, **kwargs)
    database.session.commit()

    # Need to look into this more. This should enqueue a job to write back the result right after the processing job is finished 
    # but if some other job is enqueued before that, it is started before this writeback job even when this is enqueued at the front
    write_result_job = redis_queue.enqueue('morphocut.server.tasks.write_result',
                                           task.id, depends_on=rq_job, at_front=True)

    return task


def write_result(task_id):
    with morphocut.app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        rq_job = task.get_rq_job()
        if rq_job.get_status() == 'finished':
            task.complete = True
            task.result = rq_job.result
            database.session.commit()
