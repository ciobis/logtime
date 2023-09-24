from abc import ABC, abstractmethod
from typing import List
from itertools import groupby
from functools import reduce
import re
from .model import TimeLog

def load_aggregators(config):
    result = {}
    for logger in config["loggers"]:
        aggregators = []

        if not 'aggregate' in logger:
                result[logger['name']] = IterativeAggregator(aggregators)
                continue
        
        for aggregate in logger['aggregate']:
            group_by = aggregate.get('group', [])
            transform = aggregate.get('transform', [])

            transform_by_field = {}
            for tr in transform:
                transform_by_field[tr['field']] = tr

            aggregators.append(BasicAggregator(group_by, transform_by_field))

        result[logger['name']] = IterativeAggregator(aggregators)

    return result


class Aggregator(ABC):
    @abstractmethod
    def aggregate(logs: List[TimeLog]) -> List[TimeLog]:
        pass

class BasicAggregator(Aggregator):
    def __init__(self, group_by, transform):
        self.group_by = group_by
        self.transform = transform

    def aggregate(self, logs: List[TimeLog]) -> List[TimeLog]:
        sorted_logs = sorted(logs, key=self.__agg_key)
        groups = [list(result) for key, result in groupby(sorted_logs, key=self.__agg_key)]

        result = []
        for group in groups:
            descriptions = self.__extract_field_values(group, self.transform.get('description', {}), lambda log: log.description)
            descriptions.sort()
            tasks = self.__extract_field_values(group, self.transform.get('task', {}), lambda log: log.task)
            tasks.sort()

            result.append(TimeLog(
                reduce(lambda min_time, log: min_time if min_time < log.time else log.time, group, group[0].time),
                reduce(lambda x, task: x + task , tasks, ''),
                reduce(lambda x, desc: x + desc , descriptions, ''),
                reduce(lambda x, log: x + log.duration, group, 0)
            ))

        return result

    def __agg_key(self, log: TimeLog) -> str:
        values = []
        for group in self.group_by:
            col_name = group['field']
            col_function = group.get('function', 'value')
            col_function_params = group.get('args', [])

            if not hasattr(log, col_name):
                continue
            
            col_value = getattr(log, col_name)
            transformed_col_value = self.__apply_col_function(col_value, col_function, col_function_params)
            values.append(transformed_col_value)

        return str(values)


    def __apply_col_function(self, value, function_name, function_args):
        if function_name == 'value':
            return value
        
        if function_name == 'regex':
            regex = function_args[0]
            match = re.search(regex, value)
            if match:
                return match.group(0)
            
            return ''

        
    def __extract_field_values(self, logs: List[TimeLog], transform_options, resolve_field):
        fields = []
        if 'template' in transform_options:
            fields = reduce(lambda x, log: x + [transform_options['template'].format(**{'task': log.task, 'description': log.description, 'duration': log.duration, 'duration_hours': log.duration_hours()})] , logs, [])
        else:
            fields = reduce(lambda x, log: x + [resolve_field(log)] , logs, [])

        if transform_options.get('unique', True):
            fields = list(set(fields))


        return fields
    
class IterativeAggregator(Aggregator):
    def __init__(self, aggregators: List[Aggregator]):
        self.aggregators = aggregators

    def aggregate(self, logs: List[TimeLog]) -> List[TimeLog]:
        aggregated_logs = logs
        for aggregator in self.aggregators:
            aggregated_logs = aggregator.aggregate(aggregated_logs)

        return aggregated_logs