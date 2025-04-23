import os
import re
import sys
import config
from app.logger import get_logger

# Initialize logger for this module
logger = get_logger("process_srt")

def convert_srt_to_txt(srt_file_path, output_file_path=None, extract_text_only=None):
    """
    Convert an SRT file to a plain text file.

    Args:
        srt_file_path (str): Path to the SRT file
        output_file_path (str, optional): Path for the output TXT file.
                                          If not provided, will use the same name as the SRT file with .txt extension.
        extract_text_only (bool, optional): If True, only extract the text content without timestamps.
                                            If None, will use the value from config.py.
    """
    # Get configuration value if parameter is not provided
    srt2txt_config = config.get_config("processing", "srt2txt")
    if extract_text_only is None:
        extract_text_only = srt2txt_config.get("extract_text_only", True)
        
    remove_timestamps = srt2txt_config.get("remove_timestamps", True)
    combine_sentences = srt2txt_config.get("combine_sentences", True)

    logger.debug(f"Processing SRT file: {srt_file_path} with settings: extract_text_only={extract_text_only}, remove_timestamps={remove_timestamps}, combine_sentences={combine_sentences}")

    # Determine output file path
    if not output_file_path:
        output_file_path = os.path.splitext(srt_file_path)[0] + ".txt"
        logger.debug(f"No output path provided, using: {output_file_path}")

    try:
        logger.debug(f"Reading SRT file: {srt_file_path}")
        with open(srt_file_path, "r", encoding="utf-8") as srt_file:
            srt_content = srt_file.read()

        # Extract text content
        if extract_text_only:
            logger.debug("Extracting text content only (without timestamps)")
            # Regular expression to match SRT entries (index, timestamp, text)
            pattern = r"\d+\s*\n(\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3})\s*\n([\s\S]*?)(?=\n\s*\n\d+\s*\n|\Z)"
            
            # Find all matches
            matches = re.findall(pattern, srt_content)
            logger.debug(f"Found {len(matches)} subtitle segments")
            
            # Extract text from matches
            text_content = []
            for _, text in matches:
                # Clean up text (remove HTML, extra whitespace, etc.)
                cleaned_text = re.sub(r"<[^>]+>", "", text)  # Remove HTML tags
                cleaned_text = re.sub(r"\s+", " ", cleaned_text)  # Replace multiple spaces with a single space
                cleaned_text = cleaned_text.strip()
                
                if cleaned_text:
                    text_content.append(cleaned_text)
            
            # Combine into a single text file
            if combine_sentences:
                logger.debug("Combining segments into continuous text")
                output_content = " ".join(text_content)
            else:
                logger.debug("Keeping segments as separate lines")
                output_content = "\n".join(text_content)
        else:
            # Keep timestamps if extract_text_only is False
            logger.debug("Keeping full SRT content including timestamps")
            output_content = srt_content

        logger.debug(f"Writing output to: {output_file_path}")
        with open(output_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(output_content)

        logger.info(f"Successfully converted SRT to TXT: {srt_file_path} -> {output_file_path}")
        return output_file_path

    except Exception as e:
        logger.error(f"Error converting SRT to TXT: {str(e)}", exc_info=True)
        print(f"Error converting SRT to TXT: {e}")
        return None


def main():
    """
    Main function to handle command-line usage.
    """
    if len(sys.argv) < 2:
        logger.error("No input file provided when running as script")
        print("Usage: python process_srt.py <path_to_srt_file> [output_txt_file]")
        sys.exit(1)

    srt_file_path = sys.argv[1]
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(srt_file_path):
        logger.error(f"SRT file not found: {srt_file_path}")
        print(f"Error: SRT file '{srt_file_path}' not found.")
        sys.exit(1)

    logger.info(f"Converting SRT to TXT: {srt_file_path} -> {output_file_path or 'auto-generated'}")
    convert_srt_to_txt(srt_file_path, output_file_path)


if __name__ == "__main__":
    main()