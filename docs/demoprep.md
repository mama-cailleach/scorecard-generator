What to showcase (most important, in order)

    HTML report (primary deliverable)
    Show the charts (Manhattan, run-rate line, worm) + key tables (scorecards, best batters/bowlers, phases). This is what will “sell” the project fastest.
    Markdown report (shareable + readable)
    Show it rendered (Notion/GitHub preview). This proves the tool can produce a clean written match report.
    CLI scoring (credibility)
    Show just enough ball-by-ball entry to prove it’s a scoring tool, then jump to the outputs.
    Exports folder contents (trust + reproducibility)
    One screenshot of scorecard_generator/exports/ showing the generated files: .html, .md, and the legacy/useful .csvs.

Best-practice demo plan (60–90 seconds)
Clip 1: “It’s a scorer” (15–25s)

    Run: python -m scorecard_generator.main
    Quick cuts through team selection/toss/openers/bowler
    Enter 1 over (include at least: a dot ball, a boundary, and either a wicket or an extra)

Clip 2: “It produces professional outputs” (30–45s)

    Jump cut to end-of-innings/end-of-match
    Choose “match stats” (very briefly)
    Show the CLI saying exports were written to scorecard_generator/exports/

Clip 3: “Open the HTML report” (20–30s)

    Open the exported HTML in a browser
    Scroll to:
        Summary/result
        Scorecards
        Phases
        Best batters/bowlers
        Charts (pause briefly on each chart)

Optional (but nice): 5 seconds showing the Markdown report rendered.
Screenshots checklist (for your Notion page)

Take these after you run a match once:

    CLI in-progress scoring (showing the ball prompt and a few balls logged)
    CLI match summary + “stats menu” (whatever screen shows you can choose analyses)
    scorecard_generator/exports/ folder listing (show .html, .md, .csv)
    HTML report – header/summary
    HTML report – innings scorecards
    HTML report – phases
    HTML report – best batters/bowlers
    HTML report – charts section (Manhattan + worm + run-rate)

That’s plenty; you can cut it down to 6 if you want.
How to present this on Notion (simple structure)

    Title: Cricket T20 Scorecard Generator (Live Scoring + Auto Reports)
    1-liner: “Ball-by-ball scoring tool that exports a complete match report (HTML/Markdown) with charts and analytics.”
    Demo: embed the 60–90s video
    Outputs: screenshots + links/downloads (HTML/MD)
    How to run:
        python -m scorecard_generator.main
        outputs in scorecard_generator/exports/
    What it demonstrates: interactive data capture → structured outputs → analysis/reporting
