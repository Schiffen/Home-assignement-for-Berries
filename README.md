# Home-assignement-for-Berries
# Therapy Note Generator

A comprehensive system for processing therapy session transcripts into structured clinical notes with intelligent formatting and quote integration.

## Overview

This program converts raw therapy session transcripts into structured therapy notes following the SOAP format (Subjective, Objective, Assessment, Plan) with a focus on capturing client quotes and clinical insights. The system uses a two-stage aggregation process and smart line breaking for enhanced readability.

## Features

- **Accurate Speaker Attribution**: Distinguishes between therapist and client statements using AI
- **Intelligent Summarization**: Extracts key clinical information while maintaining context
- **Quote Integration**: Places client quotes directly after the relevant feelings/thoughts they illustrate
- **Two-Stage Aggregation**: Processes the session in halves before final merging for better context handling
- **Smart Line Breaking**: Adds line breaks at natural thought boundaries for improved readability
- **Professional Formatting**: Creates clean HTML therapy notes with proper styling and structure

## Requirements

- Python 3.7+
- OpenAI API key
- Required Python packages:
  - openai
  - langchain
  - nltk

## File Structure

- `main.py`: Main script that orchestrates the entire process
- `chunker.py`: Splits transcript into manageable chunks
- `speaker_attribution.py`: Identifies speaker roles (therapist vs client)
- `summarizer.py`: Summarizes each chunk with integrated client quotes
- `quality_assessment.py`: Evaluates summary quality and provides feedback
- `aggregator.py`: Contains functions for first-level and final aggregation
- `final_html_constructor.py`: Converts structured text to HTML with line breaks
- `utils.py`: Utility functions including API setup and file handling

## How It Works

1. **Chunking**: The transcript is divided into manageable segments
2. **Speaker Attribution**: Each line is classified as either therapist or client
3. **Chunk Summarization**: Each chunk is summarized with key clinical information
4. **Quality Assessment**: Summaries are evaluated and improved if needed
5. **First-Level Aggregation**: Session halves are processed separately
   - First half chunks → First partial note
   - Second half chunks → Second partial note
6. **Final Aggregation**: The two partial notes are merged into one cohesive note
7. **HTML Conversion**: The final note is formatted with intelligent line breaks

## Usage

1. Set your OpenAI API key in `utils.py` or as an environment variable
2. Place your transcript file in the project directory
3. Run the main script:
```
python main.py
```
4. Find the generated therapy note in `final_therapy_note.html`

## Customization

### Changing the Input Transcript

In `main.py`, modify the file path:
```python
file_path = "Your_Transcript_File.txt"
```

### Adjusting Chunk Size

To process longer or shorter sections, modify:
```python
docs = chunk_transcript_into_docs(raw_text, chunk_size=1500, chunk_overlap=120)
```

### Modifying Quality Threshold

Change the minimum quality score for summaries:
```python
if score < 85:  # Change this value
```

### Adjusting Line Breaks

The line breaking logic can be customized in `final_html_constructor.py` by modifying the `add_smart_line_breaks` function.

## HTML Output Format

The final HTML includes:

1. **Title**: "Speech Therapy Note"
2. **Subjective Section**: Client's reported feelings/experiences with integrated quotes
3. **Objective Section**: Therapist's observations and session details
4. **Assessment Section**: Clinical impressions and conceptualizations
5. **Plan Section**: Numbered recommendations and next steps

## Troubleshooting

- **Empty HTML Output**: Check the quality assessment scores to ensure summaries meet the threshold
- **Missing Quotes**: Verify your transcript contains clear client statements to extract
- **API Errors**: Confirm your OpenAI API key is valid and has sufficient credits

## Future Improvements

- Support for additional note formats beyond SOAP
- Multi-session analysis for tracking progress
- Integration with electronic health record systems
- Custom styling options for HTML output
