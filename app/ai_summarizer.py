import argparse
import os
import sys
from openai import OpenAI
import config

# Initialize OpenAI client with configuration from config.py
client = OpenAI(
    base_url=config.openai_config.get("base_url"),
    api_key=config.openai_config.get("api_key")
)
model = config.openai_config.get("model")
temperature = config.openai_config.get("temperature")


def chat_with_qwen(messages):
    completion = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
    )
    return completion.choices[0].message.content.strip()


def extract_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def get_all_file(file_path):
    all_files = []
    if os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            for file in files:
                if file.endswith(".txt"):
                    all_files.append(os.path.join(root, file))
    elif os.path.isfile(file_path) and file_path.endswith(".txt"):
        all_files.append(file_path)

    return all_files


def summarize_text(text):
    prompt_system = (
        "You are an expert video content analyst and summarizer. "
        "Your task is to create comprehensive, structured summaries of video transcripts that capture the full essence and value of the content."
        "\n\nFormat your entire response using proper Markdown syntax:\n"
        "- Use # for the main document title\n"
        "- Use ## for major sections (e.g., Overview, Key Points, Video Sections)\n"
        "- Use ### for subsections (e.g., specific video segment titles)\n"
        "- Use bullet points (*, -) for list items\n"
        "- Use numbered lists (1., 2., etc.) for next steps or call-to-action\n"
        "- Use **bold** for emphasis on important terms\n"
        "- Use > for quotes or notable remarks\n"
        "- Use horizontal rules (---) to visually divide major parts of the document\n"
        "\nFollow this specific structure strictly:\n"
        "# Comprehensive Summary of the Video: _[Video Title]_\n"
        "\n## Overview\n"
        "- Provide a brief summary of the video’s purpose and why it matters.\n"
        "\n## Key Points\n"
        "- Bullet key takeaways (3–5 main points).\n"
        "\n## Video Sections\n"
        "### 1. [First Section Title]\n"
        "- Explain the main idea.\n"
        "- Give examples, benefits, or applications if applicable.\n"
        "### 2. [Second Section Title]\n"
        "- Provide a breakdown of steps, explanations, or highlights.\n"
        "### 3. [Third Section Title]\n"
        "- Clarify purpose and how to apply it.\n"
        "\n## Conclusion and Takeaways\n"
        "- Reiterate the core message.\n"
        "- Include a 'Call to Action' with 2–3 practical follow-ups.\n"
        "\n## Additional Thoughts\n"
        "- Add reflections, subtle insights, or presenter’s non-obvious points.\n"
        "\n## Next Steps\n"
        "1. [First follow-up action]\n"
        "2. [Second follow-up action]\n"
        "3. [Third follow-up action]\n"
        "\nEnsure your summary is informative, clear, and reader-friendly when rendered in Markdown."
    )

    prompt_user = (
        "Please create a comprehensive summary of the following video transcript:\n\n"
        f"{text}\n\n"
        "In your summary:\n"
        "1. Start with a brief overview of the video (topic, purpose, and main ideas)\n"
        "2. Divide the content into logical sections\n"
        "3. For each section:\n"
        "    - Summarize key points and insights\n"
        "    - For tutorials, provide clear step-by-step instructions\n"
        "    - Include important details, tips, and warnings\n"
        "    - Use bullet points or numbered lists for clarity\n"
        "4. Conclude with:\n"
        "    - The overall message or takeaway\n"
        "    - Any recommended resources or links\n"
        "    - Any call to action from the creator\n"
        "5. Add brief additional context that might help the reader\n\n"
        "Format your summary with clear headings, bullet points, and organized structure for maximum readability.\n\n"
        "Summary:"
    )

    messages = [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": prompt_user},
    ]
    summary = chat_with_qwen(messages)
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Summarize video transcripts from .txt files."
    )
    parser.add_argument(
        "-i", "--input", help="Path to the .txt file or directory containing .txt files"
    )
    args = parser.parse_args()
    input_path = args.input

    try:
        if not input_path:
            raise ValueError("Input path is required.")

        files = get_all_file(input_path)

        if not files:
            print(f"No .txt files found in {input_path}.")
            return

        for file in files:
            print(f"Processing {file}...")
            text = extract_text(file)
            summary = summarize_text(text)
            summary = summary.strip()

            # Save the summary to a new file
            summary_file = os.path.splitext(file)[0] + ".md"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)

            print(f"Summary saved to {summary_file}.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
