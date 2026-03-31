"""Seed the database with realistic sample data for demo purposes.

Run this if you want the dashboard to have content without needing API keys.
The pipeline will add real data on top of this when you run it with keys.
"""

from src.database import init_db, get_connection
import json
from datetime import datetime, timedelta


def seed():
    init_db()
    conn = get_connection()

    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    if count > 0:
        print(f"Database already has {count} articles. Skipping seed.")
        conn.close()
        return

    today = datetime.now()

    articles = [
        {
            "title": "ChargePoint Announces Layoffs Affecting 15% of Workforce",
            "url": "https://example.com/chargepoint-layoffs",
            "source": "Bloomberg",
            "published_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "summary": "ChargePoint Holdings said it would cut about 15% of its workforce as the EV charging company tries to reach profitability amid slowing demand growth. The company cited macroeconomic headwinds and a need to streamline operations.",
            "raw_content": "ChargePoint Holdings said it would cut about 15% of its workforce as the EV charging company tries to reach profitability amid slowing demand growth.",
            "theme": "competition",
            "relevance_score": 0.95,
            "signal": "ChargePoint cutting 15% of staff signals financial pressure in the EV charging sector.",
            "fetched_via": "seed",
        },
        {
            "title": "FHWA Opens $2.1B in NEVI Formula Funding for Rural EV Charging Corridors",
            "url": "https://example.com/nevi-rural-funding",
            "source": "Electrek",
            "published_date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "summary": "The Federal Highway Administration announced a new $2.1 billion tranche of NEVI formula funding specifically targeting rural and underserved communities. States must submit deployment plans by Q3 2026.",
            "raw_content": "The Federal Highway Administration announced a new $2.1 billion tranche of NEVI formula funding.",
            "theme": "policy",
            "relevance_score": 0.92,
            "signal": "Major new federal funding round opens for rural EV charging with Q3 2026 deadline.",
            "fetched_via": "seed",
        },
        {
            "title": "California Grid Operator Warns of Summer Strain from EV Fast Charging Growth",
            "url": "https://example.com/caiso-ev-strain",
            "source": "Green Car Reports",
            "published_date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "summary": "CAISO released a report warning that rapid deployment of DC fast chargers in urban California corridors could strain the grid during peak summer demand, calling for smarter load management and vehicle-to-grid integration.",
            "raw_content": "CAISO released a report warning that rapid deployment of DC fast chargers in urban California corridors could strain the grid.",
            "theme": "infrastructure",
            "relevance_score": 0.88,
            "signal": "California grid operator flags EV fast charging as a growing strain risk for summer peaks.",
            "fetched_via": "seed",
        },
        {
            "title": "EVgo Partners with Starbucks to Add Charging at 500 Drive-Thru Locations",
            "url": "https://example.com/evgo-starbucks",
            "source": "TechCrunch",
            "published_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "summary": "EVgo announced a partnership with Starbucks to install EV fast chargers at 500 drive-thru locations nationwide, positioning charging time as coffee break time for EV drivers.",
            "raw_content": "EVgo announced a partnership with Starbucks to install EV fast chargers at 500 drive-thru locations.",
            "theme": "competition",
            "relevance_score": 0.90,
            "signal": "EVgo-Starbucks partnership signals charging networks competing on experience, not just speed.",
            "fetched_via": "seed",
        },
        {
            "title": "Study Finds EV Charging Deserts Correlate with Income Inequality in Major Metro Areas",
            "url": "https://example.com/charging-deserts-equity",
            "source": "The Verge",
            "published_date": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
            "summary": "A new study from MIT found that EV charging station density in the 50 largest US metro areas correlates strongly with median household income, with low-income neighborhoods having 73% fewer public chargers per capita.",
            "raw_content": "A new study from MIT found that EV charging station density correlates strongly with median household income.",
            "theme": "consumer",
            "relevance_score": 0.85,
            "signal": "MIT study quantifies EV charging infrastructure gap: 73% fewer chargers in low-income areas.",
            "fetched_via": "seed",
        },
        {
            "title": "Blink Charging Stock Drops 22% After SEC Investigation Disclosed",
            "url": "https://example.com/blink-sec",
            "source": "WSJ",
            "published_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "summary": "Blink Charging shares plunged after the company disclosed an SEC investigation into its revenue recognition practices. The probe focuses on whether Blink overstated charger deployment numbers in recent filings.",
            "raw_content": "Blink Charging shares plunged after the company disclosed an SEC investigation.",
            "theme": "competition",
            "relevance_score": 0.93,
            "signal": "Blink Charging under SEC investigation for potentially overstated charger deployment numbers.",
            "fetched_via": "seed",
        },
        {
            "title": "New Battery Tech Promises 10-Minute EV Charging by 2028",
            "url": "https://example.com/fast-battery-tech",
            "source": "InsideEVs",
            "published_date": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
            "summary": "StoreDot announced successful testing of silicon-dominant battery cells that can reach 80% charge in under 10 minutes, with mass production targeted for 2028. The technology could reshape charging network economics.",
            "raw_content": "StoreDot announced successful testing of silicon-dominant battery cells.",
            "theme": "technology",
            "relevance_score": 0.78,
            "signal": "10-minute charging tech from StoreDot nearing production could reshape charging network business models.",
            "fetched_via": "seed",
        },
        {
            "title": "Multi-Family Housing Becomes the Next Frontier for EV Charging Installation",
            "url": "https://example.com/multifamily-ev-charging",
            "source": "CleanTechnica",
            "published_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "summary": "Industry analysts report that apartment complexes and condos represent the largest untapped market for EV charging. Over 36% of Americans live in multi-family housing but fewer than 5% of those buildings have any EV charging infrastructure.",
            "raw_content": "Apartment complexes and condos represent the largest untapped market for EV charging.",
            "theme": "market",
            "relevance_score": 0.86,
            "signal": "Multi-family housing identified as biggest EV charging gap: 36% of Americans, under 5% coverage.",
            "fetched_via": "seed",
        },
        {
            "title": "Texas Approves Utility Rate Structure Favoring Commercial EV Charging Operators",
            "url": "https://example.com/texas-ev-rates",
            "source": "Electrek",
            "published_date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "summary": "The Public Utility Commission of Texas approved a new commercial rate structure that reduces demand charges for EV charging operators by up to 40%, making Texas one of the most favorable states for charging network economics.",
            "raw_content": "Texas PUC approved a new rate structure reducing demand charges for EV charging operators by up to 40%.",
            "theme": "policy",
            "relevance_score": 0.87,
            "signal": "Texas slashes demand charges for EV chargers by 40%, creating favorable economics for network expansion.",
            "fetched_via": "seed",
        },
        {
            "title": "J.D. Power Survey: EV Drivers Rank Charging Reliability Over Speed",
            "url": "https://example.com/jdpower-reliability",
            "source": "Green Car Reports",
            "published_date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "summary": "A new J.D. Power survey of 12,000 EV drivers found that charger reliability (uptime and successful session completion) ranked as the top priority, ahead of charging speed and pricing. The survey found that 21% of public charging attempts still fail.",
            "raw_content": "J.D. Power found charger reliability ranked as the top priority for EV drivers, with 21% of sessions failing.",
            "theme": "consumer",
            "relevance_score": 0.91,
            "signal": "21% of public EV charging sessions still fail — reliability now the top driver concern per J.D. Power.",
            "fetched_via": "seed",
        },
        {
            "title": "Amazon Delivery Fleet Expansion Drives Demand for Depot-Based Charging Infrastructure",
            "url": "https://example.com/amazon-fleet-charging",
            "source": "TechCrunch",
            "published_date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "summary": "Amazon's push to electrify its last-mile delivery fleet is creating massive demand for depot-based charging infrastructure, with the company seeking partners to install over 10,000 chargers at fulfillment centers by 2027.",
            "raw_content": "Amazon seeking partners to install over 10,000 chargers at fulfillment centers.",
            "theme": "market",
            "relevance_score": 0.80,
            "signal": "Amazon needs 10,000+ depot chargers by 2027, creating a major B2B charging opportunity.",
            "fetched_via": "seed",
        },
        {
            "title": "European Automakers Push for Standardized Charging Payment Systems in US",
            "url": "https://example.com/eu-payment-standards",
            "source": "Bloomberg",
            "published_date": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
            "summary": "A coalition of European automakers including BMW, VW, and Mercedes are lobbying US regulators to mandate interoperable payment systems across all public EV charging networks, similar to European regulations taking effect in 2027.",
            "raw_content": "European automakers lobbying US regulators for standardized EV charging payments.",
            "theme": "policy",
            "relevance_score": 0.82,
            "signal": "EU automaker coalition pushing for US charging payment standardization — could reshape network interoperability.",
            "fetched_via": "seed",
        },
    ]

    for art in articles:
        conn.execute(
            """INSERT INTO articles (title, url, source, published_date, summary, raw_content,
               theme, relevance_score, signal, fetched_via)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (art["title"], art["url"], art["source"], art["published_date"],
             art["summary"], art["raw_content"], art["theme"],
             art["relevance_score"], art["signal"], art["fetched_via"]),
        )

    # Pre-generated angles based on these articles
    angles = [
        {
            "headline": "While competitors stumble, a new class of EV charging networks is quietly winning on reliability",
            "news_peg": "ChargePoint's 15% workforce reduction and Blink's SEC investigation come the same week J.D. Power data shows 21% of charging sessions fail — creating an opening for reliability-focused networks.",
            "rationale": "Two of the three largest charging networks are in crisis mode simultaneously. Combined with J.D. Power data showing reliability is the top driver concern, this is a rare moment where a challenger brand can credibly claim the incumbent model is broken. Editors love a David-vs-Goliath story backed by data.",
            "outlet_type": "business_press",
            "outlet_rationale": "Bloomberg and WSJ are already covering the ChargePoint and Blink stories — this gives them a 'what comes next' follow-up with a clear narrative arc.",
            "urgency": "high",
            "source_article_ids": [1, 6, 10],
        },
        {
            "headline": "The $2.1 billion race to charge rural America — and why most networks aren't built for it",
            "news_peg": "FHWA just opened $2.1B in NEVI funding specifically for rural corridors, with a Q3 2026 submission deadline. Most existing networks are optimized for urban density, not rural economics.",
            "rationale": "This is a massive infrastructure story with a ticking clock. Rural EV charging is an equity issue, a policy issue, and a business opportunity all at once. The funding deadline creates genuine urgency, and the gap between urban and rural charging (MIT study shows 73% fewer chargers in low-income areas) provides the narrative tension.",
            "outlet_type": "policy",
            "outlet_rationale": "Strong fit for Politico's energy desk, E&E News, and business outlets covering infrastructure spending. The equity angle also plays well for general news.",
            "urgency": "high",
            "source_article_ids": [2, 5],
        },
        {
            "headline": "Why your apartment building is the biggest obstacle to buying an electric car",
            "news_peg": "New industry data shows 36% of Americans live in multi-family housing but fewer than 5% of those buildings have any EV charging — making renters effectively locked out of the EV transition.",
            "rationale": "This reframes EV adoption as a housing equity story rather than a car story. It's relatable (millions of people live in apartments), surprising (most readers don't realize the gap is this extreme), and solvable — which means an editor can see the full arc of the piece.",
            "outlet_type": "consumer_tech",
            "outlet_rationale": "The Verge and Wired love stories that connect technology adoption to systemic barriers. This also works well for lifestyle publications covering urban living and sustainability.",
            "urgency": "medium",
            "source_article_ids": [8, 5],
        },
        {
            "headline": "The hidden fight over how you'll pay to charge your car",
            "news_peg": "European automakers are lobbying US regulators for standardized payment systems while networks compete to lock in proprietary apps and memberships — echoing the early mobile payment wars.",
            "rationale": "Payment fragmentation is a concrete frustration every EV driver experiences but few people understand why it exists. The EU coalition push gives it a geopolitical angle (European regulation influencing US policy), and the comparison to early mobile payments gives editors a familiar frame.",
            "outlet_type": "consumer_tech",
            "outlet_rationale": "TechCrunch and The Verge regularly cover platform interoperability battles. The consumer frustration angle makes this accessible beyond the EV niche.",
            "urgency": "medium",
            "source_article_ids": [12],
        },
        {
            "headline": "Texas just made itself the best state in America to operate an EV charging network",
            "news_peg": "Texas PUC approved a 40% reduction in demand charges for commercial EV charging — a move that fundamentally changes the economics of charging network expansion in the state.",
            "rationale": "Texas as an EV-friendly state is a counter-narrative that editors love. Demand charges are the hidden cost that makes many charging stations unprofitable, so a 40% cut is genuinely significant. This positions Volta to announce Texas expansion plans tied to the rate change.",
            "outlet_type": "trade_press",
            "outlet_rationale": "Electrek and Utility Dive would cover the rate structure impact. Business press (Forbes, WSJ Texas bureau) would pick up the counter-narrative of Texas as EV leader.",
            "urgency": "medium",
            "source_article_ids": [9],
        },
        {
            "headline": "What happens to the grid when every Amazon van needs a charge by morning",
            "news_peg": "Amazon's push for 10,000+ depot chargers by 2027 coincides with CAISO's warning about grid strain from fast charging growth — creating a collision between fleet electrification ambitions and infrastructure reality.",
            "rationale": "Fleet electrification is the unsexy-but-enormous side of the EV transition. Amazon's scale makes it tangible for a general audience, and the grid strain tension creates a genuine problem to explore. This positions Volta as having smart grid integration capabilities.",
            "outlet_type": "trade_press",
            "outlet_rationale": "Strong fit for GreenTech Media, Canary Media, and fleet-focused trade publications. The Amazon angle also gives it crossover potential to business press.",
            "urgency": "low",
            "source_article_ids": [11, 3],
        },
        {
            "headline": "Coffee and kilowatts: how EV charging is reshaping the American roadside rest stop",
            "news_peg": "EVgo's 500-location Starbucks partnership signals that charging networks are competing on experience and amenities, not just watts — turning charging time into commercial real estate.",
            "rationale": "This is a lifestyle and design story disguised as an energy story. The Starbucks partnership is concrete and visual, and the broader trend of charging-as-destination touches urban planning, retail strategy, and consumer behavior. It's the kind of story that gets shared because it makes people imagine a different future.",
            "outlet_type": "lifestyle",
            "outlet_rationale": "Fast Company, Curbed, and even food/travel publications would engage with this. It's shareable and visual, which lifestyle editors prioritize.",
            "urgency": "medium",
            "source_article_ids": [4],
        },
    ]

    for angle in angles:
        conn.execute(
            """INSERT INTO angles (headline, rationale, news_peg, outlet_type, outlet_rationale, urgency, source_article_ids)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (angle["headline"], angle["rationale"], angle["news_peg"],
             angle["outlet_type"], angle["outlet_rationale"], angle["urgency"],
             json.dumps(angle["source_article_ids"])),
        )

    conn.commit()
    conn.close()
    print(f"Seeded {len(articles)} articles and {len(angles)} angles.")


if __name__ == "__main__":
    seed()
