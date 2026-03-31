"""Seed historical data for January and February 2026 for the history dashboard."""

from src.database import init_db, get_connection
import json


def seed_history():
    init_db()
    conn = get_connection()

    # Check if history already seeded
    count = conn.execute("SELECT COUNT(*) FROM articles WHERE fetched_via = 'seed-history'").fetchone()[0]
    if count > 0:
        print(f"Historical data already seeded ({count} articles). Skipping.")
        conn.close()
        return

    # ==================== JANUARY 2026 ====================

    jan_articles = [
        {
            "title": "Biden Administration Finalizes $7.5B EV Charging Buildout Plan",
            "url": "https://example.com/hist/biden-ev-plan",
            "source": "Bloomberg",
            "published_date": "2026-01-08",
            "summary": "The White House released final guidance for the $7.5 billion EV charging investment from the Infrastructure Act, including new requirements for uptime monitoring and interoperability.",
            "theme": "policy",
            "relevance_score": 0.95,
            "signal": "Federal EV charging spending rules finalized with strict uptime and interoperability mandates.",
        },
        {
            "title": "ChargePoint Q4 Revenue Beats Estimates But Guidance Disappoints",
            "url": "https://example.com/hist/cp-q4",
            "source": "WSJ",
            "published_date": "2026-01-12",
            "summary": "ChargePoint reported Q4 revenue of $118M, beating estimates, but issued weak forward guidance citing slower-than-expected commercial fleet adoption.",
            "theme": "competition",
            "relevance_score": 0.92,
            "signal": "ChargePoint beats Q4 but weak guidance suggests commercial fleet charging growth stalling.",
        },
        {
            "title": "GM and Pilot Travel Centers Open 500th DC Fast Charger",
            "url": "https://example.com/hist/gm-pilot",
            "source": "Electrek",
            "published_date": "2026-01-15",
            "summary": "General Motors and Pilot Company celebrated the 500th DC fast charger installation at Pilot and Flying J travel centers across the US, targeting long-distance EV road trips.",
            "theme": "competition",
            "relevance_score": 0.85,
            "signal": "GM-Pilot highway charging partnership hits 500 stations, intensifying competition for road-trip charging.",
        },
        {
            "title": "Winter Storm Exposes EV Charging Reliability Gaps Across Midwest",
            "url": "https://example.com/hist/winter-storm",
            "source": "The Verge",
            "published_date": "2026-01-18",
            "summary": "A severe winter storm left hundreds of EV drivers stranded at non-functioning chargers in Illinois and Wisconsin, reigniting debate about charging infrastructure resilience in extreme weather.",
            "theme": "infrastructure",
            "relevance_score": 0.90,
            "signal": "Midwest winter storm strands EV drivers at broken chargers, highlighting cold-weather reliability crisis.",
        },
        {
            "title": "California Mandates 99% Uptime for Publicly Funded EV Chargers",
            "url": "https://example.com/hist/ca-uptime",
            "source": "Green Car Reports",
            "published_date": "2026-01-22",
            "summary": "California Energy Commission adopted new regulations requiring 99% uptime for any EV charger receiving state or federal funding, with financial penalties for non-compliance.",
            "theme": "policy",
            "relevance_score": 0.93,
            "signal": "California sets 99% uptime mandate for funded chargers with penalties, raising the reliability bar.",
        },
        {
            "title": "Uber Launches EV-Only Ride Option in 10 US Cities",
            "url": "https://example.com/hist/uber-ev",
            "source": "TechCrunch",
            "published_date": "2026-01-25",
            "summary": "Uber rolled out an EV-only ride option in major metros including NYC, LA, and Chicago, creating new demand patterns for rideshare driver charging.",
            "theme": "market",
            "relevance_score": 0.80,
            "signal": "Uber EV-only rides in 10 cities will reshape urban charging demand patterns for rideshare fleets.",
        },
        {
            "title": "Report: Average Public Charging Cost Now Rivals Gas Per Mile",
            "url": "https://example.com/hist/charging-cost",
            "source": "InsideEVs",
            "published_date": "2026-01-28",
            "summary": "A new AAA report found that the average cost of public DC fast charging now approaches gasoline per-mile costs in many states, undermining a key EV selling point.",
            "theme": "consumer",
            "relevance_score": 0.88,
            "signal": "Public charging costs approaching gas parity per mile, threatening core EV value proposition.",
        },
        {
            "title": "Rivian Partners with State Parks for Destination Charging Network",
            "url": "https://example.com/hist/rivian-parks",
            "source": "CleanTechnica",
            "published_date": "2026-01-30",
            "summary": "Rivian announced partnerships with 40 state parks to install Level 2 destination chargers, positioning its adventure brand with outdoor recreation.",
            "theme": "competition",
            "relevance_score": 0.75,
            "signal": "Rivian enters charging game with state park destination network, targeting outdoor adventure niche.",
        },
    ]

    jan_angles = [
        {
            "headline": "The $7.5 billion reliability test: Why federal charging rules will separate winners from pretenders",
            "news_peg": "Biden administration finalized EV charging buildout guidance with strict uptime monitoring and interoperability requirements.",
            "rationale": "The new federal rules effectively pick winners among charging networks. Companies already focused on reliability will thrive while those with poor uptime records face exclusion from federal funding. This is a defining regulatory moment for the industry.",
            "outlet_type": "business_press",
            "outlet_rationale": "Bloomberg and WSJ readers need to understand how this reshapes the competitive landscape for their portfolio companies.",
            "urgency": "high",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-01-10",
        },
        {
            "headline": "Frozen out: How a single winter storm exposed the EV charging industry's biggest weakness",
            "news_peg": "Hundreds of EV drivers stranded at broken chargers during Midwest winter storm, with social media backlash going viral.",
            "rationale": "This is visceral and visual. Stranded drivers, frozen screens, angry social posts. It puts a human face on the reliability data and creates urgency around cold-weather charging infrastructure.",
            "outlet_type": "consumer_tech",
            "outlet_rationale": "The Verge and Wired audiences are EV-curious consumers who need to understand real-world ownership challenges.",
            "urgency": "high",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-01-20",
        },
        {
            "headline": "When charging your EV costs as much as filling a gas tank, what's the point?",
            "news_peg": "AAA report shows public DC fast charging now rivals gasoline per-mile costs in many states.",
            "rationale": "This directly challenges the economic narrative that has driven EV adoption. It is a provocative angle that editors love because it goes against conventional wisdom, while opening the door for solutions.",
            "outlet_type": "consumer_tech",
            "outlet_rationale": "Perfect for The Verge, CNET, and general consumer outlets where readers are actively considering EV purchases.",
            "urgency": "medium",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-01-29",
        },
        {
            "headline": "California just set the standard every charging network feared: 99% uptime or lose your funding",
            "news_peg": "California Energy Commission mandates 99% uptime with financial penalties for publicly funded EV chargers.",
            "rationale": "99% uptime is an aspirational target that many networks cannot currently meet. This creates a clear narrative of regulatory pressure forcing the industry to mature.",
            "outlet_type": "trade_press",
            "outlet_rationale": "Electrek, Utility Dive, and energy trade press will cover the operational implications in depth.",
            "urgency": "medium",
            "source_article_ids": [],
            "used": 0,
            "generated_at": "2026-01-24",
        },
        {
            "headline": "From trailheads to truck stops: The surprisingly different strategies for where to put EV chargers",
            "news_peg": "Rivian targets state parks while GM-Pilot focuses on highway travel centers, showing how different brands chase different use cases.",
            "rationale": "Two contrasting strategies reveal that there is no single charging market. The destination vs. corridor split has implications for every player and investor.",
            "outlet_type": "lifestyle",
            "outlet_rationale": "Fast Company and outdoor/travel publications would engage with the adventure and design angle.",
            "urgency": "low",
            "source_article_ids": [],
            "used": 0,
            "generated_at": "2026-01-31",
        },
    ]

    # ==================== FEBRUARY 2026 ====================

    feb_articles = [
        {
            "title": "Tesla Opens Supercharger Network to All EVs in 15 Additional States",
            "url": "https://example.com/hist/tesla-open",
            "source": "Electrek",
            "published_date": "2026-02-03",
            "summary": "Tesla expanded its open Supercharger program to 15 more states, bringing the total to 40 states where non-Tesla EVs can charge at Supercharger stations.",
            "theme": "competition",
            "relevance_score": 0.93,
            "signal": "Tesla Supercharger network now open to all EVs in 40 states, intensifying competitive pressure on other networks.",
        },
        {
            "title": "EVgo Reports First Profitable Quarter in Company History",
            "url": "https://example.com/hist/evgo-profit",
            "source": "Bloomberg",
            "published_date": "2026-02-06",
            "summary": "EVgo achieved its first quarterly profit, driven by increased utilization rates and strategic partnerships with retail locations including Starbucks and Walmart.",
            "theme": "competition",
            "relevance_score": 0.91,
            "signal": "EVgo hits first-ever profit on the back of retail partnerships, proving the co-location model works.",
        },
        {
            "title": "DOE Study: 40% of Rural Counties Still Have Zero Public EV Chargers",
            "url": "https://example.com/hist/doe-rural",
            "source": "Green Car Reports",
            "published_date": "2026-02-10",
            "summary": "A Department of Energy analysis found that 40% of rural US counties have no public EV charging infrastructure at all, with the gap widening despite federal investment.",
            "theme": "infrastructure",
            "relevance_score": 0.89,
            "signal": "40% of rural counties still have zero public chargers despite billions in federal spending.",
        },
        {
            "title": "Hertz Reverses Course, Adds 5,000 EVs Back to Fleet After Charging Improvements",
            "url": "https://example.com/hist/hertz-ev",
            "source": "WSJ",
            "published_date": "2026-02-12",
            "summary": "After selling off EVs last year citing charging challenges, Hertz is re-expanding its electric fleet after partnering with charging networks to install depot chargers at 200 rental locations.",
            "theme": "market",
            "relevance_score": 0.84,
            "signal": "Hertz U-turn on EVs after solving depot charging, validating that infrastructure solves adoption hesitancy.",
        },
        {
            "title": "Cybersecurity Researchers Discover Vulnerabilities in Major Charging Network APIs",
            "url": "https://example.com/hist/cyber-charger",
            "source": "TechCrunch",
            "published_date": "2026-02-15",
            "summary": "Security researchers at Black Hat demonstrated vulnerabilities in three major charging network APIs that could allow attackers to start/stop sessions, access payment data, and disrupt grid connections.",
            "theme": "technology",
            "relevance_score": 0.82,
            "signal": "Charging network APIs found vulnerable to cyberattacks, raising concerns about payment security and grid stability.",
        },
        {
            "title": "New York City Approves Curbside EV Charging Pilot on 100 Blocks",
            "url": "https://example.com/hist/nyc-curbside",
            "source": "The Verge",
            "published_date": "2026-02-18",
            "summary": "NYC DOT approved a pilot program to install curbside Level 2 EV chargers on 100 blocks across all five boroughs, targeting residents without access to home charging.",
            "theme": "policy",
            "relevance_score": 0.87,
            "signal": "NYC launches curbside charging on 100 blocks, creating a model for dense urban EV infrastructure.",
        },
        {
            "title": "Ford Cuts Price of Mustang Mach-E by $3,000 Citing Improved Charging Access",
            "url": "https://example.com/hist/ford-price",
            "source": "InsideEVs",
            "published_date": "2026-02-20",
            "summary": "Ford reduced the Mustang Mach-E price by $3,000, with executives explicitly citing improved public charging infrastructure as reducing range anxiety and enabling more competitive pricing.",
            "theme": "market",
            "relevance_score": 0.78,
            "signal": "Ford links price cut to better charging access, showing infrastructure directly drives auto industry pricing.",
        },
        {
            "title": "Blink Charging Announces Merger with European Network Allego",
            "url": "https://example.com/hist/blink-allego",
            "source": "Bloomberg",
            "published_date": "2026-02-22",
            "summary": "Blink Charging and European charging operator Allego announced a merger to create a transatlantic network, seeking scale advantages amid industry consolidation.",
            "theme": "competition",
            "relevance_score": 0.90,
            "signal": "Blink-Allego merger signals charging industry consolidation is accelerating, creating transatlantic networks.",
        },
        {
            "title": "Oregon Becomes First State to Require EV Chargers at All New Gas Stations",
            "url": "https://example.com/hist/oregon-mandate",
            "source": "CleanTechnica",
            "published_date": "2026-02-25",
            "summary": "Oregon Governor signed legislation requiring all newly built or substantially renovated gas stations to include at least two EV charging ports, effective 2027.",
            "theme": "policy",
            "relevance_score": 0.86,
            "signal": "Oregon mandates EV chargers at new gas stations, potentially setting a model for other states.",
        },
        {
            "title": "Utilities Report 300% Increase in Commercial EV Charging Rate Applications",
            "url": "https://example.com/hist/utility-demand",
            "source": "Electrek",
            "published_date": "2026-02-27",
            "summary": "Major utilities including Duke Energy, Southern Company, and PG&E reported a 300% year-over-year increase in applications for commercial EV charging electrical service, signaling infrastructure buildout is accelerating.",
            "theme": "infrastructure",
            "relevance_score": 0.85,
            "signal": "Utility applications for commercial charging up 300% YoY, confirming infrastructure buildout is accelerating.",
        },
    ]

    feb_angles = [
        {
            "headline": "Tesla just made every charging network's business plan obsolete",
            "news_peg": "Tesla opened Superchargers to all EVs in 40 states, creating the largest open charging network overnight.",
            "rationale": "When the biggest network opens up, smaller players must differentiate on something other than station count. This forces a strategic rethink across the industry.",
            "outlet_type": "business_press",
            "outlet_rationale": "WSJ and Bloomberg readers holding charging network stocks need this analysis immediately.",
            "urgency": "high",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-02-05",
        },
        {
            "headline": "The proof is in the profit: How EVgo cracked the charging business model everyone said was impossible",
            "news_peg": "EVgo reported first-ever quarterly profit, driven by retail co-location partnerships with Starbucks and Walmart.",
            "rationale": "First profit in the charging industry is a milestone that proves viability. The retail co-location strategy is the story within the story.",
            "outlet_type": "business_press",
            "outlet_rationale": "Bloomberg and Fortune love milestone-moment business stories, especially ones that validate a disputed business model.",
            "urgency": "high",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-02-08",
        },
        {
            "headline": "Hackers can now remotely control your EV charger. The industry is not ready.",
            "news_peg": "Black Hat researchers demonstrated API vulnerabilities in three major charging networks, exposing payment data and grid connection risks.",
            "rationale": "Cybersecurity plus critical infrastructure is a guaranteed headline. The grid connection angle elevates this beyond consumer data theft into national security territory.",
            "outlet_type": "consumer_tech",
            "outlet_rationale": "TechCrunch, Wired, and The Verge all have dedicated cybersecurity coverage that would jump on this.",
            "urgency": "high",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-02-16",
        },
        {
            "headline": "Hertz tried to quit EVs. Then they fixed the charging, and everything changed.",
            "news_peg": "Hertz re-expanding EV fleet after solving depot charging through network partnerships, reversing last year's high-profile EV selloff.",
            "rationale": "This is a redemption narrative that directly ties infrastructure to adoption. Hertz's U-turn is proof that charging solves the hesitancy problem.",
            "outlet_type": "consumer_tech",
            "outlet_rationale": "The Verge and Ars Technica covered the original Hertz selloff extensively and would want the follow-up.",
            "urgency": "medium",
            "source_article_ids": [],
            "used": 1,
            "generated_at": "2026-02-14",
        },
        {
            "headline": "NYC is about to turn every curb into a gas station. Here is how.",
            "news_peg": "NYC approved curbside Level 2 charging on 100 blocks across all five boroughs, targeting the 70% of New Yorkers who lack home charging.",
            "rationale": "Urban curbside charging is the missing link for city dwellers and EV adoption. NYC as the test case gets automatic attention.",
            "outlet_type": "local_news",
            "outlet_rationale": "NYC media (Gothamist, NY Post, Curbed NY) plus national urbanist outlets like CityLab and Fast Company.",
            "urgency": "medium",
            "source_article_ids": [],
            "used": 0,
            "generated_at": "2026-02-19",
        },
        {
            "headline": "The great consolidation: Why the EV charging industry is about to look a lot like the airline business",
            "news_peg": "Blink-Allego transatlantic merger signals the start of serious industry consolidation among charging networks.",
            "rationale": "Mergers and consolidation make for accessible business narratives. The airline industry comparison gives readers an instant mental model for what the end state looks like.",
            "outlet_type": "business_press",
            "outlet_rationale": "Bloomberg and Financial Times love industry consolidation stories with clear historical parallels.",
            "urgency": "low",
            "source_article_ids": [],
            "used": 0,
            "generated_at": "2026-02-24",
        },
    ]

    # Insert January articles
    for art in jan_articles:
        conn.execute(
            """INSERT INTO articles (title, url, source, published_date, summary, raw_content,
               theme, relevance_score, signal, fetched_via)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'seed-history')""",
            (art["title"], art["url"], art["source"], art["published_date"],
             art["summary"], art["summary"], art["theme"],
             art["relevance_score"], art["signal"]),
        )

    # Insert February articles
    for art in feb_articles:
        conn.execute(
            """INSERT INTO articles (title, url, source, published_date, summary, raw_content,
               theme, relevance_score, signal, fetched_via)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'seed-history')""",
            (art["title"], art["url"], art["source"], art["published_date"],
             art["summary"], art["summary"], art["theme"],
             art["relevance_score"], art["signal"]),
        )

    # Insert January angles
    for angle in jan_angles:
        conn.execute(
            """INSERT INTO angles (headline, rationale, news_peg, outlet_type, outlet_rationale,
               urgency, used, source_article_ids, generated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (angle["headline"], angle["rationale"], angle["news_peg"],
             angle["outlet_type"], angle["outlet_rationale"], angle["urgency"],
             angle["used"], json.dumps(angle["source_article_ids"]), angle["generated_at"]),
        )

    # Insert February angles
    for angle in feb_angles:
        conn.execute(
            """INSERT INTO angles (headline, rationale, news_peg, outlet_type, outlet_rationale,
               urgency, used, source_article_ids, generated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (angle["headline"], angle["rationale"], angle["news_peg"],
             angle["outlet_type"], angle["outlet_rationale"], angle["urgency"],
             angle["used"], json.dumps(angle["source_article_ids"]), angle["generated_at"]),
        )

    conn.commit()
    conn.close()
    print(f"Seeded historical data: {len(jan_articles) + len(feb_articles)} articles, {len(jan_angles) + len(feb_angles)} angles.")


if __name__ == "__main__":
    seed_history()
