# SpeedGrader

A grader for canvas submissions

## Dependencies

The package has following dependencies and can be installed via PIP

- rarfile
- tqdm
- reptil
- typing-extensions
- coloredlogs
- zsh Shell(or any shell with regex command support)

(See requirements.txt)

## Installation

```shell
python setup.py install
```

or

```shell
python setup.py bdist_wheel
pip install dist/canvasgrader-<version>-<arch>.whl
```

## Usage

Prepare the submission files. User should extract submission as follows. The name of submission directory is `submission` by default.

```shell
.
└── submission
    ├── 5xxxxxxxxxxxNAME*_*_*.zip
    └── ...
```

Where `5xxxxxxxxxxx` is student's ID number. We denote this folder as `$submission_root`

Run the canvasgrader module with appropriated arguments

```shell
python -m canvasgrader --submission_dir=$submission_root --output_dir=$output_dir --report_name=REPORT
```

For example

```shell
python -m canvasgrader --submission_dir=./submission --output_dir=./output --report_name=REPORT
```

**Arguments**:

- `--submission_dir` The root of submission
- `--output_dir=$output_dir` The output directory of processed submissions
- `--report_name` Name of report, will genearate `$report_name-xxxxxx.md/csv`

This will generate processed submissions:

```text
.
├── output
│   ├── 5xxxxxxxxxxxNAME
│   │   ├── src
│   │   ├── include
│   │   └── main
│   └── ...
├── REPORT.csv
└── REPORT.md
```

## Mechanisme

This tool process submissions as follows

1. Smart Extraction. The files are extracted in a smart way. For example, zip archieves with single directory can be detected.
2. Reorganization. The tool scans for the presence of `CMakeLists.txt` or `Makefile`. If one of them exists, the structure of submission is preserved. Otherwise, it will move all source files ro `src` subdirectory and `hpp` to `include` subdirectory
3. Build executable. CMake and Makefile submission are automatically treated. Other submisions will be build by `g++ ./src/*.(c|cpp) -I ./include -o main -Wall -g --std=c++17`. This command will be executed with `/bin/zsh`

## App - ManulGrader

Use keys to navigate between submissions

- `<-`, `<`, `,` for previous submission
- `->`, `>`, `.` for next submission
- `[executable]` run executable
- `cd` change directory
- `ls` list directory
- `grade [score]`, `g [score]` to cache score
- `save` to save score to disk
- `quit` to quit
- `help` to display help

## Full command args

- `--submission_dir`, `-s` Path to submision directory
- `--output_dir`, `-o` Path to output directory
- `--report_path`, `-r` Path to report, will generate `<REPORT>.csv|md`
- `--command`, `-c` Build command, default is `g++ ./src/*.(c|cpp) -I ./include -o main -Wall -g -std=c++14`
- `--keep_output` Will assume that output_dir exists and is properly filtered, the output_dir will not be modified
- `--keep_file_structure` Will keep the structure of original submission without auto-filtering (but will extract submissions)
- `-a` Choose apps to launch in filter/builder/reporter/grader

## Antiplag Module

An antiplag script is added to fight against cheating. The antiplag tool use `difflib` to compare the similarity of C/C++ source files.

To run the app, execute the following command

```shell
python -m canvasgrader.tools.antiplag --base_dir=$output_dir
```

The `$output_dir` can be any directory. All source files and header files under this directory will be cross compared (complexity $\mathcal{O}(N^2)$).

There are other configurable arguments:

- `--base_dir` Root directory
- `--ext` Comma seperated extensions, default to `c,cpp,h,hpp,cc,cxx,c++,h++,hxx,hh`
- `--threshold` Threshold to determine plagarism. Default is 100 (less than 100 characters of difference)
- `--output_dir` Output of report. Cross compare report will be generated under this directory as html files. Default is `./antiplag_output`
- `--use_basename` If the report should use basename of files.
- `--path_depth` If the report should use a section of directory of files, default is 2
- `--ignore_pattern` Ignore files with this pattern. This should be a regex expression.
