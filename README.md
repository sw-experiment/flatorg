# flatorg
Flatten folder structure and organise files - useful clean-up for digital hoarders

## Usage

Run the `flatorg.py` script with two arguments: the source directory and the destination directory.

```bash
python flatorg.py /path/to/source /path/to/destination
```

For a dry run that shows what would be done without actually copying files:

```bash
python flatorg.py --plan /path/to/source /path/to/destination
```

The script will:
- Recursively scan the source directory for all files (including hidden files)
- Copy files to the destination directory organized into subfolders:
  - `pics/` for image files (.jpg, .png, etc.)
  - `vids/` for video files (.mp4, .avi, etc.)
  - `docs/` for all other file types
- Rename files with a sequential numeric prefix (e.g., 0001_filename.jpg)
- Show progress percentage and current file being copied
- Create a timestamped log file recording all copy operations
- Verify that the number of files in destination matches source
- Display a summary of file counts

## Safety Features

The script includes defensive programming to prevent data loss:
- **No writes to source**: Destination cannot be inside the source directory
- **No overwrites**: Refuses to run if destination directory already contains files
- **Path validation**: Ensures source and destination are valid directories

## Requirements

- Python 3.8+

## Development

This project uses:
- Ruff for formatting and linting
- Pyright for static type checking with strict settings

Run checks locally:
```bash
ruff format .
ruff check .
pyright --warnings
```
