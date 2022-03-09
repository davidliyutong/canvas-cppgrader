import subprocess
import os
from typing import List, Dict
import sys
import time
import replit

class ManualGrader:
    __doc__ = "Use '<' or ',' for previous submission\n" \
              "    '>' or '.' for next submission\n" \
              "'grade \{score1\} \{score2\}' or 'g \{score1\} \{score2\}' to grade\n" \
              "Type the name of executable to execute\n" \
              "'ls' and 'cd' commands are available\n" \
              "'save' to save and 'quit' to quit\n" \
              "\nMethods:\n\n\trun()"
    path_to_output: str = ''

    def __init__(self, path_to_output: str = './output', path_to_report: str = './GRADES.csv', dimension: List[str] = ['Answer', 'Interface']):
        self.path_to_output: str = path_to_output
        self.path_to_grade_report: str = path_to_report
        self.dimension: List[str] = dimension
        self.grades: Dict[str, List[float]] = dict()
        self._restor_grades()

    def _restor_grades(self):
        """Restore the grades from self.path_to_grade_report
        """
        if os.path.exists(self.path_to_grade_report):
            with open(self.path_to_grade_report, 'r') as f:
                for line in f.readlines()[1:]: # Discard the first line
                    line_tokenized = line.split(',')
                    self.grades[line_tokenized[0]] = [float(score) for score in line_tokenized[1:]]

    @property
    def _output_path_exist(self) -> bool:
        """Judge if the output path exist

        Returns:
            bool: Result
        """
        return os.path.exists(self.path_to_output)

    @property
    def _output_name_list(self) -> List[str]:
        """Return a list of output

        Returns:
            List[str]: ['5xxxxxxxxxxNAME1', '5xxxxxxxxxxNAME2,...']
        """
        if os.path.exists(self.path_to_output):
            return [f for f in os.listdir(self.path_to_output) if not f.startswith('.')]
        else:
            return []

    def _execute(self, task_name: str, executable_name: str):
        path_to_exe = os.path.join(
            self.path_to_output, task_name, executable_name)
        p = subprocess.Popen(['/bin/zsh', '-c', path_to_exe],
                             stdin=sys.stdin, stderr=subprocess.PIPE, stdout=sys.stdout)
        while p.poll() is None:
            time.sleep(0.1)

    def _make_grade(self, task_name, grade):
        try:
            self.grades[task_name] = [float(score) for score in grade]
        except ValueError:
            print('[ Error ] Value error')

    def _list_submission_dir(self, path_to_dir):
        if os.path.exists(path_to_dir):
            content_list = os.listdir(path_to_dir)
            print('>', '\n> '.join(content_list))
            return content_list
        else:
            print('[ Error ] Directory does not exist')
            return []

    def run(self):
        if not self._output_path_exist:
            path = input('Input output path:')  # Get output_path
            if os.path.exists(path):
                self.path_to_output = path

        task_list: List[str] = self._output_name_list
        task_list_len: List = len(task_list)

        idx: int = 0 # index of submission
        dir_tmp = '' # Tmp directory relate to submission, used by 'cd' and 'ls'

        while True:

            # Interfering with keyboard input
            print('\n[ Info ] Listing submission: {}'.format(task_list[idx]))

            content_list = self._list_submission_dir(
                os.path.join(self.path_to_output, task_list[idx], dir_tmp)) # List content of submission

            if task_list[idx] in self.grades.keys(): # Print current grades
                print('Current Grades: ', ' '.join([str(score) for score in self.grades[task_list[idx]]]))
            
            cmd: List[str] = input('% ').split(' ') # Get keyboard input
            if cmd[0] == '>' or cmd[0] == '.' or cmd[0] == '\x1b[C' or cmd[0] == '\x1b[B': # Move to next submission
                if idx < task_list_len - 1:
                    idx += 1 # increase index
                    dir_tmp = '' # reset Tmp directory
                    replit.clear()# Clear terminal output
                    continue
                else:
                    print('[ Info ] End of submissions')
                    continue

            if cmd[0] == '<' or cmd[0] == ',' or cmd[0] == '\x1b[D' or cmd[0] == '\x1b[A': # Move to previous submission
                if idx > 0:
                    idx -= 1 # decrease index
                    dir_tmp = '' # reset Tmp directory
                    replit.clear()# Clear terminal output
                    continue
                else:
                    print('[ Info ] Begin of submissions')
                    continue

            if cmd[0] in content_list or cmd[0] == '': # Execute submission
                if cmd[0] == '': # Name of executable is 'main' by default
                    cmd[0] = 'main'
                if os.path.isfile(os.path.join(self.path_to_output, task_list[idx], dir_tmp, cmd[0])):
                    print('\n\n---- Begin ----\n')
                    self._execute(task_list[idx], os.path.join(dir_tmp, cmd[0]))
                    print('\n---- End ----\n\n')

                else:
                    print('[ Error ] Not a file')
                continue

            if cmd[0] == 'cd': # Usage similar to 'cd'
                if len(cmd) > 1:
                    if os.path.exists(os.path.join(self.path_to_output, task_list[idx], dir_tmp, cmd[1])):
                        dir_tmp = os.path.join(dir_tmp, cmd[1])
                    else:
                        print('[ Error ] Directory does not exist')
                else:
                    print('[ Error ] Wrong argument')
                continue

            if cmd[0] == 'ls': # Usage similar to 'ls'
                if len(cmd) > 1:
                    self._list_submission_dir(os.path.join(
                        self.path_to_output, task_list[idx], dir_tmp, cmd[1]))
                else:
                    continue

            if cmd[0] == 'grade' or cmd[0] == 'g': # Grade, can accept multiple input score
                if len(cmd) > 1:
                    self._make_grade(task_list[idx], cmd[1:])
                    if idx < task_list_len - 1: idx += 1 # Next submission
                    replit.clear()# Clear terminal output
                    continue
                else:
                    print('[ Error ] Insufficient argument')

            if cmd[0] == 'save' or cmd[0] == 's':
                self.save()

            if cmd[0] == 'quit' or cmd[0] == 'q':
                print('[ Info ] Quitting...')
                self.save()
                break

            if cmd[0] == 'help' or cmd[0] == 'h':
                print(self.__doc__)

    def save(self):
        print('[ Info ] Saving grade report to: {}'.format(self.path_to_grade_report))
        with open(self.path_to_grade_report, 'w') as f:
            f.writelines(['Name,', ','.join(self.dimension), '\n'])
            for task_name in self.grades.keys():
                f.writelines([task_name, ',', ','.join([str(score)
                                                        for score in self.grades[task_name]]),'\n'])


    def __call__(self, *args, **kwargs):
        try:
            self.run(*args, **kwargs)
        except:
            self.save()


if __name__ == '__main__':
    App = ManualGrader()
    App()
