"""
This file contains functions to make papermill execution work as queue.
"""
import asyncio
import logging

import papermill


async def insert_queue_element(queue_dict_element, queue):
    """
    insert element in a queue

    Parameters
    -----------
    element: dict
             dictionary containing function arguments
    queue:
           asyncio.queue object
    """

    logging.info("Inserting in the queue")
    queue.put_nowait(queue_dict_element)


# making a work that will execute the papermill
async def worker(queue):
    """
    worker for consume queue element for papermill execution

    Parameters
    -----------
    queue
           asyncio.queue object
    """
    logging.info("Executing notebook")
    while True:
        context = await queue.get()
        try:
            papermill.execute_notebook(
                context['notebook_path'],
                context['output_path'],
                context['parameters'])
        except papermill.exceptions.PapermillExecutionError:
            logging.exception("Monitoring Task Error")
            pass

        queue.task_done()


# handling the queue
async def execute_papermill_as_queue(context):
    """
    function to handle queue logic

    Parameters
    -----------
    context: dict
             context containing function arguments
    """
    queue = asyncio.Queue()

    await insert_queue_element(context, queue)
    task = asyncio.create_task(worker(queue))

    # Wait until the queue is fully processed.
    await queue.join()

    task.cancel()
