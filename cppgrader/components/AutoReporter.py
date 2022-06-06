import datetime
from typing import Dict, Tuple
import uuid
import os
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
class AutoReporter:
    """Creating a report
    """

    def __init__(self, args):
        self.unique_id = str(uuid.uuid1()).split('-')[0]
        self.report_md_path = os.path.join(os.getcwd(), args.report_name + '-' + self.unique_id + '.md')
        self.report_csv_path = os.path.join(os.getcwd(), args.report_name + '-' + self.unique_id + '.csv')

    def _gen_markdown(self, failed_targets: Dict[str, str], compiler_output: Dict[str, Tuple[int, str]]):
        """Generate markdown file

        Args:
            failed_targets (Dict[str, str]): Failed targets
            compiler_output (Dict[str, Tuple[int, str]]): Compiler output

        """
        logging.info("[ Info ] Generating report at {}".format(self.report_md_path))
        with open(self.report_md_path, 'w') as f:
            f.writelines(['# Grader report\n\n',
                          'Time: {}\n'.format(
                              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                          'Total Submissions: {}\n'.format(
                              len(compiler_output.keys())),
                          '\n## Unprocessed submissions:\n\n'])
            f.writelines(['**{}**\n\n```\n{}\n```\n\n'.format(target,
                                                              failed_targets[target]) for target in failed_targets.keys()])
            f.writelines(['\n## Compiler summary\n\n'])
            f.writelines(['|  name  |  status  |\n', '| ------ | ------- |\n'])
            f.writelines(['| **{}** |    {}    |\n'.format(task_name, str(
                compiler_output[task_name][0] == 0)) for task_name in sorted(compiler_output.keys())])
            f.writelines(['\n## Compiler output\n\n'])
            f.writelines(['**{}**: {}\n\n```\n{}\n```\n\n'.format(task_name, str(compiler_output[task_name]
                                                                                 [0] == 0), compiler_output[task_name][1]) for task_name in sorted(compiler_output.keys())])

    def _gen_csv(self, failed_targets: Dict[str, str], compiler_output: Dict[str, Tuple[int, str]]):
        """Generate CSV report

        Args:
            failed_targets (Dict[str, str]): Failed targets
            compiler_output (Dict[str, Tuple[int, str]]): Compiler output
        """
        logging.info("[ Info ] Generating report(csv) at {}".format(self.report_csv_path))
        with open(self.report_csv_path, 'w') as f:
            f.writelines(['name,status,\n'])
            f.writelines(['{},{},\n'.format(task_name, int(compiler_output[task_name][0] == 0)) for task_name in sorted(compiler_output.keys())])

    def run(self, *args, **kwargs):
        # Generate Markdown report
        self._gen_markdown(*args, **kwargs)

        # Generate CSV report
        self._gen_csv(*args, **kwargs)

    def __call__(self, failed_targets: Dict[str, str], compiler_output: Dict[str, Tuple[int, str]]):
        self.run(failed_targets, compiler_output)
