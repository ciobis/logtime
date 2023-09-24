import unittest
from unittest.mock import patch
import os
import io
import sys
import json
from log_time.log_time import log_time

class E2E(unittest.TestCase):

    def test_log_console_works(self):
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tasks.md')
        config_file  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-config.yaml')
        config_override = []
        parser = 'md_table'
        log = ['console']
        exclude_tasks = ['lunch', 'work-end']

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput

        log_time(file_name, config_file, config_override, parser, log, exclude_tasks)
        sys.stdout = sys.__stdout__

        expected = """TOTAL WORK: 9.0
------------------------
TASK-1: 7.25 hours:
  - [migration] migrate to new version
  - [talks] migration strategy discussion

TASK-2: 0.75 hours:
  - discussion about future
  - meeting about stuff

TASK-3: 1.0 hours:
  - performance issues

"""
        self.assertEqual(expected, capturedOutput.getvalue())



        

    @patch('log_time.loggers.requests.post')
    def test_log_jira_works(self, mock_post):
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tasks.md')
        config_file  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-config.yaml')
        config_override = []
        parser = 'md_table'
        log = ['jira']
        exclude_tasks = ['lunch', 'work-end']

        mock_post.return_value.status_code = 201

        log_time(file_name, config_file, config_override, parser, log, exclude_tasks)

        # print(mock_post.mock_calls)

        mock_post.assert_any_call(
            'https://jira.domain.com/rest/api/2/issue/TASK-1/worklog',
            data = json.dumps({
                "timeSpentSeconds": 24300.0,
                "comment": '  - [migration] migrate to new version\n',
                "started": '2023-04-01T08:30:00.000+0000'
            }),
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": 'Bearer test-jira-access-token'
            }
        )

        mock_post.assert_any_call(
            'https://jira.domain.com/rest/api/2/issue/TASK-1/worklog',
            data = json.dumps({
                "timeSpentSeconds": 1800.0,
                "comment": '  - [talks] migration strategy discussion\n',
                "started": '2023-04-01T11:00:00.000+0000'
            }),
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": 'Bearer test-jira-access-token'
            }
        )

        mock_post.assert_any_call(
            'https://jira.domain.com/rest/api/2/issue/TASK-2/worklog',
            data = json.dumps({
                "timeSpentSeconds": 2700.0,
                "comment": '  - discussion about future\n  - meeting about stuff\n',
                "started": '2023-04-01T10:00:00.000+0000'
            }),
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": 'Bearer test-jira-access-token'
            }
        )

        mock_post.assert_any_call(
            'https://jira.domain.com/rest/api/2/issue/TASK-3/worklog',
            data = json.dumps({
                "timeSpentSeconds": 3600.0,
                "comment": '  - performance issues\n',
                "started": '2023-04-01T11:30:00.000+0000'
            }),
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": 'Bearer test-jira-access-token'
            }
        )

    @patch('log_time.loggers.requests.post')
    @patch('log_time.hooks.subprocess.run')
    def test_log_redime_works(self, mock_run, mock_post):
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tasks.md')
        config_file  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-config.yaml')
        config_override = []
        parser = 'md_table'
        log = ['redmine']
        exclude_tasks = ['lunch', 'work-end']

        mock_post.return_value.status_code = 201
        mock_run.return_value = 1

        log_time(file_name, config_file, config_override, parser, log, exclude_tasks)

        # print(mock_post.mock_calls)

        mock_post.assert_called_with(
            'https://redmine.domain.com/time_entries.json',
            data = json.dumps({
                "time_entry": {
                    "project_id": 0,
                    "hours": 9.0,
                    "activity_id": 1,
                    "comments": 'TASK-1: 7.25hours; TASK-2: 0.75hours; TASK-3: 1.0hours; ',
                    "spent_on": '2023-04-01'
                }
            }),
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Redmine-API-Key": 'test-redmine-access-key'
            }
        )

        mock_run.assert_called_once_with(['firefox', 'http://link.to.open.on.success'])

    @patch('log_time.loggers.requests.post')
    @patch('log_time.hooks.subprocess.run')
    def test_failure_hook_works(self, mock_run, mock_post):
        file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tasks.md')
        config_file  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-config.yaml')
        config_override = []
        parser = 'md_table'
        log = ['redmine']
        exclude_tasks = ['lunch', 'work-end']

        mock_post.return_value.status_code = 400
        mock_run.return_value = 1

        log_time(file_name, config_file, config_override, parser, log, exclude_tasks)

        mock_run.assert_called_once_with(['firefox', 'http://link.to.open.on.failure'])


