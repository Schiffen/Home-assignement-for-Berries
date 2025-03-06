# quality_assessment.py

import openai
from typing import Tuple


def llm_evaluate_summary(chunk_text: str, summary_text: str) -> Tuple[int, str]:
    """
    Uses an LLM to evaluate how well 'summary_text' captures the main ideas
    from 'chunk_text'. Returns (score, critique).

    'chunk_text' is the raw conversation snippet or transcript chunk.
    'summary_text' is the chunk-level summary we produced.

    Score: integer 0-100
    Critique: short text describing what's missing / inaccurate.
    """

    system_prompt = (
        "You are an evaluator that compares a raw therapy conversation snippet to its summary. "
        "Your evaluation focuses on these key criteria:\n"
        "1. Completeness: Does the summary include all key clinical information?\n"
        "2. Quote Integration: Are client quotes included immediately after the relevant feelings/thoughts they illustrate?\n"
        "3. Clinical Relevance: Does the summary highlight therapeutically significant content?\n"
        "4. Structure & Clarity: Is the summary well-organized and clear?\n\n"
        "Provide a 0-100 numeric score and detailed critique focusing on these areas."
    )

    user_prompt = f"""
Below is the raw chunk of conversation (unlabeled or partially labeled). Then follows the summary.

Raw chunk text:
\"\"\"{chunk_text}\"\"\"

Summary produced:
\"\"\"{summary_text}\"\"\"

Evaluate the summary on these specific criteria:
1. COMPLETENESS: Does it capture all key information from the original text?
2. QUOTE INTEGRATION: Are quotes positioned immediately after the feelings/thoughts they illustrate?
3. CLINICAL RELEVANCE: Does it highlight clinically significant information?
4. STRUCTURE & CLARITY: Is it well-organized and easy to understand?

Provide:
1) An overall SCORE: <integer> from 0-100
2) A detailed CRITIQUE identifying specific issues that need improvement

Focus especially on:
- Whether quotes follow immediately after the client feelings/thoughts they illustrate
- Missing important clinical details
- The quality and relevance of selected quotes
- Treatment recommendations clarity

Format your response exactly as:
SCORE: [number]
CRITIQUE: [detailed feedback]
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",  # Using GPT-4 for better evaluation quality
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=800
    )

    eval_output = response["choices"][0]["message"]["content"].strip()

    # Parse the output lines using simple text parsing
    score = 50  # Default score if parsing fails
    critique = ""

    # Extract score from text
    for line in eval_output.split('\n'):
        line = line.strip()
        if line.upper().startswith("SCORE:"):
            try:
                score_text = line.split(":", 1)[1].strip()
                # Handle cases where score might have extra text
                score_text = ''.join(c for c in score_text if c.isdigit())
                if score_text:
                    score = int(score_text)
            except:
                score = 50
        elif line.upper().startswith("CRITIQUE:"):
            critique = line.split(":", 1)[1].strip()
            # Also capture multi-line critique
            critique_started = True
        elif 'critique_started' in locals() and critique_started and not line.upper().startswith("SCORE:"):
            # Append additional critique lines
            critique += " " + line

    # If we couldn't find a clearly marked critique section, use everything after SCORE:
    if not critique:
        try:
            score_index = eval_output.upper().find("SCORE:")
            if score_index >= 0:
                remaining_text = eval_output[score_index + 6:]  # Skip "SCORE:"
                critique_index = remaining_text.upper().find("CRITIQUE:")
                if critique_index >= 0:
                    critique = remaining_text[critique_index + 9:].strip()  # Skip "CRITIQUE:"
                else:
                    # If no CRITIQUE label, just use everything after the score line
                    next_line_index = remaining_text.find('\n')
                    if next_line_index >= 0:
                        critique = remaining_text[next_line_index:].strip()
        except:
            critique = "Error extracting critique from response."

    return (score, critique)