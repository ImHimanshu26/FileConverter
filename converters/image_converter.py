import io
from PIL import Image, ImageSequence
from pathlib import Path

class ImageConverter:
    """Handles image format conversions"""
    
    def __init__(self):
        self.supported_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
        self.mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        }
    
    def convert(self, input_path, output_format, original_filename):
        """Convert image to specified format"""
        
        output_filename = self._get_output_filename(original_filename, output_format)
        
        try:
            # Open the image
            with Image.open(input_path) as img:
                # Handle different conversion scenarios
                if output_format.lower() in ['jpg', 'jpeg']:
                    return self._convert_to_jpeg(img, output_filename)
                elif output_format.lower() == 'png':
                    return self._convert_to_png(img, output_filename)
                elif output_format.lower() == 'gif':
                    return self._convert_to_gif(img, output_filename, input_path)
                elif output_format.lower() == 'webp':
                    return self._convert_to_webp(img, output_filename)
                elif output_format.lower() == 'bmp':
                    return self._convert_to_bmp(img, output_filename)
                else:
                    raise ValueError(f"Unsupported output format: {output_format}")
                    
        except Exception as e:
            raise Exception(f"Failed to convert image: {str(e)}")
    
    def _convert_to_jpeg(self, img, output_filename):
        """Convert image to JPEG format"""
        buffer = io.BytesIO()
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(buffer, format='JPEG', quality=95, optimize=True)
        buffer.seek(0)
        
        return buffer.getvalue(), output_filename, self.mime_types['jpg']
    
    def _convert_to_png(self, img, output_filename):
        """Convert image to PNG format"""
        buffer = io.BytesIO()
        
        # PNG supports all modes, but optimize for common ones
        if img.mode not in ('RGB', 'RGBA', 'L', 'LA'):
            if 'transparency' in img.info:
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
        
        img.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        return buffer.getvalue(), output_filename, self.mime_types['png']
    
    def _convert_to_gif(self, img, output_filename, input_path):
        """Convert image to GIF format"""
        buffer = io.BytesIO()
        
        # Check if the original image is animated
        try:
            img.seek(1)  # Try to go to the second frame
            is_animated = True
            img.seek(0)  # Go back to the first frame
        except:
            is_animated = False
        
        if is_animated:
            # Handle animated GIF
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(img):
                # Convert frame to RGB then to palette mode for GIF
                frame_rgb = frame.convert('RGB')
                frame_p = frame_rgb.quantize(colors=256)
                frames.append(frame_p)
                durations.append(frame.info.get('duration', 100))
            
            frames[0].save(
                buffer,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=True
            )
        else:
            # Handle static image
            if img.mode != 'P':
                if img.mode in ('RGBA', 'LA'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to palette mode for GIF
                img = img.quantize(colors=256)
            
            img.save(buffer, format='GIF', optimize=True)
        
        buffer.seek(0)
        return buffer.getvalue(), output_filename, self.mime_types['gif']
    
    def _convert_to_webp(self, img, output_filename):
        """Convert image to WebP format"""
        buffer = io.BytesIO()
        
        # WebP supports RGB and RGBA
        if img.mode not in ('RGB', 'RGBA'):
            if 'transparency' in img.info or img.mode in ('RGBA', 'LA'):
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
        
        img.save(buffer, format='WebP', quality=90, method=6)
        buffer.seek(0)
        
        return buffer.getvalue(), output_filename, self.mime_types['webp']
    
    def _convert_to_bmp(self, img, output_filename):
        """Convert image to BMP format"""
        buffer = io.BytesIO()
        
        # BMP typically uses RGB mode
        if img.mode in ('RGBA', 'LA', 'P'):
            if 'transparency' in img.info:
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(buffer, format='BMP')
        buffer.seek(0)
        
        return buffer.getvalue(), output_filename, self.mime_types['bmp']
    
    def _get_output_filename(self, original_filename, output_format):
        """Generate output filename with new extension"""
        base_name = Path(original_filename).stem
        return f"{base_name}.{output_format.lower()}"
