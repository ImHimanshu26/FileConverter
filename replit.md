# Universal File Converter

## Overview

This is a Streamlit-based universal file converter application that handles conversions between various document, image, audio, and video formats. The application provides a web interface for users to upload files and convert them to different formats, with support for batch processing and download functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **UI Components**: 
  - Main conversion interface with file upload
  - Sidebar showing supported formats
  - Session state management for conversion history
  - Wide layout with expandable sidebar

### Backend Architecture
- **Core Structure**: Modular converter classes for different file types
- **Converter Pattern**: Separate converter classes for each media type (documents, images, audio, video)
- **Utility Layer**: Shared utilities for file operations and validation
- **Processing Flow**: Upload → Validation → Conversion → Download

## Key Components

### Converter Classes
1. **DocumentConverter**: Handles PDF, DOC, DOCX, TXT, RTF conversions
   - Uses libraries: docx, PyPDF2, reportlab, docx2pdf
   - Supports conversions to PDF, DOCX, TXT formats

2. **ImageConverter**: Manages image format conversions
   - Uses PIL (Pillow) for image processing
   - Supports JPG, PNG, GIF, WebP, BMP formats
   - Handles transparency and color mode conversions

3. **AudioConverter**: Processes audio file conversions
   - Uses pydub with ffmpeg backend
   - Supports MP3, WAV, M4A, OGG, FLAC formats
   - Configures ffmpeg paths automatically

4. **VideoConverter**: Handles video format conversions
   - Uses ffmpeg via subprocess calls
   - Supports MP4, AVI, MOV, MKV, WebM formats
   - Includes timeout protection (5 minutes)

### Utility Modules
1. **file_utils.py**: File type detection and filename cleaning
2. **validation.py**: File size, type, and batch validation with security checks

### Session Management
- Tracks converted files in session state
- Maintains conversion history
- Handles temporary file cleanup

## Data Flow

1. **File Upload**: User uploads files through Streamlit interface
2. **Validation**: Files are validated for type, size, and security
3. **Type Detection**: System determines file category (document/image/audio/video)
4. **Format Selection**: User selects target output format
5. **Conversion**: Appropriate converter processes the file
6. **Temporary Storage**: Converted files stored temporarily
7. **Download**: User downloads converted files (single or batch zip)
8. **Cleanup**: Temporary files are cleaned up

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **PIL/Pillow**: Image processing
- **pydub**: Audio processing
- **ffmpeg**: Audio/video processing backend

### Document Processing
- **python-docx**: DOCX file handling
- **PyPDF2**: PDF manipulation
- **reportlab**: PDF generation
- **docx2pdf**: Document to PDF conversion

### System Dependencies
- **ffmpeg**: Required for audio and video conversions
- **ffprobe**: Audio/video metadata extraction

## Deployment Strategy

### Environment Requirements
- Python 3.7+ environment
- External dependencies (ffmpeg) may need system-level installation
- Temporary file storage for processing
- Memory considerations for large file processing

### File Size Limits
- Documents: 100MB
- Images: 100MB  
- Audio: 100MB
- Video: 50MB (reduced due to processing requirements)
- Batch processing: Maximum 10 files

### Error Handling
- Graceful degradation when optional dependencies unavailable
- File validation before processing
- Timeout protection for long-running conversions
- Temporary file cleanup on errors

### Security Considerations
- Filename sanitization to prevent path traversal
- File type validation beyond extension checking
- Size limits to prevent resource exhaustion
- Temporary file isolation