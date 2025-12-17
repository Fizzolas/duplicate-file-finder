# Duplicate File Finder

An advanced GUI application for finding and removing duplicate images and videos with intelligent content comparison, multithreading, and automatic backup functionality.

## Download & Installation

### Option 1: Download Pre-built Release (Recommended)

1. Go to the [Releases](https://github.com/Fizzolas/duplicate-file-finder/releases) page
2. Download the latest `DuplicateFileFinder-vX.X.X.zip`
3. Extract the ZIP file
4. Run `DuplicateFileFinder.exe` (Windows) or the appropriate executable for your OS

### Option 2: Run from Source

**Prerequisites:**
- Python 3.8 or higher
- pip package manager

**Setup:**

1. Clone the repository:
```bash
git clone https://github.com/Fizzolas/duplicate-file-finder.git
cd duplicate-file-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### Option 3: Build Your Own Executable

1. Install build dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

2. Run the build script:

**Windows:**
```bash
build.bat
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

3. Find the executable in the `dist/` folder

## Features

- **Intelligent Duplicate Detection**
  - Exact file matching (hash-based)
  - Visual similarity detection for images (perceptual hashing)
  - Content-based matching for videos
  - Resolution-variant detection (same content, different resolutions)
  - Format-variant detection (same content, different formats)

- **Performance Optimized**
  - Multithreaded scanning for maximum performance
  - Auto-detects system CPU cores and RAM
  - Adjustable memory limits
  - Background processing support
  - Progress tracking and cancellation

- **User-Friendly GUI**
  - Clean, modern dark interface
  - Real-time progress updates
  - Visual preview of duplicates
  - Detailed file information
  - Helpful tooltips and guided workflow

- **Safe Deletion**
  - Automatic backup before deletion
  - Multiple deletion modes
  - Keep best quality option
  - Undo functionality via backups
  - Files sent to Recycle Bin by default

## Usage

1. **Add Folders**: Click "Add Folder" to select directories to scan

2. **Configure Options**:
   - Choose what types of duplicates to find
   - Adjust CPU threads (auto-detected based on your system)
   - Set RAM limit (based on available system memory)
   - Set similarity threshold (higher = stricter matching)
   - Click **"Apply Settings"** to save your configuration

3. **Start Scan**: Click "Start Scan" to begin detection

4. **Review Results**: View grouped duplicates in the results table

5. **Delete Duplicates**:
   - **Delete All But One**: Keep only one copy per duplicate group
   - **Keep Best Quality**: Keep highest resolution/quality version
   - All deleted files are automatically backed up to `./backups/`

## Supported Formats

### Images
- JPEG/JPG, PNG, GIF, BMP, TIFF, WEBP, HEIC/HEIF

### Videos
- MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V

## Configuration

Settings are stored in `config.json`:

```json
{
  "similarity_threshold": 90,
  "thread_count": 4,
  "max_memory_mb": 2048,
  "backup_enabled": true,
  "backup_directory": "./backups",
  "use_trash": true
}
```

## Advanced Features

### Perceptual Hashing

Images are compared using multiple perceptual hash algorithms:
- Average Hash (aHash)
- Difference Hash (dHash)
- Perceptual Hash (pHash)
- Wavelet Hash (wHash)

### Video Comparison

Videos are analyzed using:
- Frame sampling and comparison
- Duration and resolution matching
- Codec and bitrate analysis

### Background Processing

Click "Run in Background" to minimize the application to system tray while scanning continues.

## Safety

- All deletions create automatic backups
- Backups are timestamped ZIP archives in `./backups/`
- Original files can be restored from backups
- Send to trash option (recoverable deletion)
- Backups are created BEFORE any files are deleted

## Performance Tips

- Adjust thread count based on CPU cores (auto-detected)
- Set RAM limit based on available memory (shown in UI)
- Use exact matching first for faster results
- Enable similarity detection only when needed
- Scan smaller directories for quicker results

## Troubleshooting

### High Memory Usage

Reduce RAM limit in Performance settings or scan smaller directories.

### Slow Scanning

Increase thread count or disable similarity detection features.

### Missing Dependencies (Source Install)

Ensure all requirements are installed:
```bash
pip install -r requirements.txt --upgrade
```

## Building a Release Package

To create a distributable ZIP package:

1. Build the executable (see Option 3 above)
2. The executable will be in `dist/DuplicateFileFinder.exe`
3. Create a release ZIP containing:
   - `DuplicateFileFinder.exe`
   - `README.md`
   - `LICENSE`
4. Upload to GitHub Releases

## System Requirements

- **OS**: Windows 10/11, Linux, macOS
- **RAM**: 512 MB minimum, 2 GB recommended
- **CPU**: Dual-core or better
- **Disk Space**: 100 MB for application + space for backups

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

Created by Fizzolas

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
