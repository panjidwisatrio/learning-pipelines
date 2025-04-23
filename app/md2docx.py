#!/usr/bin/env python3
import sys
import os
import argparse
import pypandoc
import config
from app.logger import get_logger

# Initialize logger for this module
logger = get_logger("md2docx")

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

    # Determine output file path
    if not output_docx_path:
        output_docx_path = os.path.splitext(md_file_path)[0] + ".docx"
        logger.debug(f"No output path provided, using: {output_docx_path}")

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
            
        if template_file and os.path.exists(template_file):
            logger.debug(f"Using custom template file: {template_file}")
            extra_args.append(f'--reference-doc={template_file}')

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
        logger.error(f"Error converting MD to DOCX: {str(e)}", exc_info=True)
        print(f"Error converting MD to DOCX: {e}")
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
