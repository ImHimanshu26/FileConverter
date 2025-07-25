import io
import tempfile
import os
from pathlib import Path

try:
    from pydub import AudioSegment
    from pydub.utils import which
except ImportError:
    pass

class AudioConverter:
    """Handles audio format conversions"""
    
    def __init__(self):
        self.supported_formats = ['mp3', 'wav', 'm4a', 'ogg', 'flac']
        self.mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac'
        }
        
        # Set up pydub to work without external dependencies where possible
        AudioSegment.converter = which("ffmpeg") or "ffmpeg"
        AudioSegment.ffmpeg = which("ffmpeg") or "ffmpeg"
        AudioSegment.ffprobe = which("ffprobe") or "ffprobe"
    
    def convert(self, input_path, output_format, original_filename):
        """Convert audio to specified format"""
        
        output_filename = self._get_output_filename(original_filename, output_format)
        
        try:
            # Determine input format
            input_ext = Path(input_path).suffix.lower()[1:]
            
            # Load audio file
            if input_ext == 'mp3':
                audio = AudioSegment.from_mp3(input_path)
            elif input_ext == 'wav':
                audio = AudioSegment.from_wav(input_path)
            elif input_ext == 'm4a':
                audio = AudioSegment.from_file(input_path, format='m4a')
            elif input_ext == 'ogg':
                audio = AudioSegment.from_ogg(input_path)
            elif input_ext == 'flac':
                audio = AudioSegment.from_file(input_path, format='flac')
            else:
                # Try to load as generic audio file
                audio = AudioSegment.from_file(input_path)
            
            # Convert to target format
            return self._export_audio(audio, output_format, output_filename)
            
        except Exception as e:
            # Fallback: try basic conversion without format-specific loading
            try:
                audio = AudioSegment.from_file(input_path)
                return self._export_audio(audio, output_format, output_filename)
            except Exception as fallback_error:
                raise Exception(f"Failed to convert audio: {str(e)}. Fallback also failed: {str(fallback_error)}")
    
    def _export_audio(self, audio, output_format, output_filename):
        """Export audio to specified format"""
        
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as tmp_file:
            tmp_output_path = tmp_file.name
        
        try:
            if output_format == 'mp3':
                audio.export(tmp_output_path, format='mp3', bitrate='192k')
            elif output_format == 'wav':
                audio.export(tmp_output_path, format='wav')
            elif output_format == 'm4a':
                audio.export(tmp_output_path, format='mp4', codec='aac')
            elif output_format == 'ogg':
                audio.export(tmp_output_path, format='ogg')
            elif output_format == 'flac':
                audio.export(tmp_output_path, format='flac')
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            # Read the converted file
            with open(tmp_output_path, 'rb') as f:
                audio_data = f.read()
            
            mime_type = self.mime_types.get(output_format, 'audio/mpeg')
            return audio_data, output_filename, mime_type
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_output_path):
                os.unlink(tmp_output_path)
    
    def _get_output_filename(self, original_filename, output_format):
        """Generate output filename with new extension"""
        base_name = Path(original_filename).stem
        return f"{base_name}.{output_format.lower()}"
