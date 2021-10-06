import datetime
from typing import Dict, Tuple


class AutoReporter:
    """Creating a report
    """

    def __init__(self, args):
        self.report_md_path = args.report_path + '.md'
        self.report_csv_path = args.report_path + '.csv'

    def _gen_markdown(self, failed_targets: Dict[str, str], compiler_output: Dict[str, Tuple[int, str]]):
        """Generate markdown file

        Args:
            failed_targets (Dict[str, str]): Failed targets
            compiler_output (Dict[str, Tuple[int, str]]): Compiler output

        """
        print('[ Info ] Generating report at {}'.format(self.report_md_path))
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
                compiler_output[task_name][0] == 0)) for task_name in compiler_output.keys()])
            f.writelines(['\n## Compiler output\n\n'])
            f.writelines(['**{}**: {}\n\n```\n{}\n```\n\n'.format(task_name, str(compiler_output[task_name]
                                                                                 [0] == 0), compiler_output[task_name][1]) for task_name in compiler_output.keys()])

    def _gen_csv(self, failed_targets: Dict[str, str], compiler_output: Dict[str, Tuple[int, str]]):
        """Generate CSV report

        Args:
            failed_targets (Dict[str, str]): Failed targets
            compiler_output (Dict[str, Tuple[int, str]]): Compiler output
        """
        print('[ Info ] Generating report(csv) at {}'.format(self.report_csv_path))
        with open(self.report_csv_path, 'w') as f:
            f.writelines(['name,status,\n'])
            f.writelines(['{},{},\n'.format(task_name, int(compiler_output[task_name][0] == 0)) for task_name in compiler_output.keys()])

    def run(self, *args, **kwargs):
        # Generate Markdown report
        self._gen_markdown(*args, **kwargs)

        # Generate CSV report
        self._gen_csv(*args, **kwargs)

    def __call__(self, failed_targets: Dict[str, str], compiler_output: Dict[str, Tuple[int, str]]):
        self.run(failed_targets, compiler_output)
