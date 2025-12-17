# Duplicate File Finder

**Find and remove duplicate images and videos with intelligent content comparison, automatic backups, and a clean GUI.**

Duplicate File Finder uses advanced perceptual hashing and content analysis to detect not just exact copies, but also similar files across different resolutions, formats, and quality levels. Scan thousands of files quickly with multithreaded processing, then safely delete duplicates with automatic backup protection.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Quick Start

### Download Pre-built Release (Easiest)

1. Go to [Releases](https://github.com/Fizzolas/duplicate-file-finder/releases)
2. Download `DuplicateFileFinder.exe` (Windows) or the latest release for your OS
3. Run the executable - no installation needed!

### Run from Source

If you prefer to run from Python:

```bash
git clone https://github.com/Fizzolas/duplicate-file-finder.git
cd duplicate-file-finder
pip install -r requirements.txt
python main.py
```

---

## ✨ Key Features

### Smart Detection
- **Exact Duplicates**: Hash-based detection finds byte-perfect copies instantly
- **Visual Similarity**: Finds images that look the same even if resolution or compression differs
- **Video Content Matching**: Detects re-encoded videos and resolution variants
- **Cross-Format Detection**: Matches the same content saved in different file formats (JPG vs PNG, MP4 vs AVI)
- **Resolution Variants**: Identifies the same image/video at different sizes

### Performance
- **Multithreaded Scanning**: Automatically uses all available CPU cores
- **Memory Aware**: Adjusts to your system's available RAM (auto-detected)
- **Background Processing**: Minimize the app and let it work while you do other tasks
- **Real-time Progress**: See exactly what's being scanned and how much time remains
- **Cancellable**: Stop scans at any time without losing partial results

### User Experience
- **Modern Dark Interface**: Clean, easy-to-read design with helpful tooltips everywhere
- **Guided Workflow**: Step-by-step prompts make it impossible to get lost
- **Visual Grouping**: Duplicates are clearly organized by group number in the results table
- **Flexible Deletion**: Choose to keep one copy, keep the best quality, or manually select

### Safety First
- **Automatic Backups**: Every deletion creates a timestamped ZIP archive first
- **Recycle Bin Integration**: Deleted files go to Recycle Bin by default (recoverable)
- **Backup Before Delete**: Files are backed up BEFORE deletion - never after
- **No Surprises**: Confirmation dialogs before any destructive action

---

## 📋 How to Use

### Step 1: Add Folders
Click **"Add Folder"** and select one or more directories to scan. Subfolders are automatically included.

### Step 2: Configure Settings

**What to look for:**
- ✅ **Exact duplicates** - Fast and safe, finds identical copies
- ✅ **Similar images** - Finds visually similar photos (different resolutions, slight edits)
- ✅ **Similar videos** - Detects re-encoded or resized videos
- ✅ **Different resolutions** - Treats 1920×1080 and 1280×720 versions as duplicates
- ✅ **Different formats** - Matches JPG/PNG or MP4/AVI versions of same content

**Performance:**
- **CPU Threads**: Auto-detected based on your system (adjust if needed)
- **RAM Limit**: Slider shows your total system RAM - drag to set max usage
- **Similarity Threshold**: Higher = stricter (90% is recommended)

**Important:** Click **"Apply Settings"** after making changes!

### Step 3: Scan
Click **"Start Scan"**. Progress bar and status text show real-time updates.

### Step 4: Review Results
The results table shows all duplicate groups:
- **Group**: Files with the same number are duplicates of each other
- **File Path**: Full location of each file
- **Size**: File size in megabytes
- **Resolution**: Image/video dimensions
- **Format**: File extension
- **Hash**: Unique identifier (truncated for display)
- **Keep/Delete**: Shows which files will be kept or deleted

### Step 5: Delete Safely

**Delete All But One per Group**  
Keeps one file from each duplicate group, backs up and deletes the rest.

**Keep Best Quality per Group**  
Keeps the largest file (usually highest quality) from each group, deletes the rest.

Both options:
1. Create a timestamped backup ZIP in `./backups/`
2. Send files to Recycle Bin (or permanently delete if configured)
3. Show confirmation with backup location

---

## 🎨 Supported File Formats

### Images
`.jpg` `.jpeg` `.png` `.gif` `.bmp` `.tiff` `.webp` `.heic` `.heif`

### Videos
`.mp4` `.avi` `.mov` `.mkv` `.wmv` `.flv` `.webm` `.m4v`

---

## ⚙️ How It Works

### Image Comparison
Uses **perceptual hashing** with four different algorithms:
- **aHash** (Average Hash): Compares average color values
- **dHash** (Difference Hash): Detects edges and gradients
- **pHash** (Perceptual Hash): Frequency-domain analysis via DCT
- **wHash** (Wavelet Hash): Wavelet transform for detail detection

Images are considered similar if their combined hash distance is below the threshold. This catches resized, compressed, or slightly edited versions of the same image.

### Video Comparison
Extracts **10 evenly-spaced frames** from each video:
1. Converts frames to grayscale
2. Resizes to 16×16 for consistent comparison
3. Hashes each frame
4. Compares frame sequences between videos

Videos match if frame sequences are similar AND durations are within 5%.

### Exact Matching
Uses **SHA256 hashing** of entire file content. Two files with the same hash are 100% identical byte-for-byte.

---

## 🛠️ Configuration

Settings are saved in `config.json` (auto-created on first run):

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

**Options:**
- `similarity_threshold`: 50-100, higher = stricter matching
- `thread_count`: Number of CPU threads to use
- `max_memory_mb`: RAM limit in megabytes
- `backup_enabled`: Create backups before deletion (recommended: true)
- `backup_directory`: Where to store backup ZIP files
- `use_trash`: Send files to Recycle Bin instead of permanent deletion

---

## 💡 Performance Tips

- **Large Libraries**: Scan one folder at a time rather than your entire drive
- **Speed vs Accuracy**: Disable "Similar images" and "Similar videos" for faster exact-match-only scans
- **Memory Issues**: Lower the RAM limit if you experience slowdowns or crashes
- **CPU Usage**: Reduce thread count if your PC becomes unresponsive during scans

---

## 🔧 Troubleshooting

### "Scan is slow"
- Increase CPU thread count in Performance settings
- Disable similarity detection (use exact match only)
- Scan smaller directories

### "High memory usage"
- Lower the RAM limit slider in Performance settings
- Close other applications before scanning
- Scan fewer folders at once

### "Results seem wrong"
- Increase similarity threshold (90-95% recommended)
- Enable only "Exact duplicates" to verify hash-based matching first
- Check file extensions match your expectations

### "Application won't start" (source install)
```bash
pip install -r requirements.txt --upgrade
python main.py
```

---

## 📦 Building from Source

To create your own standalone executable:

```bash
# Install build dependencies
pip install -r requirements.txt
pip install pyinstaller

# Windows
build.bat

# Linux/Mac
chmod +x build.sh
./build.sh
```

Executable will be in `dist/DuplicateFileFinder.exe` (or platform equivalent).

---

## 📊 System Requirements

**Minimum:**
- OS: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- RAM: 512 MB
- CPU: Dual-core processor
- Disk: 100 MB for app + space for backups

**Recommended:**
- RAM: 2 GB or more
- CPU: Quad-core or better
- SSD for faster file scanning

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with a clear description

---

## 🐛 Issues & Support

Found a bug or have a feature request? [Open an issue](https://github.com/Fizzolas/duplicate-file-finder/issues).

---

## 👤 Author

Created by **Fizzolas**  
GitHub: [@Fizzolas](https://github.com/Fizzolas)
