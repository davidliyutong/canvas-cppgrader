import os
import os.path as osp
import glob2
from typing import List
import argparse
import difflib
from io import StringIO
import coloredlogs
import logging
import tqdm
import re

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

DEFAULT_IGNORE_PATTERNS = r'.*CMakeCXXCompilerId.cpp|.*CMakeCCompilerId.c|\.vscode|\.idea|\.git|\.gitignore'


def find_c_source_files(base_dir: str, ext: List[str]) -> List[str]:
    """Find C Source Files in the current directory.

    Args:
        base_dir (str): Base directory
        ext (List[str]): Extension

    Returns:
        List[str]: File names
    """
    return sum([glob2.glob(osp.join(base_dir, '**', '*.{}'.format(e)), recursive=True) for e in ext], [])
    # return sum(*[list(map(lambda x: x.name,Path(base_dir).rglob('*.{}'.format(e)))) for e in ext],[])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', type=str, default='./')
    parser.add_argument('--ext', type=str,
                        default='c,cpp,h,hpp,cc,cxx,c++,h++,hxx,hh')
    parser.add_argument('--threshold', type=int, default=100)
    parser.add_argument('--output_dir', type=str, default='./antiplag_output')
    parser.add_argument('--use_basename', type=bool, default=False)
    parser.add_argument('--path_depth', type=int, default=2)
    parser.add_argument('--ignore_pattern', type=str, default='\.\.')
    # parser.add_argument('--debug', action='store_true')
    # parser.add_argument('--verbose', action='store_true')
    # parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    args.ext = args.ext.split(',')
    return args


def read_files(files: List[str]) -> List[str]:
    """Read files.

    Args:
        files (List[str]): File names

    Returns:
        List[str]: File contents
    """
    return {f: open(f).read() for f in files}


def html_comp(in_lines1: list, in_lines2: list, out_file: str):
    d = difflib.HtmlDiff()
    result = d.make_file(in_lines1, in_lines2)
    with open(out_file, 'w') as f:
        f.writelines(result)


def context_comp(in_lines1: list, in_lines2: list, out_file: str = None):
    d = difflib.context_diff(in_lines1, in_lines2)
    buf = StringIO()
    buf.writelines(d)
    if out_file is not None and out_file != '':
        with open(out_file, 'w') as f:
            f.writelines(d)
    return len(buf.getvalue()), buf


def main():
    args = parse_args()

    # if args.debug:
    #     pass
    #     args.base_dir = './PermutationOut'
    #     args.ext = ['cpp']

    if not osp.exists(args.output_dir):
        logger.info('Creating output directory: {}'.format(args.output_dir))
        os.makedirs(args.output_dir)

    logging.info(f"Processing files in {args.base_dir}")
    list_of_files = find_c_source_files(args.base_dir, ext=args.ext)
    logging.info(f"Reading {len(list_of_files)} files")
    file_contents = read_files(list_of_files)
    num_files = len(file_contents)

    with tqdm.tqdm(total=num_files) as pbar:
        for index1 in range(num_files):
            pbar.set_description(f"Processing file {list_of_files[index1]}")
            for index2 in range(index1+1, num_files):
                file1 = list_of_files[index1]
                file2 = list_of_files[index2]
                if (not len(re.findall(DEFAULT_IGNORE_PATTERNS, file1)) > 0) and (not len(re.findall(DEFAULT_IGNORE_PATTERNS, file2)) > 0):
                    if (not len(re.findall(args.ignore_pattern, file1)) > 0) and (not len(re.findall(args.ignore_pattern, file2)) > 0):
                        num_chars, _ = context_comp(file_contents[file1].split(
                            '\n'), file_contents[file2].split('\n'))

                        if num_chars < args.threshold:
                            logging.warning('{} and {} are {} chars different'.format(
                                file1, file2, num_chars))
                            if args.use_basename:
                                report_name = osp.join(
                                    args.output_dir, '{}-{}.html'.format(osp.basename(file1), osp.basename(file2)))
                            else:
                                report_name = osp.join(args.output_dir, '.'.join(file1.split(
                                    os.sep)[-args.path_depth:]) + '-' + '.'.join(file2.split(os.sep)[-args.path_depth:]) + '.html')
                            html_comp(file_contents[file1].split('\n'),
                                      file_contents[file2].split('\n'),
                                      report_name)
            pbar.update()


if __name__ == '__main__':
    main()
