# Duplicate File Finder

An advanced GUI application for finding and removing duplicate images and videos with intelligent content comparison, multithreading, and automatic backup functionality.

## Features

- **Intelligent Duplicate Detection**
  - Exact file matching (hash-based)
  - Visual similarity detection for images (perceptual hashing)
  - Content-based matching for videos
  - Resolution-variant detection (same content, different resolutions)
  - Format-variant detection (same content, different formats)

- **Performance Optimized**
  - Multithreaded scanning for maximum performance
  - Background processing support
  - Progress tracking and cancellation
  - Memory-efficient processing

- **User-Friendly GUI**
  - Clean, modern interface
  - Real-time progress updates
  - Visual preview of duplicates
  - Detailed file information

- **Safe Deletion**
  - Automatic backup before deletion
  - Multiple deletion modes
  - Keep best quality option
  - Undo functionality via backups

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Fizzolas/duplicate-file-finder.git
cd duplicate-file-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Click "Add Folder" to select directories to scan

3. Configure scan options:
   - **Exact Match**: Find identical files
   - **Similar Images**: Find visually similar images (adjustable threshold)
   - **Similar Videos**: Find content-similar videos
   - **Different Resolutions**: Find same content at different resolutions
   - **Different Formats**: Find same content in different formats

4. Click "Start Scan" to begin detection

5. Review results and select deletion mode:
   - **Delete All But One**: Keep only one copy per duplicate group
   - **Delete All But Best Quality**: Keep highest resolution/quality version
   - **Custom Selection**: Manually select files to delete

6. Deleted files are automatically backed up to `./backups/backup_YYYYMMDD_HHMMSS.zip`

## Supported Formats

### Images
- JPEG/JPG
- PNG
- GIF
- BMP
- TIFF
- WEBP
- HEIC/HEIF

### Videos
- MP4
- AVI
- MOV
- MKV
- WMV
- FLV
- WEBM
- M4V

## Configuration

Settings are stored in `config.json` and can be adjusted:

```json
{
  "similarity_threshold": 90,
  "thread_count": 4,
  "max_memory_mb": 2048,
  "backup_enabled": true,
  "backup_directory": "./backups"
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
- Backups are timestamped ZIP archives
- Original files can be restored from backups
- Send to trash option (recoverable deletion)

## Performance Tips

- Adjust thread count based on CPU cores (default: auto-detect)
- Use exact matching first for faster results
- Enable similarity detection only when needed
- Scan smaller directories for quicker results

## Troubleshooting

### High Memory Usage

Reduce `max_memory_mb` in config.json or scan smaller directories.

### Slow Scanning

Increase `thread_count` or disable similarity detection features.

### Missing Dependencies

Ensure all requirements are installed:
```bash
pip install -r requirements.txt --upgrade
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

Created by Fizzolas
