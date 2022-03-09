import subprocess
import os
from typing import Dict, List, Tuple
from tqdm import tqdm


class AutoBuilder:
    """Build submissions
    """
    shell_executable: str = '/bin/zsh'

    def __init__(self, args, shell_executable: str='/bin/zsh'):
        self.task_dir: str = args.output_dir
        self.original_working_dir: str = os.getcwd()
        self.task_list: List[str] = list()
        self.compiler_output: Dict[str, Tuple[int, str]] = dict()
        # Fullfill the build instruction
        self.compiler_command = args.command
        self.shell_executable = shell_executable

    @property
    def _build_instruction(self) -> List[str]:
        return [self.shell_executable, '-c', self.compiler_command]

    @property
    def _cmake_instructions(self) ->List[List[str]]:
        return [
        [self.shell_executable, '-c', 'cmake ./'], [self.shell_executable, '-c', 'make']]
    
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

    def _build_executable_cmake(self, retcode_tmp, output_tmp):
        ret = subprocess.run(
                    self._cmake_instructions[0], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retcode_tmp += ret.returncode
        output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')

        return self._build_executable_make(retcode_tmp, output_tmp)
       
    def _build_executable_make(self, retcode_tmp, output_tmp):
        ret = subprocess.run(
                    self._cmake_instructions[1], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retcode_tmp += ret.returncode
        output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')
        
        if retcode_tmp != 0:
            return self._build_executable_cmd(0, output_tmp + '\nMakefile failed, fallback to command')
        return retcode_tmp, output_tmp
    
    def _build_executable_cmd(self, retcode_tmp, output_tmp):
        ret = subprocess.run(
                    self._build_instruction, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retcode_tmp += ret.returncode
        output_tmp += str(ret.stderr + ret.stdout, encoding='UTF-8')
        return retcode_tmp, output_tmp

        
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
                retcode_tmp, output_tmp = self._build_executable_cmake(retcode_tmp, output_tmp)

            elif self._probe_makefile():  # Makefile is found
                retcode_tmp, output_tmp = self._build_executable_make(retcode_tmp, output_tmp)

            else:
                retcode_tmp, output_tmp = self._build_executable_cmd(retcode_tmp, output_tmp)

            self.compiler_output[task_name] = (retcode_tmp, output_tmp)

            # Change back
            os.chdir(self.original_working_dir)

    def run(self):
        """Run builder
        """
        self._list_tasks()
        self._build_executable()

    def __call__(self):
        self.run()
