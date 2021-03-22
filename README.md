# SpeedGrader

A grader for canvas submissions

## Dependencies

- rarfile
- tqdm
- reptil
- typing-extensions

(See requirements.txt)

## Usage


```bash
.
├── app.py
└── submission
    ├── 5xxxxxxxxxxxNAME*_*_*.zip
    └── ...
```

Execute

```bash
python app.py
```

Output:

```
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
``` 
```
