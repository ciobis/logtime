from abc import ABC, abstractmethod
from functools import reduce
from typing import List
import requests
import json
from .model import *


available_loggers = {
    'console': lambda cnf: ConsoleLogger(cnf),
    'jira': lambda cnf: JiraLogger(cnf),
    'redmine': lambda cnf: RedmineLogger(cnf)
}

def load_loggers(config, required_loggers):
    result = []

    for logger in config["loggers"]:
        if logger['name'] in required_loggers or logger['always_present']:
            result.append(available_loggers[logger['type']](logger))

    result.sort(key=lambda l: l.priority)

    return result


class LogStatus:
    def __init__(self, success: bool, error: str):
        self.success = success
        self.error = error

class LogSuccess(LogStatus):
    def __init__(self):
        LogStatus.__init__(self, True, '')

class LogFailure(LogStatus):
    def __init__(self, error: str):
        LogStatus.__init__(self, False, error)



class Logger(ABC):

    def __init__(self, config):
        self.name = config['name']
        self.confirm_prompt = config['confirm_prompt']
        self.priority = config['priority']
        self.options = config['options']

    def log(self, log_records: List[TimeLog]) -> LogStatus:
        status = LogSuccess()
        for log in log_records:
            status = self.log_record(log)
            if not status.success:
                return status
            
        return status

    @abstractmethod
    def log_record(self, log: TimeLog) -> LogStatus:
        pass



class ConsoleLogger(Logger):
    def __init__(self, config):
        Logger.__init__(self, config)

    def log_record(self, log: TimeLog):
        print(f'{log.task}: {log.duration_hours()} hours')
        print(log.description)
        return LogSuccess()

class JiraLogger(Logger):
    def __init__(self, config):
        Logger.__init__(self, config)

    def log_record(self, log: TimeLog):
        print(f'Logging JIRA {log.duration_hours()} hours for issue {log.task}')

        response = self.__jira_api_log_time(log.task, log.duration_hours(), log.description, log.time)
        if response.status_code != 201:
            return LogFailure(f'Log failed with status {response.status_code}\r\n{response.text}')
            
        return LogSuccess()

    def __jira_api_log_time(self, issue_key, time_in_hours, comment, started_on):
        # https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-worklogs/#api-rest-api-2-issue-issueidorkey-worklog-post
        time_in_seconds = time_in_hours * 60 * 60

        api_url = f"{self.options['url']}/rest/api/2/issue/{issue_key}/worklog"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.options['access_token']}"
        }

        payload = {
            "timeSpentSeconds": time_in_seconds,
            "comment": comment,
            "started": started_on.strftime('%Y-%m-%dT%H:%M:%S.000+0000')
        }

        return requests.post(api_url, data=json.dumps(payload), headers=headers)


class RedmineLogger(Logger):
    def __init__(self, config):
        Logger.__init__(self, config)

    def log_record(self, log: TimeLog):
        print(f'Logging REDMINE {log.duration_hours()} hours with description {log.description}')
        
        response = self.__redmine_api_log_time(log.duration_hours(), log.description, log.time)
        if response.status_code != 201:
            return LogFailure(f'Log failed with status {response.status_code}\r\n{response.text}')
        
        return LogSuccess()

    def __redmine_api_log_time(self, time_in_hours, comment, started_on):
        # https://www.redmine.org/projects/redmine/wiki/Rest_TimeEntries

        api_url = f"{self.options['url']}/time_entries.json"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Redmine-API-Key": self.options['access_key']
        }

        payload = {
            "time_entry": {
                "project_id": self.options['project_id'],
                "hours": time_in_hours,
                "activity_id": self.options['activity_id'],
                "comments": comment,
                "spent_on": started_on.strftime('%Y-%m-%d')
            }
        }

        return requests.post(api_url, data=json.dumps(payload), headers=headers)