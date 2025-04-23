import os
import re
import sys
import config

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

    # Determine output file path
    if not output_file_path:
        output_file_path = os.path.splitext(srt_file_path)[0] + ".txt"

    try:
        with open(srt_file_path, "r", encoding="utf-8") as srt_file:
            srt_content = srt_file.read()

        # Extract text content
        if extract_text_only:
            # Regular expression to match SRT entries (index, timestamp, text)
            pattern = r"\d+\s*\n(\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3})\s*\n([\s\S]*?)(?=\n\s*\n\d+\s*\n|\Z)"
            
            # Find all matches
            matches = re.findall(pattern, srt_content)
            
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
                output_content = " ".join(text_content)
            else:
                output_content = "\n".join(text_content)
        else:
            # Keep timestamps if extract_text_only is False
            output_content = srt_content

        with open(output_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(output_content)

        return output_file_path

    except Exception as e:
        print(f"Error converting SRT to TXT: {e}")
        return None


def main():
    """
    Main function to handle command-line usage.
    """
    if len(sys.argv) < 2:
        print("Usage: python process_srt.py <path_to_srt_file> [output_txt_file]")
        sys.exit(1)

    srt_file_path = sys.argv[1]
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(srt_file_path):
        print(f"Error: SRT file '{srt_file_path}' not found.")
        sys.exit(1)

    convert_srt_to_txt(srt_file_path, output_file_path)


if __name__ == "__main__":
    main()