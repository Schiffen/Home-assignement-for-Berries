# final_html_constructor.py

import re


def call_html_converter(final_text):
    """
    Converts therapy notes to HTML with smart line breaks.
    """
    # Extract all sections from the text
    sections = {}
    current_section = None
    section_content = []

    # Process each line
    for line in final_text.splitlines():
        line_stripped = line.strip()

        if line_stripped in ["Speech Therapy Note", "Subjective", "Objective", "Assessment", "Plan"]:
            # Save previous section if it exists
            if current_section:
                sections[current_section] = "\n".join(section_content)
                section_content = []

            current_section = line_stripped
        elif current_section:
            section_content.append(line)

    # Add the last section
    if current_section and section_content:
        sections[current_section] = "\n".join(section_content)

    # Build the HTML
    result = ["<html><body><pre>"]

    # Add title
    result.append("<b>Speech Therapy Note</b>")

    # Add each section
    for section in ["Subjective", "Objective", "Assessment", "Plan"]:
        if section in sections:
            # Add section header
            result.append("")
            result.append(f"<b>{section}</b>")
            content = sections[section].strip()

            if section == "Plan":
                # Plan section is treated differently (keep numbering)
                result.append(content)
            else:
                # Other sections get smart line breaking
                formatted = add_smart_line_breaks(content)
                result.append(formatted)

    # Finish the HTML
    result.append("</pre></body></html>")

    return "\n".join(result)


def add_smart_line_breaks(text):
    """
    Adds smart line breaks to therapy notes with improved handling for whitespace.
    """
    # Step 1: Bold all quotes first
    text_with_bold = re.sub(r'\"([^\"]+)\"', r'<b>"\1"</b>', text)

    # Step 2: Add line breaks after quotes followed by spaces and capital letters
    # This fixed regex specifically handles the case where spaces follow the </b> tag
    text_with_bold = re.sub(r'(</b>)(\s+)([A-HJ-Z])', r'\1\n\2\3', text_with_bold)

    # Step 3: Add line breaks before specific patterns that start new thoughts
    patterns = [
        r'The client ',
        r'They ',
        r'The therapist ',
        r'Client ',
        r'Therapist '
    ]

    # Process each pattern
    for pattern in patterns:
        # Don't add line break if pattern is at the start
        if text_with_bold.startswith(pattern):
            continue

        # Find all matches of the pattern
        matches = list(re.finditer(pattern, text_with_bold))

        # Process matches from end to start to avoid messing up positions
        for match in reversed(matches):
            start_pos = match.start()

            # Skip if the match is at the start of a line (after a newline)
            if start_pos > 0 and text_with_bold[start_pos - 1] == '\n':
                continue

            # Check if this match is inside bold tags
            text_before = text_with_bold[:start_pos]
            open_tags = text_before.count("<b>")
            close_tags = text_before.count("</b>")

            # If not in quotes, add a line break before this pattern
            if open_tags == close_tags:
                text_with_bold = (
                        text_with_bold[:start_pos] +
                        "\n" +
                        text_with_bold[start_pos:]
                )

    # Step 4: Split at existing line breaks, then add more at sentence boundaries
    output_lines = []

    for line in text_with_bold.splitlines():
        if not line.strip():
            continue

        # Split at sentence endings (period followed by space and capital letter)
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', line)

        for part in parts:
            if part.strip():
                output_lines.append(part.strip())

    return "\n".join(output_lines)

