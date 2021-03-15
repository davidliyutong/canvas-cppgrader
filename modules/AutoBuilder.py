import subprocess
import os
from typing import Dict, List, Tuple
from tqdm import tqdm


class AutoBuilder:
    """Build submissions
    """
    _build_instruction: List[str] = ['/bin/zsh', '-c']
    _cmake_instructions: List[List[str]] = [
        ['/bin/zsh', '-c', 'cmake ./'], ['/bin/zsh', '-c', 'make']]

    def __init__(self, args):
        self.task_dir: str = args.o
        self.original_working_dir: str = os.getcwd()
        self.task_list: List[str] = list()
        self.compiler_output: Dict[str, Tuple[int, str]] = dict()
        # Fullfill the build instruction
        self._build_instruction.append(args.c)

    def _list_tasks(self):
        """List the output directory for unprocessed tasks
        """
        for target in [f for f in os.listdir(self.task_dir) if not f.startswith('.')]:
            if target[0] != '.':
                self.task_list.append(target)

    def _proble_cmake(self) -> bool:
        """Check if the directory contains CMakeLists.txt

        Returns:
            bool: exist -> True inexist -> False
        """
        content_list = [f for f in os.listdir(
            os.getcwd()) if not f.startswith('.')]
        if 'CMakeLists.txt' in content_list:
            return True
        else:
            return False

    def _probe_makefile(self) -> bool:
        """Check if the directory contains Makefile

        Returns:
            bool: exist -> True inexist -> False
        """
        content_list = [f for f in os.listdir(
            os.getcwd()) if not f.startswith('.')]
        if 'Makefile' in content_list:
            return True
        else:
            return False

    def _build_executable(self):
        """Build executable for all submissions
        """
        pbar = tqdm(self.task_list)
        os.chdir(self.original_working_dir)

        for task_name in pbar:
            retcode_tmp = 0
            output_tmp = ''

            pbar.set_description('Building {}'.format(task_name))
            # Change current warding directory
            os.chdir(os.path.join(self.task_dir, task_name))

            if self._proble_cmake():  # CMakeLists.txt is found
                ret = subprocess.run(
                    self._cmake_instructions[0], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                retcode_tmp += ret.returncode
                output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')

                ret = subprocess.run(
                    self._cmake_instructions[1], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                retcode_tmp += ret.returncode
                output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')

            elif self._probe_makefile():  # Makefile is found
                ret = subprocess.run(
                    self._cmake_instructions[1], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                retcode_tmp += ret.returncode
                output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')

            else:
                ret = subprocess.run(
                    self._build_instruction, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                retcode_tmp += ret.returncode
                output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')

            self.compiler_output[task_name] = (retcode_tmp, output_tmp)

            # Change back
            os.chdir(self.original_working_dir)

    def run(self):
        """Run builder
        """
        self._list_tasks()
        self._build_executable()

    def __call__(self):
        self.run
