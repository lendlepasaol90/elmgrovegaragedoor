# JSON schemas

## services/<slug>.json  (must total >= 1,750 words across all string values counted by wc.py; aim 1,850-2,050)
{
 "slug": "<slug>",
 "name": "<nav name>",
 "category": "Service & Repair" | "Garage Doors" | "Garage Door Openers",
 "metaTitle": "<Service> in Elm Grove, WI | Same Day Service"   (<= 62 chars, vary wording per page),
 "metaDescription": "<= 158 chars, mentions Elm Grove, WI",
 "h1": "<Service> in Elm Grove, WI",
 "kicker": "2-4 words",
 "intro": "55-80 words",
 "highlights": [ {"label": "2-3 words", "value": "3-6 words"} x4 ],
 "sections": [  x4
   {"eyebrow": "2-4 words", "h2a": "first half of heading", "h2b": "second half (shown accented)",
    "paragraphs": ["90-125 words", "90-125 words", "90-125 words"],
    "bullets": ["4-8 words each" x6]   // bullets on sections index 0 and 2; [] on the others
   }
 ],
 "signsHeading": ["first half", "second half"],
 "signs": [ {"title": "3-6 words", "text": "40-55 words"} x6 ],
 "process": [ {"title": "2-5 words", "text": "40-55 words"} x4 ],
 "costFactors": [ {"title": "2-5 words", "text": "35-50 words"} x4 ],
 "localNote": {"title": "6-10 words, Elm Grove-specific", "text": "130-170 words tying this service to Elm Grove homes, trees, weather, streets"},
 "faqs": [ {"q": "question", "a": "60-85 words"} x6 ],
 "ctaTitle": "4-8 words",
 "ctaText": "25-40 words"
}

## home.json (must total >= 2,900 words by wc.py; aim 3,000-3,300)
{
 "heroKicker": "3-6 words",
 "heroIntro": "55-75 words",
 "intro": {"eyebrow": "...", "h2a": "...", "h2b": "...", "paragraphs": ["110-140 words" x4]},
 "servicesLead": "40-60 words",
 "problems": [ {"label": "2-3 words", "title": "3-6 words", "text": "70-90 words", "slug": "<service slug>"} x4 ],
 "fullwidth": {"eyebrow": "...", "title": "6-10 words (Elm Grove trees / seasons themed)", "text": "80-110 words"},
 "whyUs": [ {"title": "2-5 words", "text": "55-75 words"} x6 ],
 "process": [ {"title": "2-4 words", "text": "45-60 words"} x4 ],
 "doors": {"h2a": "...", "h2b": "...", "paragraphs": ["100-130 words" x3], "bullets": ["3-6 words" x6]},
 "openers": {"h2a": "...", "h2b": "...", "paragraphs": ["90-120 words" x2], "bullets": ["3-6 words" x6]},
 "seasons": [ {"label": "Winter|Spring|Summer|Fall", "title": "4-8 words", "text": "65-85 words"} x4 ],
 "costFactors": {"intro": "50-70 words", "items": [ {"title": "2-5 words", "text": "45-60 words"} x5 ]},
 "maintenance": {"intro": "60-80 words", "bullets": ["4-9 words" x8], "outro": "40-60 words"},
 "area": {"paragraphs": ["90-120 words" x2], "places": [12 place names]},
 "faqs": [ {"q": "...", "a": "65-90 words"} x9 ],
 "cta": {"title": "4-8 words", "text": "25-40 words"}
}

Service slugs (use exactly), with nav name:
garage-door-repairs (Garage Door Repair), same-day-garage-door-repair-service (Same Day Repair; h1 "Emergency & Same Day Garage Door Repair in Elm Grove, WI"), broken-garage-door-springs-repair (Spring Replacement), garage-door-cable-repair (Cable Replacement), roller-replacement-repair (Roller Replacement), garage-door-panel-replacement (Panel Replacement), garage-door-track-replacement (Track Replacement), garage-door-drum-replacement (Drum Replacement), new-garage-door-installation (Garage Door Installation), garage-door-materials (Garage Door Materials), garage-door-styles (Garage Door Styles), custom-garage-doors (Custom Garage Doors), new-garage-door-opener-installation (Opener Installation), garage-door-opener-repair (Opener Repair)
