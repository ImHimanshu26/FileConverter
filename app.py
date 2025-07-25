import streamlit as st
import os
import tempfile
import zipfile
from io import BytesIO
import time
from pathlib import Path

from converters.document_converter import DocumentConverter
from converters.image_converter import ImageConverter
from converters.audio_converter import AudioConverter
from converters.video_converter import VideoConverter
from utils.file_utils import get_file_type, get_supported_formats, clean_filename
from utils.validation import validate_file_size, validate_file_type

# Configure page
st.set_page_config(
    page_title="Universal File Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add PWA meta tags and service worker
def add_pwa_tags():
    st.markdown("""
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#ff6b6b">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="File Converter">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/static/sw.js')
                    .then(function(registration) {
                        console.log('SW registered: ', registration);
                    }).catch(function(registrationError) {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }
    </script>
    """, unsafe_allow_html=True)

add_pwa_tags()

# Initialize session state
if 'converted_files' not in st.session_state:
    st.session_state.converted_files = []
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

def main():
    st.title("🔄 Universal File Converter")
    st.markdown("Convert documents, images, audio, and video files between different formats")
    
    # Sidebar with supported formats
    with st.sidebar:
        st.header("📋 Supported Formats")
        
        with st.expander("📄 Documents"):
            st.write("**Input:** PDF, DOC, DOCX, TXT, RTF")
            st.write("**Output:** PDF, DOCX, TXT")
        
        with st.expander("🖼️ Images"):
            st.write("**Input/Output:** JPG, PNG, GIF, WebP, BMP")
        
        with st.expander("🎵 Audio"):
            st.write("**Input/Output:** MP3, WAV, M4A")
        
        with st.expander("🎬 Video"):
            st.write("**Input/Output:** MP4, AVI, MOV")
        
        st.header("ℹ️ File Limits")
        st.write("• Max file size: 100MB")
        st.write("• Batch limit: 10 files")
        st.write("• Video limit: 50MB")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Upload Files")
        
        # File uploader with multiple file support
        uploaded_files = st.file_uploader(
            "Choose files to convert",
            accept_multiple_files=True,
            help="Drag and drop files here or click to browse"
        )
        
        if uploaded_files:
            if len(uploaded_files) > 10:
                st.error("❌ Please upload maximum 10 files at once")
                return
            
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
            
            # Display uploaded files
            st.subheader("📋 Files to Convert")
            
            conversion_jobs = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                with st.container():
                    file_col1, file_col2, file_col3 = st.columns([2, 1, 1])
                    
                    with file_col1:
                        file_type = get_file_type(uploaded_file.name)
                        file_size = uploaded_file.size / (1024 * 1024)  # Size in MB
                        
                        st.write(f"**{uploaded_file.name}**")
                        st.write(f"Size: {file_size:.2f} MB | Type: {file_type}")
                        
                        # Validate file
                        size_valid, size_msg = validate_file_size(uploaded_file.size, file_type)
                        type_valid, type_msg = validate_file_type(uploaded_file.name)
                        
                        if not size_valid:
                            st.error(size_msg)
                            continue
                        if not type_valid:
                            st.error(type_msg)
                            continue
                    
                    with file_col2:
                        # Get supported output formats
                        supported_formats = get_supported_formats(file_type)
                        
                        if supported_formats:
                            output_format = st.selectbox(
                                "Output format",
                                supported_formats,
                                key=f"format_{i}"
                            )
                        else:
                            st.error("Unsupported file type")
                            continue
                    
                    with file_col3:
                        if st.button(f"Convert", key=f"convert_{i}"):
                            conversion_jobs.append({
                                'file': uploaded_file,
                                'output_format': output_format,
                                'file_type': file_type
                            })
                    
                    st.divider()
            
            # Process conversion jobs
            if conversion_jobs:
                process_conversions(conversion_jobs)
    
    with col2:
        st.header("📥 Download Center")
        
        if st.session_state.converted_files:
            st.success(f"✅ {len(st.session_state.converted_files)} file(s) ready for download")
            
            # Option to download all as ZIP
            if len(st.session_state.converted_files) > 1:
                if st.button("📦 Download All as ZIP"):
                    zip_data = create_zip_archive(st.session_state.converted_files)
                    st.download_button(
                        label="⬇️ Download ZIP Archive",
                        data=zip_data,
                        file_name=f"converted_files_{int(time.time())}.zip",
                        mime="application/zip"
                    )
            
            # Individual download buttons
            st.subheader("Individual Downloads")
            for file_info in st.session_state.converted_files:
                st.download_button(
                    label=f"⬇️ {file_info['filename']}",
                    data=file_info['data'],
                    file_name=file_info['filename'],
                    mime=file_info['mime_type']
                )
        else:
            st.info("No converted files available")
        
        # Clear downloads button
        if st.session_state.converted_files:
            if st.button("🗑️ Clear Downloads"):
                st.session_state.converted_files = []
                st.rerun()

def process_conversions(conversion_jobs):
    """Process multiple conversion jobs with progress tracking"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_jobs = len(conversion_jobs)
    
    for i, job in enumerate(conversion_jobs):
        # Update progress
        progress = (i + 1) / total_jobs
        progress_bar.progress(progress)
        status_text.text(f"Converting {job['file'].name}... ({i + 1}/{total_jobs})")
        
        try:
            # Convert file based on type
            converted_data, output_filename, mime_type = convert_file(
                job['file'], 
                job['output_format'], 
                job['file_type']
            )
            
            if converted_data:
                # Add to converted files
                st.session_state.converted_files.append({
                    'filename': output_filename,
                    'data': converted_data,
                    'mime_type': mime_type
                })
                
                # Add to history
                st.session_state.conversion_history.append({
                    'original': job['file'].name,
                    'converted': output_filename,
                    'timestamp': time.time()
                })
            
        except Exception as e:
            st.error(f"❌ Failed to convert {job['file'].name}: {str(e)}")
    
    status_text.text("✅ All conversions completed!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()
    
    st.rerun()

def convert_file(uploaded_file, output_format, file_type):
    """Convert a single file to the specified format"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    
    try:
        # Choose converter based on file type
        if file_type == 'document':
            converter = DocumentConverter()
            result = converter.convert(tmp_file_path, output_format, uploaded_file.name)
        elif file_type == 'image':
            converter = ImageConverter()
            result = converter.convert(tmp_file_path, output_format, uploaded_file.name)
        elif file_type == 'audio':
            converter = AudioConverter()
            result = converter.convert(tmp_file_path, output_format, uploaded_file.name)
        elif file_type == 'video':
            converter = VideoConverter()
            result = converter.convert(tmp_file_path, output_format, uploaded_file.name)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return result
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

def create_zip_archive(converted_files):
    """Create a ZIP archive containing all converted files"""
    
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_info in converted_files:
            zip_file.writestr(file_info['filename'], file_info['data'])
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

if __name__ == "__main__":
    main()
