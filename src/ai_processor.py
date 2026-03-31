"""Claude API integration for article classification and angle generation."""

import json
from anthropic import Anthropic


CLASSIFICATION_SYSTEM = """You are a senior PR analyst specializing in clean tech and EV infrastructure.

You will receive a batch of news articles. For each article, provide:
1. **theme**: Exactly one of: policy, infrastructure, competition, consumer, technology, market
2. **relevance_score**: 0.0 to 1.0 — how relevant is this to an EV charging network company (like ChargePoint, EVgo, Blink, or a new entrant)?
   - 0.9-1.0: Directly about EV charging networks, infrastructure policy, or named competitors
   - 0.7-0.8: About EV industry trends, grid/energy issues affecting charging, or adjacent infrastructure
   - 0.4-0.6: Tangentially related (general EV news, broader clean tech)
   - 0.0-0.3: Barely relevant or off-topic
3. **signal**: One sentence capturing the key newsworthy takeaway a PR person would care about.

Respond ONLY with a JSON array. No markdown, no explanation. Example:
[
  {"id": 1, "theme": "competition", "relevance_score": 0.9, "signal": "ChargePoint reported a 15% drop in utilization rates, suggesting market softness."},
  {"id": 2, "theme": "policy", "relevance_score": 0.8, "signal": "New NEVI funding tranche opens applications for rural charging corridors."}
]"""


ANGLE_GENERATION_SYSTEM = """You are a senior PR strategist at a top communications agency. Your client is **Volta**, a fictional electric vehicle charging network expanding rapidly across the US.

**Volta's positioning:**
- Mid-size but fast-growing EV charging network
- Focused on reliability and user experience over pure station count
- Expanding into underserved markets (rural, suburban, multi-family housing)
- Differentiator: integrating charging with local businesses and community spaces
- Key competitors: ChargePoint (largest network), EVgo (fast-charging focused), Blink Charging (diverse locations)

**Your job:** Generate 5-7 compelling story angle ideas that the PR team can pitch THIS WEEK. Each angle must be rooted in a specific recent news event or trend from the articles provided — no generic evergreen ideas.

**Quality bar — these are examples of angles Volta has successfully pitched before:**
- "How EV charging deserts are creating a new infrastructure inequality" → Business/policy outlets
- "The hidden grid strain of ultra-fast charging and how networks are adapting" → Trade press
- "Why charging stations are becoming the new third place for remote workers" → Lifestyle/consumer media

Notice what makes these good: each has a clear narrative tension, a "why now" hook, and a natural audience.

**For each angle, provide:**
1. **headline**: A compelling pitch headline (not clickbait — something an editor would take seriously)
2. **news_peg**: The specific recent event, announcement, data point, or trend that makes this timely. Reference the actual article(s) that inspired it.
3. **rationale**: 2-3 sentences on why an editor would care. What's the narrative tension? What's the reader's stake?
4. **outlet_type**: One of: trade_press, consumer_tech, business_press, local_news, lifestyle, policy
5. **outlet_rationale**: One sentence on why this specific outlet type is the right fit and which specific publications would bite.
6. **urgency**: high (news peg expires within days), medium (relevant for 1-2 weeks), low (trend-based, can pitch anytime)
7. **source_article_ids**: Array of article IDs from the input that inspired this angle.

**Rules:**
- Every angle MUST tie to specific article(s) from the input. No making up news events.
- Spread angles across different outlet types — don't cluster everything in trade press.
- At least one angle should position Volta as a thought leader (commenting on industry trend).
- At least one angle should be locally anchored (specific market or region).
- Avoid generic angles like "EV adoption is growing" — find the tension, the surprise, the counter-narrative.
- Think about what makes a journalist's eyes light up: conflict, data that contradicts expectations, human impact, trend inflection points.

Respond ONLY with a JSON array. No markdown, no explanation."""


def classify_articles(client: Anthropic, articles: list[dict]) -> list[dict]:
    """Classify a batch of articles by theme and relevance."""
    articles_text = "\n\n".join(
        f"[Article ID: {a['id']}]\nTitle: {a['title']}\nSource: {a['source']}\nDate: {a['published_date']}\nSummary: {a['summary']}"
        for a in articles
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=CLASSIFICATION_SYSTEM,
        messages=[{"role": "user", "content": f"Classify these articles:\n\n{articles_text}"}],
    )

    text = response.content[0].text.strip()
    # Handle potential markdown wrapping
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Classification JSON parse error: {e}")
        print(f"Raw response: {text[:500]}")
        return []


def generate_angles(client: Anthropic, articles: list[dict], custom_instructions: str = "") -> list[dict]:
    """Generate story angles from classified, relevant articles."""
    articles_text = "\n\n".join(
        f"[Article ID: {a['id']}] [{a['theme'].upper()}] [Relevance: {a['relevance_score']}]\n"
        f"Title: {a['title']}\nSource: {a['source']}\nDate: {a['published_date']}\n"
        f"Signal: {a.get('signal', a['summary'])}\nSummary: {a['summary']}"
        for a in articles
    )

    system = ANGLE_GENERATION_SYSTEM
    if custom_instructions.strip():
        system += (
            "\n\n**ADDITIONAL INSTRUCTIONS FROM THE PR TEAM (always follow these):**\n"
            + custom_instructions.strip()
        )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system,
        messages=[{
            "role": "user",
            "content": f"Here are the top recent articles relevant to Volta. Generate story angles for this week's pitching:\n\n{articles_text}",
        }],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Angle generation JSON parse error: {e}")
        print(f"Raw response: {text[:500]}")
        return []
