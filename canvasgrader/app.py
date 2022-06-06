import argparse
from .components import *
from typing import List

__version__ = '1.0'


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--submission_dir', help='Path to submision directory', type=str, default='./submissions')
    parser.add_argument('-o', '--output_dir', help='Path to output directory', type=str, default='./output')
    parser.add_argument('--report_name', help='Path to report, will generate <REPORT>.csv|md', type=str, default='REPORT')
    parser.add_argument('-c',
                        '--command',
                        help='Build command',
                        type=str,
                        default='g++ ./src/*.(c|cpp) -I ./include -o main -Wall -g -std=c++14')
    parser.add_argument('--keep_output', action='store_true', default=False, help='Keep output files, do not extract')
    parser.add_argument('--keep_file_structure', action='store_true', default=False, help='Keep structure of source files')
    parser.add_argument('-a',
                        '--apps',
                        type=str,
                        default='filter,builder,reporter,grader',
                        help='Apps to start, defualt to all(filter,builder,reporter,grader)')
    args = parser.parse_args()

    apps: List[str] = args.apps.split(',')
    # Copy files to output_dir
    if 'filter' in apps:
        App1 = AutoFilter(args)
        App1()

    # Build submissions
    if 'builder' in apps:
        App2 = AutoBuilder(args)
        App2()

    # Generate report
    if 'reporter' in apps:
        App3 = AutoReporter(args)
        App3(App1.failed_targets, App2.compiler_output)

    if 'grader' in apps:
        # Grading
        cmd: str = input('[ Info ] Start grading? [y/N]:')
        if cmd == 'y' or cmd == 'Y':
            cmd = input('[ Info ] Save report to? (default: ./GRADES.csv): ')
            path_to_report: str = cmd if len(cmd) > 0 else './GRADES.csv'
            cmd = input('[ Info ] Grading dimensions? (default: Answer Interface):')
            dimension: List[str] = cmd.split(' ') if len(cmd) > 0 else ['Answer', 'Interface']
            App4 = ManualGrader(args.output_dir, path_to_report, dimension)
            App4()


if __name__ == '__main__':
    main()