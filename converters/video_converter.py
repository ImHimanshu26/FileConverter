import tempfile
import os
from pathlib import Path
import subprocess
import sys

class VideoConverter:
    """Handles basic video format conversions"""
    
    def __init__(self):
        self.supported_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm']
        self.mime_types = {
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska',
            'webm': 'video/webm'
        }
    
    def convert(self, input_path, output_format, original_filename):
        """Convert video to specified format"""
        
        output_filename = self._get_output_filename(original_filename, output_format)
        
        try:
            # Check if ffmpeg is available
            if not self._check_ffmpeg():
                raise Exception("FFmpeg is required for video conversion but not available")
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as tmp_file:
                tmp_output_path = tmp_file.name
            
            try:
                # Build ffmpeg command
                cmd = self._build_ffmpeg_command(input_path, tmp_output_path, output_format)
                
                # Run conversion
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    raise Exception(f"FFmpeg conversion failed: {result.stderr}")
                
                # Read converted file
                with open(tmp_output_path, 'rb') as f:
                    video_data = f.read()
                
                mime_type = self.mime_types.get(output_format, 'video/mp4')
                return video_data, output_filename, mime_type
                
            finally:
                # Clean up temporary output file
                if os.path.exists(tmp_output_path):
                    os.unlink(tmp_output_path)
                    
        except Exception as e:
            # If ffmpeg is not available, return a more user-friendly error
            if "FFmpeg" in str(e):
                raise Exception("Video conversion requires FFmpeg installation. Please use a simpler format conversion or install FFmpeg.")
            raise Exception(f"Failed to convert video: {str(e)}")
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _build_ffmpeg_command(self, input_path, output_path, output_format):
        """Build ffmpeg command for conversion"""
        
        base_cmd = ['ffmpeg', '-i', input_path, '-y']  # -y to overwrite output file
        
        if output_format == 'mp4':
            # High compatibility MP4
            cmd = base_cmd + [
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                '-movflags', '+faststart',
                output_path
            ]
        elif output_format == 'avi':
            # Standard AVI
            cmd = base_cmd + [
                '-c:v', 'libx264',
                '-c:a', 'mp3',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
        elif output_format == 'mov':
            # QuickTime MOV
            cmd = base_cmd + [
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
        elif output_format == 'webm':
            # WebM for web
            cmd = base_cmd + [
                '-c:v', 'libvpx-vp9',
                '-c:a', 'libopus',
                '-crf', '30',
                '-b:v', '0',
                output_path
            ]
        elif output_format == 'mkv':
            # Matroska container
            cmd = base_cmd + [
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-crf', '23',
                output_path
            ]
        else:
            # Generic conversion
            cmd = base_cmd + [output_path]
        
        return cmd
    
    def _get_output_filename(self, original_filename, output_format):
        """Generate output filename with new extension"""
        base_name = Path(original_filename).stem
        return f"{base_name}.{output_format.lower()}"
