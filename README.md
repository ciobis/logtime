# Log Time
A command line tool to help summarize and log task times either to console or to external systems. Tool reads in the data describing when particular task was started and provides an aggregated summary of how much time was spent for each task. 

## Motivation
Time logging is quite tedious and error prone task. It must be performed with a certain degree of accuracy. A system on how to organize and review logs is needed. 

For organizational part logs can be organized in daily buckets and saved somewhere in the disk. Folder structure can be something like:
```
log
└── 2023
    ├── 02
    │   ├── 01.md
    │   ├── ...
    │   └── 28.md
    └── 03
        ├── 01.md
        ├── ...
        └── 31.md
```

Each file would contain a time log for that day. To simplify the process only task start time is registered. For example:
```
| Time  | Task     | Description             |
| ----- | -------- | ----------------------- |
| 08:30 | TASK-1   | migrate to new version  |
| 10:00 | TASK-2   | discussion about future |
| 10:30 | TASK-1   | migrate to new version  |
```

This way it is easy to log time but at the end of the day it is not so straightforward to see how much time was spent per particular task. Additionally there is a big chance that this time needs to be logged to external systems like jira or redmine. And this is where this tool comes into the picture. Scope of the tool is a single file and it performs time summary and automatic logging either to console or to external systems. Check usage examples below.

## Install
* Clone repo
* Add `bin` folder to your path

## Usage example
Create a file named `tasks.md`. Content should be markdown table where each row represents when particular task was started. For example:
```markdown
| Time  | Task     | Description             |
| ----- | -------- | ----------------------- |
| 08:30 | TASK-1   | migrate to new version  |
| 10:00 | TASK-2   | discussion about future |
| 10:30 | TASK-1   | migrate to new version  |
| 10:45 | TASK-2   | meeting about stuff     |
| 11:30 | TASK-3   | performance issues      |
| 12:30 | lunch    |                         |
| 13:30 | TASK-1   | migrate to new version  |
| 18:30 | work-end |                         |
```
### Execute the tool.
* Use `--exclude` flag to hide non relevant tasks. 
* To log to external systems like `jira` or `redmine` use `--log` flag.
```console
$ logtime --file tasks.md
TOTAL WORK: 10.0
------------------------
TASK-1: 6.75 hours:
  - migrate to new version
TASK-2: 1.25 hours:
  - discussion about future
  - meeting about stuff
TASK-3: 1.0 hours:
  - performance issues
lunch: 1.0 hours:
  - 
work-end: 0.0 hours:
  - 

$ logtime --file tasks.md --exclude lunch work-end
TOTAL WORK: 9.0
------------------------
TASK-1: 6.75 hours:
  - migrate to new version
TASK-2: 1.25 hours:
  - discussion about future
  - meeting about stuff
TASK-3: 1.0 hours:
  - performance issues

$ logtime --file tasks.md --exclude lunch work-end --log jira redmine
TOTAL WORK: 9.0
------------------------
TASK-1: 6.75 hours:
  - migrate to new version
TASK-2: 1.25 hours:
  - discussion about future
  - meeting about stuff
TASK-3: 1.0 hours:
  - performance issues
Enter 'yes' if you want to automatically log time 
yes
Logging JIRA 6.75 hours for issue TASK-1
Logging JIRA 1.25 hours for issue TASK-2
Logging JIRA 1.0 hours for issue TASK-3
Logging REDMINE 9.0 hours with description TASK-3: 1.0hours; TASK-2: 1.25hours; TASK-1: 6.75hours; 
```

## Concepts
There are 4 main concepts in the tool:
* **Parser** - Reads the data and converts it to internal data model. Currently only md table is supported.
* **Aggregator** - Groups and aggregates model rows. Useful when there are multiple time logs for the same task but only one summarized record is desired.
* **Logger** - Once the parser collects the data, it is provided for all configured loggers. There are 3 loggers at the moment:
  * **console** - logs data to console. By default it has set config `always_present: true` which allows logger to be executed even though it is not provided to `--log` flag.
  * **jira** - Logs data to jira. Task name is treated as jira issue number.
  * **redmine** - Logs data to redmine. Currently project and activity are preconfigured static values. Log task name is ignored and only description logged.
* **Hooks** - Action on log success or failure. Currently only open url action supported - useful when you want to check the dashboard of time log in external system.

Check `config.yaml` to explore how to configure these entities.

--------------------------

## Development
### Execute tests
```bash
python3 -m unittest tests.test_e2e
```