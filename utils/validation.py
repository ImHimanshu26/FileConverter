from pathlib import Path
from utils.file_utils import get_file_type

def validate_file_size(file_size_bytes, file_type):
    """Validate file size based on type"""
    
    # Size limits in bytes
    size_limits = {
        'document': 100 * 1024 * 1024,  # 100MB
        'image': 100 * 1024 * 1024,     # 100MB
        'audio': 100 * 1024 * 1024,     # 100MB
        'video': 50 * 1024 * 1024       # 50MB (smaller due to processing requirements)
    }
    
    limit = size_limits.get(file_type, 100 * 1024 * 1024)
    
    if file_size_bytes > limit:
        limit_mb = limit / (1024 * 1024)
        file_size_mb = file_size_bytes / (1024 * 1024)
        return False, f"File size ({file_size_mb:.1f} MB) exceeds limit for {file_type} files ({limit_mb:.0f} MB)"
    
    return True, "File size is valid"

def validate_file_type(filename):
    """Validate if file type is supported"""
    
    file_type = get_file_type(filename)
    
    if file_type == 'unknown':
        ext = Path(filename).suffix.lower()
        return False, f"Unsupported file type: {ext}"
    
    return True, f"File type '{file_type}' is supported"

def validate_batch_size(file_count):
    """Validate batch conversion size"""
    
    max_batch_size = 10
    
    if file_count > max_batch_size:
        return False, f"Batch size ({file_count}) exceeds maximum allowed ({max_batch_size})"
    
    return True, "Batch size is valid"

def validate_filename(filename):
    """Validate filename for security and compatibility"""
    
    # Check for empty filename
    if not filename or filename.strip() == "":
        return False, "Filename cannot be empty"
    
    # Check filename length
    if len(filename) > 255:
        return False, "Filename is too long (max 255 characters)"
    
    # Check for dangerous patterns
    dangerous_patterns = ['../', '.\\', '<script', '<?php', '#!/']
    filename_lower = filename.lower()
    
    for pattern in dangerous_patterns:
        if pattern in filename_lower:
            return False, f"Filename contains potentially dangerous pattern: {pattern}"
    
    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    base_name = Path(filename).stem.upper()
    if base_name in reserved_names:
        return False, f"Filename uses reserved name: {base_name}"
    
    return True, "Filename is valid"

def get_conversion_warnings(input_format, output_format, file_type):
    """Get warnings about potential quality loss or compatibility issues"""
    
    warnings = []
    
    # Image conversion warnings
    if file_type == 'image':
        if input_format in ['png', 'gif'] and output_format in ['jpg', 'jpeg']:
            warnings.append("Converting from PNG/GIF to JPEG may lose transparency")
        
        if input_format == 'gif' and output_format != 'gif':
            warnings.append("Converting from animated GIF will lose animation")
        
        if output_format == 'gif' and input_format != 'gif':
            warnings.append("Converting to GIF may reduce color quality (256 colors max)")
    
    # Audio conversion warnings
    elif file_type == 'audio':
        if input_format in ['flac', 'wav'] and output_format in ['mp3', 'm4a', 'ogg']:
            warnings.append("Converting from lossless to lossy format will reduce quality")
        
        if output_format == 'wav' and input_format != 'wav':
            warnings.append("Converting to WAV will create larger file sizes")
    
    # Video conversion warnings
    elif file_type == 'video':
        warnings.append("Video conversion may take several minutes")
        warnings.append("Video quality may be reduced to ensure compatibility")
    
    # Document conversion warnings
    elif file_type == 'document':
        if input_format == 'pdf' and output_format in ['txt', 'docx']:
            warnings.append("PDF text extraction may not preserve formatting")
        
        if output_format == 'txt':
            warnings.append("Converting to TXT will lose all formatting")
    
    return warnings
