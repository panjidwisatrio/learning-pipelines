#!/usr/bin/env python3
import sys
import os
import argparse
import pypandoc
import config
from pathlib import Path
from app.logger import get_logger

# Initialize logger for this module
logger = get_logger("md2docx")

# Security constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
ALLOWED_INPUT_EXTENSIONS = ['.md', '.markdown']
ALLOWED_OUTPUT_EXTENSIONS = ['.docx']
ALLOWED_TEMPLATE_EXTENSIONS = ['.docx']

def is_safe_path(base_dir, path, follow_symlinks=True):
    """
    Validate that path is within base_dir to prevent traversal attacks.
    
    Args:
        base_dir (str): The base directory that paths should be confined to
        path (str): The path to validate
        follow_symlinks (bool): Whether to resolve symbolic links
        
    Returns:
        bool: True if the path is safe (within base_dir), False otherwise
    """
    try:
        if follow_symlinks:
            base = Path(base_dir).resolve()
            target = Path(path).resolve()
        else:
            base = Path(base_dir)
            target = Path(path)
        
        # Check if target is within base or is base itself
        return base == target or base in target.parents
    except (ValueError, OSError):
        return False

def convert_md_to_docx(md_file_path, output_docx_path=None):
    """
    Convert a Markdown file to a DOCX file using pypandoc.

    Args:
        md_file_path (str): Path to the Markdown file
        output_docx_path (str, optional): Path for the output DOCX file.
                                          If not provided, will use the same name as the MD file with .docx extension.

    Returns:
        str: Path to the generated DOCX file, or None if conversion failed
    """
    # Get configuration options from config.py
    md2docx_config = config.get_config("processing", "md2docx")
    add_table_of_contents = md2docx_config.get("add_table_of_contents", True)
    add_page_numbers = md2docx_config.get("add_page_numbers", True)
    template_file = md2docx_config.get("template_file", "")

    logger.debug(f"MD to DOCX conversion settings: add_table_of_contents={add_table_of_contents}, add_page_numbers={add_page_numbers}, template_file={template_file or 'None'}")

    # Validate input path
    try:
        md_file_path = os.path.abspath(md_file_path)
        base_dir = os.getcwd()
        
        # Check for path traversal
        if not is_safe_path(base_dir, md_file_path):
            logger.error("Path traversal attempt detected in input file path")
            print("Error: Invalid file path")
            return None
        
        # Validate file extension
        file_ext = os.path.splitext(md_file_path)[1].lower()
        if file_ext not in ALLOWED_INPUT_EXTENSIONS:
            logger.error(f"Invalid input file extension: {file_ext}")
            print(f"Error: Only {', '.join(ALLOWED_INPUT_EXTENSIONS)} files are allowed")
            return None
        
        # Check if file exists
        if not os.path.exists(md_file_path):
            logger.error(f"Input file not found: {md_file_path}")
            print("Error: Input file not found")
            return None
        
        # Check file size
        file_size = os.path.getsize(md_file_path)
        if file_size > MAX_FILE_SIZE:
            logger.error(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            print(f"Error: File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)")
            return None
            
    except (ValueError, OSError) as e:
        logger.error(f"Error validating input file path: {str(e)}")
        print("Error: Invalid input file path")
        return None

    # Determine output file path
    if not output_docx_path:
        output_docx_path = os.path.splitext(md_file_path)[0] + ".docx"
        logger.debug(f"No output path provided, using: {output_docx_path}")
    
    # Validate output path
    try:
        output_docx_path = os.path.abspath(output_docx_path)
        
        # Check for path traversal
        if not is_safe_path(base_dir, output_docx_path):
            logger.error("Path traversal attempt detected in output file path")
            print("Error: Invalid output path")
            return None
        
        # Validate output file extension
        output_ext = os.path.splitext(output_docx_path)[1].lower()
        if output_ext not in ALLOWED_OUTPUT_EXTENSIONS:
            logger.error(f"Invalid output file extension: {output_ext}")
            print(f"Error: Only {', '.join(ALLOWED_OUTPUT_EXTENSIONS)} files are allowed for output")
            return None
            
    except (ValueError, OSError) as e:
        logger.error(f"Error validating output file path: {str(e)}")
        print("Error: Invalid output file path")
        return None

    try:
        import pypandoc

        # Set up pandoc arguments
        extra_args = []
        
        if add_table_of_contents:
            logger.debug("Adding table of contents to the document")
            extra_args.extend(['--toc', '--toc-depth=3'])
            
        if add_page_numbers:
            logger.debug("Adding page numbers to the document")
            extra_args.append('--variable=numbersections')
            
        # Validate template file if provided
        if template_file:
            try:
                template_file = os.path.abspath(template_file)
                
                # Check for path traversal
                if not is_safe_path(base_dir, template_file):
                    logger.error("Path traversal attempt detected in template file path")
                    template_file = ""
                # Validate template file extension
                elif os.path.splitext(template_file)[1].lower() not in ALLOWED_TEMPLATE_EXTENSIONS:
                    logger.error(f"Invalid template file extension: {os.path.splitext(template_file)[1]}")
                    template_file = ""
                # Check if template file exists
                elif not os.path.exists(template_file):
                    logger.warning(f"Template file not found: {template_file}")
                    template_file = ""
                else:
                    logger.debug(f"Using custom template file: {template_file}")
                    extra_args.append(f'--reference-doc={template_file}')
            except (ValueError, OSError) as e:
                logger.error(f"Error validating template file: {str(e)}")
                template_file = ""

        # Convert md to docx
        logger.info(f"Converting MD to DOCX: {md_file_path} -> {output_docx_path}")
        pypandoc.convert_file(
            md_file_path,
            'docx',
            outputfile=output_docx_path,
            extra_args=extra_args
        )
        
        logger.info(f"Successfully converted MD to DOCX: {output_docx_path}")
        return output_docx_path
        
    except ImportError:
        logger.error("pypandoc library is not installed")
        print("Error: pypandoc library is not installed. Install it with 'pip install pypandoc'")
        return None
    except Exception as e:
        logger.error(f"Error converting MD to DOCX: {str(e)}")
        print("Error: Conversion failed")
        return None

def main():
    """
    Main function to handle command-line usage.
    """
    if len(sys.argv) < 2:
        logger.error("No input file provided when running as script")
        print("Usage: python md2docx.py <path_to_md_file> [output_docx_file]")
        sys.exit(1)

    md_file_path = sys.argv[1]
    output_docx_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(md_file_path):
        logger.error(f"Markdown file not found: {md_file_path}")
        print(f"Error: Markdown file '{md_file_path}' not found.")
        sys.exit(1)

    logger.info(f"Starting MD to DOCX conversion: {md_file_path} -> {output_docx_path or 'auto-generated'}")
    convert_md_to_docx(md_file_path, output_docx_path)

if __name__ == "__main__":
    main()
