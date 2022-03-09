# SpeedGrader

A grader for canvas submissions

## Dependencies

- rarfile
- tqdm
- reptil
- typing-extensions
- zsh Shell(or any shell with regex command support)

(See requirements.txt)

## Installation

```bash
python setup.py install
```

or

```bash
python setup.py bdist_wheel
pip install dist/canvasgrader-<version>-<arch>.whl
```

## Usage

Extract submission as follows. The name of submission directory is `submission` by default.

```bash
.
├── app.py
└── submission
    ├── 5xxxxxxxxxxxNAME*_*_*.zip
    └── ...
```

Execute

```bash
python -m canvasgrader
```

Output:

```text
.
├── app.py
├── submission
│   ├── 5xxxxxxxxxxxNAME_*_*_*_.zip
│   └── ...
├── output
│   ├── 5xxxxxxxxxxxNAME
│   │   ├── src
│   │   ├── include
│   │   └── main
│   └── ...
└── REPORT.md
```

## Function

- Filter the submission
- Build executable

## ManulGrader

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
- `--keep_output` Will assume that output_dir exists and is properly filtered
- `--keep_file_structure` Will keep the structure of original submission without auto-filtering (but will extract submissions)
- `-a` Choose apps to launch in filter/builder/reporter/grader