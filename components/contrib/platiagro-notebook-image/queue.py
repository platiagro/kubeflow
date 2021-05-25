import asyncio
import papermill
import logging


WORKERS_QTY = 3



# some helpers functions
def create_workers(workers_qty, worker_callable):
    tasks = []
    for i in range(workers_qty):
        task = asyncio.create_task(worker_callable(queue)) 
        tasks.append(task)   
    return tasks

async def cancel_tasks(task_list):
    # Cancel our worker tasks.
    for task in task_list:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*task_list, return_exceptions=True)

async def insert_queue_element(element, queue):
    await queue.put_nowait(element)


# making a work that will execute the papermill 
async def worker(queue):
    while True:
        context = await queue.get()
        try:
            papermill.execute_notebook(
                context['notebook_path'],
                context['output_path'],
                context['parameters'],
             )
        except papermill.exceptions.PapermillExecutionError:
            logging.exception("Monitoring Task Error")
        pass

        queue.task_done()

# handling the queue
async def execute_papermill_as_queue(context):
    queue = asyncio.Queue()
    insert_queue_element(context, queue)


    tasks = create_workers(WORKERS_QTY, create_workers)

    # Wait until the queue is fully processed.
    await queue.join()

    # cancelling tasks
    cancel_tasks(tasks)

  

