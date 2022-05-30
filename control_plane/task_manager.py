from flymonlib.resource import *
from flymonlib.flymon_task import FlyMonTask
from resource_manager import ResourceManager
from data_collector import DataCollector

class TaskManager:
    def __init__(self, cmug_configs):
        self.active_tasks={
            # tasi_id : (task_instance, [resource_list], data_querier)
        }
        self.idle_tasks={
            # tasi_id : (task_instance, [resource_list], data_querier)
        }
        self.TASK_INC = 0

    def register_task(self, key, attribute, mem_size):
        """
        Input Example:
         - flow_key: hdr.ipv4.src_addr/24, hdr.ipv4.dst_addr/32
         - flow_attr: frequency(1)
         - memory_size: 65536
        Return:
         - A task object with resource lists and data querier.
        Exceptrion:
         - may rase some exception.
        """
        task_id = self.TASK_INC + 1
        self.TASK_INC += 1
        task_instance = FlyMonTask(task_id, key, attribute, mem_size)
        self.idle_tasks[task_id] = task_instance
        return task_instance

    def query_task(self, task_id, query_key):
        return 0

    def temp_data(self):
        return 
