import argparse
from modules import *
from typing import List

__version__ = '1.0'

  
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '-submission_dir',
                        help='Path to submision directory', type=str, default='./submission')
    parser.add_argument(
        '-o', '-output_dir', help='Path to output directory', type=str, default='./output')
    parser.add_argument(
        '-r', '-report_path', help='Path to report', type=str, default='./REPORT')
    parser.add_argument(
        '-c', '-command', help='Build command', type=str, default='g++ ./src/*.(c|cpp) -I ./include -o main -Wall -g -std=c++14')
    parser.add_argument('--keep', action='store_true', default=False, help='Keep output files')
    args = parser.parse_args()

    # Copy files to output_dir
    App1 = AutoFilter(args)
    App1()
    
    # Build submissions
    App2 = AutoBuilder(args)
    App2()

    # Generate report
    App3 = AutoReporter(args)
    App3(App1.failed_targets, App2.compiler_output)

    # Grading
    cmd: str = input('[ Info ] Start grading? [y/N]:')
    if cmd == 'y' or cmd == 'Y':
        cmd = input('[ Info ] Save report to? (default: ./GRADES.csv): ')
        path_to_report: str = cmd if len(cmd) > 0 else './GRADES.csv'
        cmd = input('[ Info ] Grading dimensions? (default: Answer Interface):')
        dimension: List[str] = cmd.split(' ') if len(cmd) > 0 else ['Answer', 'Interface']
        App4 = ManualGrader(args.o, path_to_report, dimension)
        App4()