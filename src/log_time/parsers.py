from abc import ABC, abstractmethod
from .model import *
from datetime import datetime
from typing import List

available_parsers = {
    'md_table': lambda cnf: MdTableParser(cnf['format'], cnf.get('date_override', None)),
}

def load_parser(config, parser_name):
    parser_options = config['parsers'][parser_name]['options']
    return available_parsers[parser_name](parser_options)

class Parser(ABC):
    @abstractmethod
    def parse(self, input: str) -> List[TimeLog]:
        pass

class MdTableParser(Parser):
    def __init__(self, format, date_override):
        self.format = format
        self.date_override = date_override

    def parse(self, input: str) -> List[TimeLog]:
        with open(input, 'r') as f:
            lines = f.readlines()

        result = []
        table_data_started = False
        header_date = None
        for line in lines:
            if not table_data_started:
                if line.startswith('# '):
                    header_date = line[2:].strip()
                table_data_started = line.startswith('| --')
                continue

            parts = [p.strip() for p in line.split('|')[1:-1]]
            start_time = self.__str_to_time(parts[0], header_date)
            task_name = parts[1]
            task_description = parts[2]


            time_log = TimeLog(start_time, task_name, task_description, 0)
            if result:
                last_log = result[-1]
                last_log.duration = (time_log.time - last_log.time).total_seconds()

            result.append(time_log)

        return result
    
    def __str_to_time(self, s, header_date):
        time = datetime.strptime(s, self.format)
        if self.date_override == None:
            return time

        if self.date_override == 'today':
            date_override = datetime.today()
        elif self.date_override == 'header' and header_date:
            date_override = datetime.strptime(header_date, '%Y-%m-%d')
        else:
            date_override = datetime.strptime(self.date_override, '%Y-%m-%d')

        return datetime.combine(date_override, time.time())