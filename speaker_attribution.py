# app/speaker_attribution.py


import openai
from typing import List, Tuple
import nltk
nltk.download('punkt_tab', quiet=True)
from nltk.tokenize import sent_tokenize


def split_into_sentences_or_turns(text_chunk: str) -> List[str]:
    lines = sent_tokenize(text_chunk)
    lines = [line.strip() for line in lines if line.strip()]
    return lines


def initial_llm_labeling(text_lines: List[str]) -> List[Tuple[str, str]]:
    """
    FIRST PASS:
    We give the LLM a batch of lines.
    The LLM returns a guess: 'Therapist' or 'Client' for each line,
    focusing mostly on direct lexical cues.
    """
    # We'll build a single prompt that the LLM can parse at once, or
    # you could do line-by-line calls. Here, let's do a single call for all lines:

    # Build a user content block:
    lines_str = "\n".join(f"Line {i + 1}: {line}" for i, line in enumerate(text_lines))

    system_prompt = (
        """
You are an expert in analyzing therapeutic conversations with specialized knowledge in linguistic patterns. Your task is to identify whether each line is spoken by the Therapist or the Client without having extensive context yet.

Analyze these linguistic markers:
- Therapists typically: ask questions, use professional language, make reflective statements, provide guidance, explain processes
- Clients typically: share personal experiences, express emotions, respond to questions, describe problems, talk about relationships

Focus on sentence structure and content, not just keywords. Maintain conversation flow logic where questions are typically followed by answers.
"""
    )

    user_prompt = f"""
    Below are lines from a therapy conversation. Classify each line as either "Therapist" or "Client" based on linguistic patterns, speech style, and content.

    {lines_str}

    Instructions:
    1. Output your classification line-by-line in exactly this format:
       Therapist: [original text]
       or 
       Client: [original text]
    2. Use conversation flow to help (questions → answers, reflections → elaborations)
    3. Pay attention to personal disclosures (likely Client) versus professional guidance (likely Therapist)
    4. Make your best determination even if uncertain
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=1000
    )

    labeled_text = response["choices"][0]["message"]["content"].strip()

    # Now parse the output
    # We'll assume lines are: "Therapist: <text>" or "Client: <text>"
    # We'll do a simple parse approach:
    labeled_pairs = []
    for line in labeled_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("therapist:"):
            text_content = line.split(":", 1)[1].strip()
            labeled_pairs.append(("Therapist", text_content))
        elif line.lower().startswith("client:"):
            text_content = line.split(":", 1)[1].strip()
            labeled_pairs.append(("Client", text_content))
        else:
            # fallback
            labeled_pairs.append(("Unknown", line))

    return labeled_pairs


def refine_llm_labels(
        labeled_pairs: List[Tuple[str, str]]
) -> List[Tuple[str, str]]:
    """
    SECOND PASS:
    We refine/validate the labeled pairs with more context:
    - It's a medical/therapy transcript.
    - We have specific tokens/phrases that might indicate 'Therapist' or 'Client'.
    - We give the LLM instructions about known mental health disclaimers, typical questions, etc.

    The LLM then returns a final classification.
    """
    # Build a text block for the second pass:
    # We'll show the LLM what the first pass classification is,
    # and ask it to refine based on medical/therapy context.

    lines_str = ""
    for i, (speaker, content) in enumerate(labeled_pairs):
        lines_str += f"Line {i + 1} (First Pass: {speaker}): {content}\n"

    system_prompt = (
        """
You are a clinical documentation specialist with expertise in therapy transcripts. Your task is to refine speaker attributions with the knowledge that this is a therapeutic conversation.

Analysis guidelines:
1. Therapist indicators:
   - Mentions of confidentiality, session structure, or treatment processes
   - Open-ended exploratory questions or reflective listening statements
   - Professional language and clinical framing of issues
   - Brief statements aimed at clarification or validation
   - Explaining therapy procedures, boundaries, or recording purposes

2. Client indicators: 
   - Detailed personal narratives about life circumstances
   - Emotional self-disclosure and feelings
   - Descriptions of interpersonal relationships or conflicts
   - Expressions of stress, overwhelm, or challenges
   - Responses that directly answer therapist questions
   - Use of conversational fillers ("like", "you know") frequently

Maintain logical conversation flow where speakers typically alternate.
"""
    )

    user_prompt = f"""
    Review these previously classified lines from a therapy session and refine the speaker attributions.

    {lines_str}

    For each line:
    1. Evaluate if the first-pass attribution is correct based on therapeutic context
    2. Consider conversation flow and turn-taking patterns
    3. Check for specific therapist language (confidentiality discussions, professional questions) or client language (personal problems, emotional content)
    4. Pay special attention to:
       - Session introduction and structure explanations (typically Therapist)
       - Discussions of work/life balance, stress, or relationships (typically Client)
       - Reflective statements that rephrase what was just said (typically Therapist)

    Output your final classification in exactly this format:
    Therapist: [original text]
    Client: [original text]
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=1500
    )

    refined_text = response["choices"][0]["message"]["content"].strip()

    final_pairs = []
    for line in refined_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("therapist:"):
            text_content = line.split(":", 1)[1].strip()
            final_pairs.append(("Therapist", text_content))
        elif line.lower().startswith("client:"):
            text_content = line.split(":", 1)[1].strip()
            final_pairs.append(("Client", text_content))
        else:
            # fallback
            final_pairs.append(("Unknown", line))

    return final_pairs


def multi_step_speaker_attribution(text_chunk: str) -> List[Tuple[str, str]]:
    """
    Overall function to:
    1) Split the text into lines
    2) First-pass labeling with LLM
    3) Second-pass refinement with LLM
    Returns final list of (speaker, content).
    """
    lines = split_into_sentences_or_turns(text_chunk)
    first_pass = initial_llm_labeling(lines)
    refined = refine_llm_labels(first_pass)
    return refined
