# app/summarizer.py

import openai
from typing import List, Tuple

def summarize_speaker_pairs(speaker_pairs: List[Tuple[str, str]]) -> str:
    """
    Takes a list of (speaker, text) from the final speaker attribution step,
    and uses a refined prompt to produce a clinically relevant summary.
    """

    labeled_conversation = "\n".join(f"{speaker}: {text}" for (speaker, text) in speaker_pairs)

    system_prompt = (
        """
You are a highly skilled clinical documentation assistant specializing in summarizing therapy transcript segments. Your task is to extract key clinical information while preserving therapeutic context and significance.

CRITICAL REQUIREMENT: Every time you mention a client's feeling, thought, or experience, you MUST immediately follow it with a relevant direct quote from the transcript. For example:
- Incorrect: "The client feels overwhelmed with work responsibilities." (Quote missing)
- Correct: "The client feels overwhelmed with work responsibilities: "I'm just overwhelmed with work. I have a lot going on.""

You must identify and prioritize:
1. Primary presenting concerns and emotional states (each with a supporting quote)
2. Significant interpersonal relationships and dynamics
3. Patterns in client thinking, feeling, and behavior
4. Relevant history or contextual factors
5. Therapist interventions and client responses
6. Any risk indicators or safety concerns
7. Progress indicators or barriers to change
8. Treatment planning elements or homework

Create summaries that maintain clinical accuracy while eliminating redundancy. Use professional language consistent with mental health documentation standards.
"""
    )

    user_prompt = f"""
Below is a segment from a therapy session transcript with speaker labels:

{labeled_conversation}

Create a concise clinical summary that:
1. Identifies the most significant clinical information
2. Highlights key emotional content and cognitive patterns
3. Notes important interpersonal dynamics discussed
4. Includes relevant quotes from the client (use " " for direct quotes)
5. Mentions therapist approaches or interventions
6. Flags any risk factors or safety concerns immediately

FORMAT REQUIREMENT:
- Every time you mention a client feeling, thought, or behavior, you MUST immediately follow it with a supporting quote from the transcript.
- Example: "The client expresses feeling overwhelmed by work demands: "I'm just overwhelmed with work. I have a lot going on.""
- NEVER group quotes at the end of paragraphs or sections.
-NEVER write twice the same quote in the same summary.

Format your summary to include:
- Main clinical themes (1-2 bullet points)
- Brief narrative summary (70-100 words) with quotes or appropriate sub_quotes integrated directly after each key point.
- Each quote brought will be max 10 words, NEVER more
- 1-2 Important contextual factors
- 1-2 Next steps or focus areas

Choose the 1 most meaningful and representative quotes that clearly illustrate the client's key feelings, thoughts, and challenges.
NEVER MORE THAN 480 tokens!! 
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Upgraded to GPT-4 for better quote selection and placement
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=600
    )

    summary_text = response["choices"][0]["message"]["content"].strip()
    return summary_text

def fix_summary_with_critique(original_summary: str, critique: str, conversation_text: str) -> str:
    """
    Use the critique to fix or improve the summary.
    We show the original chunk text again to ensure the LLM can incorporate missing details.
    """
    system_prompt = (
        "You are a therapy note improvement specialist. Your task is to fix a summary that didn't meet quality standards."
        "Your improvements must address all critique points while maintaining clinical accuracy."
        "CRITICALLY IMPORTANT: Every client feeling, thought, or behavior MUST be immediately followed by a supporting quote."
    )

    user_prompt = f"""
I need you to fix this therapy session summary that didn't meet our quality threshold.

Original Summary:
{original_summary}

Critique of Issues:
{critique}

Original Conversation (for reference):
{conversation_text}

Your task is to create an IMPROVED version that addresses ALL issues in the critique while following these STRICT requirements:

1. CRITICAL: Every time you mention a client feeling, thought, or experience, you MUST immediately follow it with a relevant direct quote. Format: "Client feels X: "direct quote here""

2. Choose the most meaningful quotes that clearly illustrate the client's emotional state and challenges.

3. Add any important clinical information missing from the original summary.

4. Remove redundancies while preserving all key clinical insights.

5. Make sure to maintain this structure:
   - Main clinical themes (bullet points)
   - Narrative summary with integrated quotes
   - 1-2 Important contextual factors
   - 1-2 Next steps

The improved summary should be clinically precise, include more meaningful quotes, and fix ALL issues mentioned in the critique.
NEVER MORE THAN 480 tokens!! 
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Using GPT-4 for more accurate improvement
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=700  # Increased for more comprehensive improvement
    )

    revised_summary = response["choices"][0]["message"]["content"].strip()
    return revised_summary