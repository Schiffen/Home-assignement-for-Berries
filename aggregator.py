# app/aggregator.py

import openai
from typing import List


def aggregate_chunk_summaries_custom_structure(chunk_summaries: List[str]) -> str:
    """
    Takes multiple chunk summaries and merges them into a single structured therapy note.
    """
    # Combine your chunk summaries into one text block
    combined_text = "\n\n".join(
        f"Chunk {i + 1}:\n{summary}"
        for i, summary in enumerate(chunk_summaries)
    )

    # System prompt – clarifies the aggregator's role
    system_prompt = (
        "You are a specialized aggregator for therapy session notes. Your task is to create a structured therapy note "
        "that integrates information from multiple session summary chunks."

        "CRITICAL FORMATTING REQUIREMENTS:"
        "1. Every time you mention a client feeling, thought, or behavior, you MUST immediately follow with a supporting quote."
        "2. Format: 'The client expresses anxiety: \"I'm always worried about what might happen.\"'"
        "3. ALL quotes must be immediately adjacent to what they illustrate - NEVER group quotes at the end."
        "4. For the Plan section, create a clear numbered list (1., 2., 3., etc.), with each item on its own line."

        "Focus on clinical accuracy, eliminate redundancy, and maintain a professional tone suitable for mental health documentation."
    )

    # User prompt – requests the final structure
    user_prompt = f"""
Below are chunk summaries from a single therapy session:

{combined_text}

Create a comprehensive therapy note with these EXACT sections and formatting requirements:

Speech Therapy Note

Subjective
- Client's reported feelings, experiences, and background (150 words)
- IMMEDIATELY follow each feeling/thought with a supporting quote
- Example format: "The client feels overwhelmed: \"I'm just overwhelmed with work.\""
- Choose the most meaningful quotes that clearly illustrate key emotions

Objective
- Therapist observations, session details (150 words)
- Include psychological concepts with brief explanations
- Use supporting quotes to illustrate therapist observations
- Example: "Therapist observed anxiety patterns: \"I'm always afraid of not being able to handle everything.\""

Assessment
- Clinical impressions, themes, conceptualizations (150 words)
- Include client strengths/challenges with supporting quotes
- Place quotes directly after each assessment point

Plan
- Create a NUMBERED list (1., 2., 3., etc.)
- Each recommendation on its own line
- Include practical activities, resources, homework
- Format: "1. [Recommendation]" (new line) "2. [Next recommendation]"

CRITICAL REQUIREMENTS:
- Every client feeling MUST be immediately followed by a quote
- Quotes MUST be in double quotation marks
- ALLWAYS adress the Client and the Therapist as the Client and the Threapist, for example do not use "She" or "He" when speaking about the Client or the Therapist
- Plan items MUST be clearly numbered
- Total length: 550-650 words
- Select the most meaningful, representative quotes

Do NOT include any explanatory text or meta-commentary - return ONLY the formatted therapy note.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Upgraded to GPT-4 for better quality
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=1300  # Increased to ensure complete output
    )

    final_note = response["choices"][0]["message"]["content"].strip()
    return final_note

def final_aggregator_merge_two(note1: str, note2: str) -> str:
    """
    Merges two partial aggregator outputs into one final structured therapy note.
    We assume each partial note is already in your SOAP (or custom) format,
    and we want to produce a single, refined final version.

    We'll do a minimal LLM pass, removing duplicates or merging headings.
    """

    system_prompt = (
        "You are a final aggregator merging two partial therapy notes into a single, cohesive final note. "
        "Each partial note is already structured. Your job is to unify them into the headings: "
        "Speech Therapy Note, Subjective, Objective, Assessment, Plan. "
        "Eliminate redundancy, unify headings, and produce a final text that respects these new rules:\n"
        "1. Feelings/emotions from the client must be followed immediately by a short, logically connected client quote (max ~10 words), "
        "   e.g. The client feels anxious: \"I'm stressed out.\" "
        "2. Only use client quotes, never therapist quotes. If the therapist says something, paraphrase instead of quoting.\n"
        "3. For Subjective, Objective, Assessment sections: break lines every ~10–20 words where it makes sense, to improve readability.\n"
        "4. The Plan section must have exactly 5–8 plan items, each with ~5-10 extra words explaining why it's good for the future.\n"
        "5. Keep total length ~550-650 words.\n"
        "6. Do not keep duplicate or identical quotes.\n"
        "7. The final note is plain text, no HTML.\n"
    )

    user_prompt = f"""
We have two partial aggregator outputs:

PARTIAL NOTE #1:
{note1}

PARTIAL NOTE #2:
{note2}

Please merge them into ONE final therapy note that preserves the structure exactly:
Speech Therapy Note
Subjective - IMPORTANT IMPROVEMENTS FOR SUBJECTIVE:
- Client's reported feelings, experiences, and background (NEVER LESS THAN 150 words)
- IMMEDIATELY follow each feeling/thought with a supporting quote
- Example format: "The client feels overwhelmed: \"I'm just overwhelmed with work.\""
- Choose the most meaningful quotes that clearly illustrate key emotions

Objective - at least 120 words NEVER LESS, in this part AND MORE IMPORTANT IMPROVEMENTS:
- Therapist observations, session details (120 words) AND Use supporting quotes to illustrate therapist observations at least 2 quotes that are NEVER more that 7 words.
- Include psychological concepts with brief explanations
- Use supporting quotes to illustrate therapist observations
- Example: "Therapist observed anxiety patterns: \"I'm always afraid of not being able to handle everything.\""

Assessment - NEEDED IMPORTANT IMPROVEMENTS
- Clinical impressions, themes, conceptualizations (130 words)
- Include client strengths/challenges with supporting quotes
- Place quotes directly after each assessment point

Plan -
- Create a NUMBERED list (1., 2., 3., etc.) MAXIMUM 8 AND MINIMUM 5 PLANS
- Each recommendation on its own line
- Include practical activities, resources, homework
- Format: "1. [Recommendation]" (new line) "2. [Next recommendation]"


Additional improvements needed:
- Show paraphrases for therapist statements instead of quoting them.
- Insert a line break (~10–20 words) inside Subjective, Objective, and Assessment sections for readability.
- ALLWAYS adress the Client and the Therapist as the Client and the Threapist, for example do not use "She" or "He" when speaking about the Client or the Therapist
- Plan items: between 5 and 8 total. Each item a numbered line (1. 2. 3. etc.), and add 5–10 words about why that plan item is beneficial.
- Expand, using 5-8 words, on any psychological terms which describes the client and brought in the final_note if need more explanation on why he feels/thinking that way that appear in the final note (stress, guilt, overwhelm, validation, etc.).

Return ONLY the final text, do not add HTML or meta commentary.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",  # or GPT-4 if you prefer
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=1500
    )

    final_note = response["choices"][0]["message"]["content"].strip()
    return final_note
