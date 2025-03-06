# main.py

import os
from utils import load_transcript, openai_setup
from chunker import chunk_transcript_into_docs
from speaker_attribution import multi_step_speaker_attribution
from summarizer import summarize_speaker_pairs, fix_summary_with_critique
from quality_assessment import llm_evaluate_summary
from aggregator import (
    aggregate_chunk_summaries_custom_structure,
    final_aggregator_merge_two
)
from final_html_constructor import call_html_converter  # new "API"

def main():
    # Setup
    openai_setup()
    scores_list=[]
    total_score=0
    # Load transcript
    file_path = "Example_Transcript_for_Testing.txt"
    raw_text = load_transcript(file_path)

    # Chunk transcript
    docs = chunk_transcript_into_docs(raw_text, chunk_size=1500, chunk_overlap=120)

    chunk_summaries = []
    for i, doc in enumerate(docs):
        text_chunk = doc.page_content

        # Speaker attribution
        speaker_pairs = multi_step_speaker_attribution(text_chunk)

        # Summarize
        summary = summarize_speaker_pairs(speaker_pairs)
        print (summary)

        # Evaluate
        score, critique = llm_evaluate_summary(text_chunk, summary)
        print (score)
        if score < 85:
            # Attempt re-fix
            conversation_text = "\n".join(f"{spk}: {txt}" for (spk, txt) in speaker_pairs)
            fixed = fix_summary_with_critique(summary, critique, conversation_text)
            new_score, new_crit = llm_evaluate_summary(text_chunk, fixed)
            if new_score > score:
                summary = fixed
                print(f"SUCCESS IMPROVEMENT {new_score}")
                score=new_score
        total_score=total_score+score
        scores_list.append(score)
        chunk_summaries.append(summary)

    # Now we do the multi aggregator approach:
    # 1) aggregator pass on the first half
    # 2) aggregator pass on the second half
    # 3) final aggregator merges them

    n = len(chunk_summaries)
    mid = n // 2
    first_half = chunk_summaries[:mid]
    second_half = chunk_summaries[mid:]
    average_score=total_score/n
    # aggregator #1
    partial_note_1 = aggregate_chunk_summaries_custom_structure(first_half)

    # aggregator #2
    partial_note_2 = aggregate_chunk_summaries_custom_structure(second_half)

    # final aggregator merges partial notes
    final_text_note = final_aggregator_merge_two(partial_note_1, partial_note_2)

    # Instead of local convert, we call the "API"
    final_html = call_html_converter(final_text_note)

    # Save result
    with open("final_therapy_note.html", "w", encoding="utf-8") as f:
        f.write(final_html)

    print("[INFO] Done! Final therapy note saved to final_therapy_note.html")


if __name__ == "__main__":
    main()
