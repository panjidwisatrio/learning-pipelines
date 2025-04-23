#!/usr/bin/env python3
import argparse
import os
import sys
from app.process_srt import convert_srt_to_txt
from app.ai_summarizer import summarize_text, extract_text, get_all_file
from app.md2docx import convert_md_to_docx
from app.generate_srt import transcribe_to_srt
from app.logger import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
import config

# Initialize console with custom theme from config
console = Console(theme=config.get_ui_theme())

def convert_srt_to_txt_files(input_path, output_dir=None):
    """Convert SRT files to TXT files.

    Args:
        input_path (str): Path to a file or directory containing SRT files
        output_dir (str): Optional output directory for TXT files

    Returns:
        list: Paths to the generated TXT files
    """
    txt_files = []

    logger.info("Starting SRT to TXT conversion")
    console.print(Panel("[bold cyan]CONVERTING SRT TO TXT[/bold cyan]", border_style="cyan"))
    if os.path.isdir(input_path):
        # Process all SRT files in directory
        srt_files = []
        video_files = []
        
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(".srt"):
                    srt_path = os.path.join(root, file)
                    srt_files.append(srt_path)
                elif file.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                    video_path = os.path.join(root, file)
                    video_files.append(video_path)

        if not srt_files:
            if video_files:
                logger.info(f"No SRT files found, but {len(video_files)} video files detected. Generating SRT files...")
                console.print("[warning]No SRT files found, but video files detected. Generating SRT files...[/warning]")
                
                # Generate SRT files from video files
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console
                ) as progress:
                    transcribe_task = progress.add_task("[highlight]Transcribing videos...[/highlight]", total=len(video_files))
                    
                    for video_file in video_files:
                        logger.debug(f"Transcribing video: {video_file}")
                        progress.update(transcribe_task, description=f"[highlight]Transcribing: {os.path.basename(video_file)}[/highlight]")
                        transcribe_to_srt(video_file)
                        srt_path = os.path.splitext(video_file)[0] + ".srt"
                        srt_files.append(srt_path)
                        progress.update(transcribe_task, advance=1)
            else:
                logger.error("No SRT or video files found in the specified directory")
                console.print("[error]No SRT or video files found in the specified directory.[/error]")
                return []

        logger.info(f"Converting {len(srt_files)} SRT files to TXT")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            convert_task = progress.add_task("[highlight]Converting SRT files to TXT...[/highlight]", total=len(srt_files))
            
            for srt_file in srt_files:
                # Determine output path for the text file
                if output_dir:
                    rel_path = os.path.relpath(srt_file, input_path)
                    txt_path = os.path.join(
                        output_dir, os.path.splitext(rel_path)[0] + ".txt"
                    )
                    os.makedirs(os.path.dirname(txt_path), exist_ok=True)
                else:
                    txt_path = os.path.splitext(srt_file)[0] + ".txt"

                # Convert the SRT file to TXT
                logger.debug(f"Converting: {srt_file} to {txt_path}")
                progress.update(convert_task, description=f"[highlight]Converting: {os.path.basename(srt_file)}[/highlight]")
                convert_srt_to_txt(srt_file, extract_text_only=True)
                txt_files.append(txt_path)
                progress.update(convert_task, advance=1)
    elif input_path.lower().endswith(".srt"):
        # Process a single SRT file
        if output_dir:
            base_name = os.path.basename(input_path)
            txt_path = os.path.join(output_dir, os.path.splitext(base_name)[0] + ".txt")
        else:
            txt_path = os.path.splitext(input_path)[0] + ".txt"

        logger.info(f"Converting single SRT file: {input_path}")
        with console.status(f"[highlight]Converting {os.path.basename(input_path)} to TXT...[/highlight]", spinner="dots"):
            convert_srt_to_txt(input_path, extract_text_only=True)
            txt_files.append(txt_path)
        console.print(f"[success]✓ Converted: {os.path.basename(input_path)}[/success]")
        logger.info(f"Successfully converted {input_path} to {txt_path}")
    else:
        logger.error(f"Input is not an SRT file or a directory containing SRT files: {input_path}")
        console.print("[error]Input is not an SRT file or a directory containing SRT files.[/error]")

    return txt_files


def summarize_txt_to_md(txt_files, input_path, output_dir=None):
    """Summarize TXT files to MD files.

    Args:
        txt_files (list): List of TXT files to summarize
        input_path (str): Original input path (for relative path calculations)
        output_dir (str): Optional output directory for MD files

    Returns:
        list: Paths to the generated MD files
    """
    md_files = []

    logger.info("Starting TXT to MD summarization")
    console.print(Panel("[bold cyan]SUMMARIZING TXT TO MD[/bold cyan]", border_style="cyan"))
    if not txt_files:
        logger.debug(f"No TXT files provided, searching in: {input_path}")
        txt_files = get_all_file(input_path)

    if not txt_files:
        logger.warning("No TXT files found to summarize")
        console.print("[warning]No TXT files found to summarize.[/warning]")
    else:
        logger.info(f"Summarizing {len(txt_files)} TXT files to MD")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            summarize_task = progress.add_task("[highlight]Summarizing TXT files...[/highlight]", total=len(txt_files))
            
            for txt_file in txt_files:
                logger.debug(f"Summarizing: {txt_file}")
                progress.update(summarize_task, description=f"[highlight]Summarizing: {os.path.basename(txt_file)}[/highlight]")
                text = extract_text(txt_file)
                summary = summarize_text(text)

                # Determine output path for the MD file
                if output_dir:
                    rel_path = (
                        os.path.relpath(txt_file, input_path)
                        if os.path.isdir(input_path)
                        else os.path.basename(txt_file)
                    )
                    md_path = os.path.join(
                        output_dir, os.path.splitext(rel_path)[0] + ".md"
                    )
                    os.makedirs(os.path.dirname(md_path), exist_ok=True)
                else:
                    md_path = os.path.splitext(txt_file)[0] + ".md"

                # Save the summary to a new MD file
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                
                logger.debug(f"Created MD file: {md_path}")
                md_files.append(md_path)
                progress.update(summarize_task, advance=1)

    return md_files


def convert_md_to_docx_files(md_files, input_path, output_dir=None):
    """Convert MD files to DOCX files.

    Args:
        md_files (list): List of MD files to convert
        input_path (str): Original input path (for relative path calculations)
        output_dir (str): Optional output directory for DOCX files
    """
    logger.info("Starting MD to DOCX conversion")
    console.print(Panel("[bold cyan]CONVERTING MD TO DOCX[/bold cyan]", border_style="cyan"))
    # If no md_files provided, find them from input
    if not md_files:
        logger.debug(f"No MD files provided, searching in: {input_path}")
        if os.path.isdir(input_path):
            md_files = []
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith(".md"):
                        md_path = os.path.join(root, file)
                        md_files.append(md_path)
        elif input_path.lower().endswith(".md"):
            md_files = [input_path]

    if not md_files:
        logger.warning("No MD files found to convert to DOCX")
        console.print("[warning]No MD files found to convert to DOCX.[/warning]")
    else:
        # check and setup pandoc
        try:
            import pypandoc
            try:
                version = pypandoc.get_pandoc_version()
                logger.info(f"Using pypandoc version: {version}")
                console.print(f"[info]Using pypandoc version: {version}[/info]")
            except OSError:
                logger.warning("Pandoc is not installed. Attempting to install it...")
                console.print("[warning]Pandoc is not installed. Attempting to install it...[/warning]")
                try:
                    with console.status("[highlight]Installing Pandoc...[/highlight]", spinner="dots"):
                        pypandoc.download_pandoc()
                    logger.info("Pandoc installed successfully")
                    console.print("[success]Pandoc installed successfully.[/success]")
                except Exception as e:
                    logger.error(f"Error installing Pandoc: {str(e)}")
                    console.print(f"[error]Error installing Pandoc: {e}[/error]")
                    console.print("[info]Please install Pandoc manually:[/info]")
                    console.print("  - Windows: https://pandoc.org/installing.html")
                    console.print("  - Linux: sudo apt install pandoc")
                    console.print("  - Mac: brew install pandoc")
                    return
        except ImportError:
            logger.error("pypandoc is not installed")
            console.print("[error]pypandoc is not installed. Please install it with 'pip install pypandoc'.[/error]")
            return
        
        logger.info(f"Converting {len(md_files)} MD files to DOCX")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            convert_task = progress.add_task("[highlight]Converting MD files to DOCX...[/highlight]", total=len(md_files))
            
            for md_file in md_files:
                # Determine output path for the DOCX file
                if output_dir:
                    rel_path = (
                        os.path.relpath(md_file, input_path)
                        if os.path.isdir(input_path)
                        else os.path.basename(md_file)
                    )
                    docx_path = os.path.join(
                        output_dir, os.path.splitext(rel_path)[0] + ".docx"
                    )
                    os.makedirs(os.path.dirname(docx_path), exist_ok=True)
                else:
                    docx_path = os.path.splitext(md_file)[0] + ".docx"

                # Convert the MD file to DOCX
                logger.debug(f"Converting MD to DOCX: {md_file} -> {docx_path}")
                progress.update(convert_task, description=f"[highlight]Converting: {os.path.basename(md_file)}[/highlight]")
                try:
                    convert_md_to_docx(md_file, docx_path)
                    logger.debug(f"Successfully converted to DOCX: {docx_path}")
                    progress.update(convert_task, advance=1)
                except Exception as e:
                    logger.error(f"Error converting {md_file} to DOCX: {str(e)}")
                    progress.update(convert_task, advance=1)
                    console.print(f"[error]Error converting {os.path.basename(md_file)} to DOCX: {e}[/error]")


def process_files(input_path, steps, output_dir=None):
    """
    Process files through a pipeline of operations: SRT -> TXT -> MD -> DOCX

    Args:
        input_path (str): Path to a file or directory
        steps (list): List of processing steps to apply ('srt2txt', 'txt2md', 'md2docx', or 'all')
        output_dir (str): Optional output directory for results
    """
    logger.info(f"Starting pipeline with input: {input_path}, steps: {steps}, output: {output_dir or 'Same as input'}")
    
    # Create output directory if specified and doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
        console.print(f"[info]Created output directory: {output_dir}[/info]")

    # Display pipeline information
    console.print(Panel.fit(
        Text("LinkedIn Learning Pipeline", style="bold cyan"),
        subtitle=Text(f"Input: {input_path} | Output: {output_dir or 'Same as input'}", style="yellow"),
        border_style="cyan"
    ))
    
    # Show selected steps
    process_all = "all" in steps
    if process_all:
        logger.info("Processing full pipeline: SRT → TXT → MD → DOCX")
        console.print("[info]Processing full pipeline: SRT → TXT → MD → DOCX[/info]")
    else:
        steps_desc = " → ".join([s.upper() for s in steps])
        logger.info(f"Processing selected steps: {steps_desc}")
        console.print(f"[info]Processing selected steps: {steps_desc}[/info]")

    # Initialize file lists
    txt_files = []
    md_files = []

    # Step 1: Convert SRT to TXT if needed
    if process_all or "srt2txt" in steps:
        txt_files = convert_srt_to_txt_files(input_path, output_dir)

    # Step 2: Summarize TXT to MD if needed
    if process_all or "txt2md" in steps:
        md_files = summarize_txt_to_md(txt_files, input_path, output_dir)

    # Step 3: Convert MD to DOCX if needed
    if process_all or "md2docx" in steps:
        convert_md_to_docx_files(md_files, input_path, output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Process video subtitle files through a pipeline: SRT -> TXT -> MD -> DOCX"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input file or directory"
    )
    parser.add_argument(
        "-o", "--output", help="Optional output directory for processed files"
    )
    parser.add_argument(
        "-s",
        "--steps",
        default="all",
        choices=["srt2txt", "txt2md", "md2docx", "all"],
        nargs="+",
        help="Processing steps to perform (default: all)",
    )

    args = parser.parse_args()

    try:
        logger.info("LinkedIn Learning Pipeline started")
        process_files(args.input, args.steps, args.output)
        logger.info("Pipeline execution completed successfully")
        console.print(Panel("[success]Processing completed successfully![/success]", border_style="green"))
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        console.print(Panel(f"[error]Error: {e}[/error]", title="Error", border_style="red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
