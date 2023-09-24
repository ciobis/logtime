from .config_loader import *
from .parsers import load_parser
from .loggers import load_loggers
from .hooks import load_hooks, HookType
from .aggregators import load_aggregators


def log_time(file, config_file, config_override, parser, log, exclude):
    config_loader = ConfigLoader(config_file, config_override)
    config = config_loader.load_config()

    parser = load_parser(config, parser)
    task_times = parser.parse(file)
    task_times = list(filter(lambda t: not t.task in exclude, task_times))

    loggers = load_loggers(config, log)
    aggregators = load_aggregators(config)
    hooks = load_hooks(config)

    prompt_confirmed = False
    for logger in loggers:
        if logger.confirm_prompt and not prompt_confirmed:
            prompt_confirmed = 'yes' == input("Enter 'yes' if you want to automatically log time \r\n")
            if not prompt_confirmed:
                return

        aggregated_times = aggregators[logger.name].aggregate(task_times)

        status = logger.log(aggregated_times)
        
        if status.success:
            hooks[logger.name][HookType.ON_SUCCESS].execute()
        else:
            hooks[logger.name][HookType.ON_FAILURE].execute()
            
            print(status.error)
            return