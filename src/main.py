import argparse
import os
from log_time.log_time import log_time
from log_time.loggers import available_loggers
from log_time.parsers import available_parsers

parser = argparse.ArgumentParser(description='Time table processor and logger')
parser.add_argument('--file', help='File with time data', type=str, required=True)
parser.add_argument('--config_file', help='Path to config file', type=str, required=True)
parser.add_argument('--config_override', help='Config overrides. For example: parsers.md_table.options.date_override=2023-01-01', type=str, nargs='*', default=[])
parser.add_argument('--parser', help=f'Data parser', choices=list(available_parsers.keys()), type=str, default=list(available_parsers.keys())[0])
parser.add_argument('--log', help=f'Names of configured loggers to use', type=str, nargs='*', default=[])
parser.add_argument('--exclude', help='List of tasks to exclude from logging', type=str, nargs='*', default=[])

args = parser.parse_args()
log_time(args.file, args.config_file, args.config_override, args.parser, args.log, args.exclude)