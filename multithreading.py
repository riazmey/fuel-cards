
import multiprocessing
import math

from typing import Callable, Tuple
from threading import Thread


class MultithreadedDataProcessing():

    def __init__(self, ws, handler: Callable, data: list | tuple, threads: int = None):
        if threads:
            number_threads = threads
        else:
            number_threads = self._quantify_threads()
        self.ws = ws
        self.processed_data = []
        self.processed_success = True
        self.threads = self._initialize_threads(handler, data, number_threads)

    def processing(self) -> Tuple[list, bool]:
        result = []
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        for data in self.processed_data:
            result.append(data)
        return result, self.processed_success

    def _quantify_threads(self):
        result = multiprocessing.cpu_count()
        match result:
            case 0:
                result = 1
            case 2:
                result = 2
            case 3:
                result = 2
            case 4:
                result = 3
        return result
    
    def _initialize_threads(self, handler: Callable, data: list | tuple, num_threads: int) -> list[Thread]:
        result = []
        
        num_items = len(data)
        if num_threads > 1:
            if num_items >= num_threads:
                if (num_items // num_threads) == (num_items / num_threads):
                    items_per_thread = num_items / num_threads
                else:
                    items_per_thread = math.ceil(num_items / num_threads)
            else:
                items_per_thread = 1
        else:
            items_per_thread = num_items

        data_thread = None
        for i in range(1, num_items + 1):
            if not data_thread:
                data_thread = []
            data_thread.append(data[i - 1])
            if (i // items_per_thread) == (i / items_per_thread) or i == num_items + 1:
                result.append(Thread(
                    target=handler,
                    args=(self.ws, data_thread, self.processed_data, self.processed_success)))
                data_thread = None
        
        if data_thread:
            result.append(Thread(
                target=handler,
                args=(self.ws, data_thread, self.processed_data, self.processed_success)))
        
        return result
