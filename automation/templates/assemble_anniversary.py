"""Build an anniversary-edition skeleton: newsletter.html + anniversary-blocks.html.

Usage: python3 automation/templates/assemble_anniversary.py <score_rows> > out.html
Placeholders stay unfilled; fill them exactly as for a normal issue. Cut stories
04 and 05 from the output (anniversary editions run 3 developments).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def assemble(template, blocks, score_rows=1):
    def block(name):
        start = blocks.find("-->", blocks.find("<!-- BLOCK " + name)) + 3
        end = blocks.find("<!-- BLOCK", start)
        return blocks[start:end if end > 0 else len(blocks)].strip()

    def before_row(marker):
        return template.rfind('<tr><td class="email-gutter"', 0, template.find(marker))

    confetti, ribbon, stats, scorecard, thanks = (
        block(n) for n in ("confetti", "ribbon", "stats", "scorecard", "thanks"))
    rs = scorecard.find("<!-- SCORE_ROW (repeat) -->")
    re_ = scorecard.find("<!-- /SCORE_ROW -->")
    scorecard = scorecard[:rs] + scorecard[rs:re_] * score_rows + scorecard[re_:]

    k = template.find("<tr>", template.find("max-width:640px"))
    template = template[:k] + confetti + "\n" + template[k:]
    eyebrow = re.search(r"<p [^>]*>The weekly brief</p>", template)
    template = template[:eyebrow.start()] + ribbon + template[eyebrow.end():]
    for marker, row in (("Sourced from", stats),
                        ("FOWL prediction [PREDICTION_NUMBER]", scorecard),
                        ("[CLOSING_REFLECTION]", thanks)):
        k = before_row(marker)
        template = template[:k] + row + "\n" + template[k:]
    return template


if __name__ == "__main__":
    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    read = lambda n: open(os.path.join(HERE, n), encoding="utf-8").read()
    sys.stdout.write(assemble(read("newsletter.html"), read("anniversary-blocks.html"), rows))
