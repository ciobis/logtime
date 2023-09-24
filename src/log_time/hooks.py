from abc import ABC, abstractmethod
from enum import Enum
from typing import List
import subprocess

available_hooks = {
    'open_link': lambda options: OpenBrowser(options['browser'], options['url']),
}

def load_hooks(config):
    result = {}
    for logger in config["loggers"]:
        result[logger['name']] = {
            HookType.ON_SUCCESS: HooksExecutor([]),
            HookType.ON_FAILURE: HooksExecutor([])
        }

        if not 'hooks' in logger:
                continue

        for hook_type, hooks in logger['hooks'].items():
            for hook in hooks:
                type = getattr(HookType, hook_type.upper())
                result[logger['name']][type].add_hook(available_hooks[hook['action']](hook['options']))
    
    return result

class HookType(Enum):
    ON_SUCCESS = 1
    ON_FAILURE = 2


class Hook(ABC):
    @abstractmethod
    def execute(self):
        pass

class OpenBrowser(Hook):
    def __init__(self, browser, url):
        self.browser = browser
        self.url = url

    def execute(self):
        subprocess.run([self.browser, self.url])

class HooksExecutor(Hook):
    def __init__(self, hooks: List[Hook]):
        self.hooks = hooks

    def execute(self):
        for hook in self.hooks:
            hook.execute()
    
    def add_hook(self, hook):
        self.hooks.append(hook)
