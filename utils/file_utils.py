from pathlib import Path

def get_file_type(filename):
    """Determine the type category of a file based on its extension"""
    
    ext = Path(filename).suffix.lower()[1:]  # Remove the dot
    
    document_formats = ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']
    image_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'svg']
    audio_formats = ['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'wma']
    video_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', '3gp']
    
    if ext in document_formats:
        return 'document'
    elif ext in image_formats:
        return 'image'
    elif ext in audio_formats:
        return 'audio'
    elif ext in video_formats:
        return 'video'
    else:
        return 'unknown'

def get_supported_formats(file_type):
    """Get list of supported output formats for a given file type"""
    
    format_mapping = {
        'document': ['pdf', 'docx', 'txt'],
        'image': ['jpg', 'png', 'gif', 'webp', 'bmp'],
        'audio': ['mp3', 'wav', 'm4a'],
        'video': ['mp4', 'avi', 'mov']
    }
    
    return format_mapping.get(file_type, [])

def clean_filename(filename):
    """Clean filename to remove invalid characters"""
    
    # Remove or replace invalid characters
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    
    clean_name = filename
    for char in invalid_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Remove multiple consecutive underscores
    while '__' in clean_name:
        clean_name = clean_name.replace('__', '_')
    
    # Remove leading/trailing underscores and spaces
    clean_name = clean_name.strip('_ ')
    
    return clean_name

def get_file_size_mb(file_size_bytes):
    """Convert file size from bytes to MB"""
    return file_size_bytes / (1024 * 1024)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_mime_type(file_extension):
    """Get MIME type for a file extension"""
    
    mime_types = {
        # Documents
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain',
        'rtf': 'application/rtf',
        
        # Images
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'bmp': 'image/bmp',
        
        # Audio
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'm4a': 'audio/mp4',
        'ogg': 'audio/ogg',
        'flac': 'audio/flac',
        
        # Video
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska',
        'webm': 'video/webm'
    }
    
    return mime_types.get(file_extension.lower(), 'application/octet-stream')
