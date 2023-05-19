import threading
import asyncio
import inspect
import logging
import traceback

def print_current_thread():
    """
    Print the name of the current thread.
    """
    thread_name = threading.current_thread().name
    print(f"\033[32mCurrent thread is {thread_name}\033[0m")

class ThreadManager:
    """
    Class for managing threads and event loops.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize the ThreadManager object.

        Args:
            logger (logging.Logger): Logger object for logging messages.
        """
        self.threads = {}  # Dictionary to store the threads
        self.logger = logger

    def add_thread(self, func, args: tuple = None, name: str = None):
        """
        Add a thread to the manager.

        Args:
            func (function): The function to run in the thread.
            args (tuple): The arguments to pass to the function
            name (str, optional): Name of the thread. If not provided, a unique name will be generated.

        Returns:
            None
        """
        if name is None:
            i = 0
            while f'Thread{i}' in self.threads:
                i += 1
            name = f'Thread{i}'
        else:
            if name in self.threads:
                self.logger.warning(f'\033[31mThread "{name}" already exists!\033[0m')
                return

        try:
            self.threads[name] = threading.Thread(target=func, args=args)
            self.logger.info(f'\033[m34[Thread:{name} added!\033[0m')
        except Exception as e:
            self.logger.error(f'\033[31mRed{e} \n{traceback.format_exc()}\033[0m')

    def add_event_loop(self):
        """
        Add an event loop as a thread.

        Returns:
            asyncio.AbstractEventLoop: The created event loop.
        """
        loop = asyncio.new_event_loop()
        name = 'loop0'
        i = 0
        while f'loop{i}' in self.threads:
            i += 1
        name = f'loop{i}'
        self.threads[name] = threading.Thread(target=loop.run_forever, name=name)

        return loop

    def remove_thread(self, func_name: str):
        """
        Remove a thread from the manager.

        Args:
            func_name (str): Name of the thread to remove.

        Returns:
            None
        """
        if func_name not in self.threads:
            self.logger.warning(f'\033[31mThread "{func_name}" does not exist!\033[0m')
            return
        try:
            del self.threads[func_name]
            self.logger.info(f'\033[m34Thread for {func_name} deleted!')
        except Exception as e:
            self.logger.error(f'\033[31mRed{e} \n{traceback.format_exc()}\033[0m')

    def start_threads(self):
        """
        Start all the threads managed by the ThreadManager.

        Returns:
            None
        """
        try:
            for name, thread in self.threads.items():
                if thread.is_alive():
                    self.logger.warning(f'\033[31mThread "{name}" is already running!\033[0m')
                    continue
                else:
                    thread.start()
                    self.logger.info(f'\033[m34Thread "{name}" started!\033[0m')
        except Exception as e:
            self.logger.error(f'\033[31mRed{e} \n{traceback.format_exc()}\033[0m')

    def join_threads(self):
        """
        Wait for all the threads to finish.

        Returns:
            None
        """
        for name, thread in self.threads.items():
            if thread.is_alive():
                self.logger.info(f'\033[34mWaiting for thread "{name}" to finish...\033[0m')
                thread.join()

    def get_thread_with_func_name(self, func_name: str) -> threading.Thread:
        """
        Get a thread object based on its function name.

        Args:
            func_name (str): Name of the function associated with the thread.

        Returns:
            threading.Thread: The thread object.
        """
        if func_name not in self.threads:
            self.logger.warning(f'\033[31mThread "{func_name}" does not exist!\033[0m')
            return
        try:
            return self.threads[func_name]
        except Exception as e:
            self.logger.error(f'\033[31mRed{e} \n{traceback.format_exc()}\033[0m')

    def get_alive_threads(self):
        """
        Generator to yield all the alive threads.

        Yields:
            threading.Thread: The alive thread.
        """
        for thread in self.threads.values():
            if thread.is_alive():
                yield thread

    def get_dead_threads(self):
        """
        Generator to yield all the dead threads.

        Yields:
            threading.Thread: The dead thread.
        """
        for thread in self.threads.values():
            if not thread.is_alive():
                yield thread
