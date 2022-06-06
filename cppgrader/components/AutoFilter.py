import os
import shutil
import zipfile
import rarfile
from tqdm import tqdm
from typing import Dict, List
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

def canvas_extract_name(target_name: str) -> str:
    """ Extract name from target -> 5xxxxxxxxxxxNAME


    Args:
        target_name (str): Example: 5xxxxxxxxxxxNAME_*_*_*_.zip

    Returns:
        str: Example 5xxxxxxxxxxxNAME
    """
    return target_name.split('_')[0]

def canvas_remove_prefix(path_to_file: str) -> str:
    """Remove canvas prefix of file

    Args:
        path_to_file (str): 5xxxxxxxxxxxNAME_*_*_filename.cpp 

    Returns:
        str: filename.zip
    """

    return ''.join(os.path.basename(path_to_file).split('_')[3:])

def canvas_test_submission_format(path_to_dir: str) -> List[int]:
    """Check if the submission is of correct format

    Args:
        path_to_dir (str): path to submission

    Returns:
        List[int]: [0,0] -> incorrec, [1,0] -> correct, [1,1] -> correct and the submission is included in another folder
    """
    content_list: List[str] = [f for f in os.listdir(
        path_to_dir) if ((not f.startswith('.')) and (not f.startswith('__MACOSX')))]
    ret: List[int] = [0,0]
    # If the zip file contains only one folder, step in
    if len(content_list) == 1 and os.path.isdir(os.path.join(path_to_dir, content_list[0])):
        content_list = [f for f in os.listdir(os.path.join(
            path_to_dir, content_list[0])) if not f.startswith('.')]
        ret[0] = 1

    if 'CMakeLists.txt' in content_list or 'Makefile' in content_list:
        ret[1] = 1
        return ret

    return ret

class AutoFilter:
    """Filter files
    """

    def __init__(self, args):
        self.submission_dir: str = args.submission_dir  # Submission directory
        # Example:
        # Submission director
        # ├── 5xxxxxxxxxxxNAME_*_*_*.zip
        # ├── ...
        # └── ...

        self.output_dir: str = args.output_dir  # Output directory
        # Example:
        # Output director
        # ├── 5xxxxxxxxxxxNAME
        #     ├── include
        #     ├── src
        #     └── CMakeLists.txt
        # ├── ...
        # └── ...

        # student_name -> [files] mapping
        self.target_mapping: Dict[str, List[str]] = dict()
        # file -> Exception mapping
        self.failed_targets: Dict[str, str] = dict()
        self.keep_output = args.keep_output  # Whether to keep output file
        self.keep_file_structure = args.keep_file_structure

        self._extract_name = canvas_extract_name
        self._remove_prefix = canvas_remove_prefix
        self._test_submission_format = canvas_test_submission_format

    def _create_output_dir(self):
        """Create the output directory, will override the directory
        """

        if os.path.exists(self.output_dir):
            if not self.keep_output:
                logging.info("Output folder exists, override")
                shutil.rmtree(self.output_dir)
                os.mkdir(self.output_dir)
            else:
                logging.info("keep_output==True, keep")
                pass
        else:
            os.mkdir(self.output_dir)

    def _preprocess_zip(self, path_to_zipfile: str):
        """Extract zip file to their related directory
        /path/5xxxxxxxxxxxNAME_*_*_*_.zip will be extract to /path/5xxxxxxxxxxxNAME_*_*_*_(dir)

        Args:
            path_to_zipfile (str): path to strfile
        """

        dir_related: str = os.path.splitext(
            os.path.basename(path_to_zipfile))[0]

        if os.path.exists(dir_related):
            shutil.rmtree(dir_related)
            os.mkdir(dir_related)
        f = zipfile.ZipFile(path_to_zipfile)
        try:
            if not os.path.exists(os.path.join(self.submission_dir, dir_related)):
                f.extractall(os.path.join(self.submission_dir, dir_related))
            else:
                logging.warning("{path_to_zipfile} is uncompressed manually")
        except Exception as err:
            logging.warning("{path_to_zipfile} could not be processed")
            shutil.rmtree(os.path.join(self.submission_dir, dir_related))
            self.failed_targets[path_to_zipfile] = err

    def _preprocess_rar(self, path_to_rarfile):
        """Extract rar file to their related directory

        Args:
            path_to_rarfile (str): Path to rarfile

        Bug:
            Usually dont work because for compatibility issues
        """

        dir_related: str = os.path.splitext(
            os.path.basename(path_to_rarfile))[0]

        if os.path.exists(dir_related):
            shutil.rmtree(dir_related)
            os.mkdir(dir_related)
        f = rarfile.RarFile(path_to_rarfile)
        try:
            f.extractall(os.path.join(self.submission_dir, dir_related))
        except Exception as err:
            logging.warning("{path_to_rarfile} could not be processed".format())
            shutil.rmtree(os.path.join(self.submission_dir, dir_related))
            self.failed_targets[path_to_rarfile] = err

    def _preprocess_tar(self, path_to_tarball: str):
        raise NotImplementedError

    def _preprocess(self):
        """Extract all zip/rar files
        """

        target_list: List[str] = [f for f in os.listdir(
            self.submission_dir) if not f.startswith('.')]
        for target in target_list:
            target_path = os.path.join(self.submission_dir, target)
            if os.path.isfile(target_path):
                if zipfile.is_zipfile(target_path):
                    self._preprocess_zip(target_path)
                if rarfile.is_rarfile(target_path):
                    self._preprocess_rar(target_path)

    def _map_submission(self):
        """Map submission to student names(IDs)
        """

        target_list: List[str] = [f for f in os.listdir(
            self.submission_dir) if not f.startswith('.')]
        for target in target_list:
            ext = os.path.splitext(target)[-1]

            # Ignore hidden files, compressed files
            if target[0] == '.' or ext in ['.rar', '.zip']:
                continue

            # Extract names from submission
            name = target.split('_')[0]

            if name in self.target_mapping.keys():
                self.target_mapping[name].append(
                    os.path.join(self.submission_dir, target))
            else:
                self.target_mapping[name] = [
                    os.path.join(self.submission_dir, target)]

    def _create_alldir(self):
        """Prepare output directory for everyone

        """
        for name in self.target_mapping.keys():
            if not os.path.exists(os.path.join(self.output_dir, name)):
                os.mkdir(os.path.join(self.output_dir, name))
                os.mkdir(os.path.join(self.output_dir, name, 'src'))
                os.mkdir(os.path.join(self.output_dir, name, 'include'))

    def _clean_dir(self, path_to_dir: str):
        """Clean a directory by recreation

        Args:
            path_to_dir (str): Output directory
        """
        shutil.rmtree(path_to_dir)
        os.mkdir(path_to_dir)

    def _filter_process_plain(self, student_name: str, path_to_file: str, remove_prefix: bool = False):
        """Process uncompressed files

        Args:
            student_name (str): student's name 5xxxxxxxxxxxNAME
            path_to_file (str): path to file
            remove_prefix (bool, optional): if the canvas prefix exist (and should be removed). Defaults to False.

        Returns:
            bool: if the file is filtered out
        """
        ext: str = os.path.splitext(path_to_file)[-1]

        # Match extension
        if remove_prefix:
            # The file is isolated
            prefix_removed_filename: str = self._remove_prefix(
                path_to_file)
            if ext in ['.cpp', '.c', 'cxx']:
                shutil.copy(path_to_file, os.path.join(
                    self.output_dir, student_name, 'src', prefix_removed_filename))

            elif ext in ['.hpp', '.h']:
                shutil.copy(path_to_file, os.path.join(
                    self.output_dir, student_name, 'include', prefix_removed_filename))

            elif ext in ['.txt', '.md', '.pdf', '.word', '.tex', '.exe', '.out', '.bin', '']:
                shutil.copy(path_to_file, os.path.join(
                    self.output_dir, student_name, prefix_removed_filename))
            else:
                return False
        else:
            if ext in ['.cpp', '.c']:
                shutil.copy(path_to_file, os.path.join(
                    self.output_dir, student_name, 'src'))

            elif ext in ['.hpp', '.h']:
                shutil.copy(path_to_file, os.path.join(
                    self.output_dir, student_name, 'include'))

            elif ext in ['.txt', '.md', '.pdf', 'rtf', '.tex', '.exe', '.out', '.bin', 'doc', 'docx', 'html','']:
                shutil.copy(path_to_file, os.path.join(
                    self.output_dir, student_name))
            else:
                return False
        return True

    def _filter_process_dir(self, student_name: str, path_to_dir: str) -> bool:
        """Process a directory

        Args:
            student_name (str): student's name 5xxxxxxxxxxxNAME
            path_to_dir (str): path to a directory

        Returns:
            bool: If the submission is of correct format(has CMakeLists.txt)
        """
        if self.keep_output and os.path.exists(os.path.join(self.output_dir, student_name)):
            logging.info('Keeping {}'.format(os.path.join(self.output_dir, student_name)))
            return True
        # Check if the submission is of correct format
        ret: List[int] = self._test_submission_format(path_to_dir)

        if ret[1] > 0 or self.keep_file_structure > 0:  # Is of correct format, 
            self._clean_dir(os.path.join(self.output_dir, student_name))
            if ret[0] > 0:  # The entire folder is compressed and of correct format
                path_to_dir = os.path.join(
                    path_to_dir, [f for f in os.listdir(path_to_dir) if ((not f.startswith('.')) and (not f.startswith('__MACOSX')))][0])

            content_list = [f for f in os.listdir(
                path_to_dir) if not f.startswith('.')]
            for content in content_list:
                if (os.path.isdir(os.path.join(path_to_dir, content))):
                    shutil.copytree(os.path.join(path_to_dir, content), os.path.join(
                        self.output_dir, student_name, content))
                else:
                    shutil.copyfile(os.path.join(path_to_dir, content), os.path.join(
                        self.output_dir, student_name, content))
            return True
        else:  # Incorrect format
            for path_to_dir, _, filenames in os.walk(path_to_dir):
                for filename in filenames:
                    if filename[0] != '.':
                        self._filter_process_plain(
                            student_name, os.path.join(path_to_dir, filename))
            return False

    def _filter_all(self):
        """Apply filters to submission
        """
        pbar = tqdm(self.target_mapping.keys())
        for name in pbar:
            pbar.set_description('Processing {}'.format(name))
            for target in self.target_mapping[name]:
                if os.path.isdir(target):
                    self._filter_process_dir(name, target)
                else:
                    # For students who submitted seperated files, prefix must be removed
                    self._filter_process_plain(
                        name, target, remove_prefix=True)

    def run(self):
        """Run the filter
        """
        self._create_output_dir()
        self._preprocess()
        self._map_submission()
        self._create_alldir()
        self._filter_all()
        logging.info("The unprocessed files are:")
        for target_name in self.failed_targets:
            print('>', target_name)

    def __call__(self):
        self.run()
