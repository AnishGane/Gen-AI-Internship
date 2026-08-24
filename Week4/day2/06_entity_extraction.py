"""
Extracting Structured Entities from Unstructured Text (via OpenRouter)

A practical, common use of structured output: pulling named entities (people, dates, action items) out of free-form text into a defined schema -- e.g. for processing meeting notes or support emails automatically instead of by hand.
"""

import os
import json
from typing import List
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

class MeetingDetails(BaseModel):
    attendees: List[str]
    date: str
    action_items: List[str]

NOTES = """
Quick sync between Priya, Jason, and Wei on Thursday to discuss the Q3
launch. Priya will finalize the marketing copy by Friday. Jason will
review the budget numbers before the next meeting. Wei is following up
with the vendor about pricing.
"""

def extract_meeting_details(notes_text):
    prompt = (
        f"Extract structured meeting details from these notes:\n\n{notes_text}\n\n"
        'Respond with ONLY this JSON shape: '
        '{"attendees": ["..."], "date": "...", "action_items": ["..."]}'
    )
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": "Respond with ONLY valid JSON, no other text, no markdown formatting."},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = response.choices[0].message.content
    try:
        raw_dict = json.loads(raw_text)
        print("===Raw dict: ===", raw_dict)
        return MeetingDetails(**raw_dict)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Extraction failed: {e}\nRaw text: {raw_text}")
        return None
    
if __name__ == "__main__":
    details = extract_meeting_details(NOTES)
    if details:
        print("Attendees:", details.attendees)
        print("Date:", details.date)
        print("Action items:")
        for item in details.action_items:
            print(" -", item)