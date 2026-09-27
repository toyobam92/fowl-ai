"""Build an anniversary-edition skeleton: newsletter.html + anniversary-blocks.html.

Usage: python3 automation/templates/assemble_anniversary.py [growth_rows] [first_rows] > out.html
Placeholders stay unfilled; fill them exactly as for a normal issue.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def repeat(html, name, times):
    start = html.find("<!-- %s (repeat" % name)
    end = html.find("<!-- /%s -->" % name)
    return html[:start] + html[start:end] * times + html[end:]


def assemble(template, blocks, growth_rows=6, first_rows=4):
    def block(name):
        start = blocks.find("-->", blocks.find("<!-- BLOCK " + name)) + 3
        end = blocks.find("<!-- BLOCK", start)
        return blocks[start:end if end > 0 else len(blocks)].strip()

    def before_row(marker):
        return template.rfind('<tr><td class="email-gutter"', 0, template.find(marker))

    confetti, ribbon, stats, growth, thanks = (
        block(n) for n in ("confetti", "ribbon", "stats", "growth", "thanks"))
    growth = repeat(repeat(growth, "GROWTH_ROW", growth_rows), "FIRST_ROW", first_rows)

    k = template.find("<tr>", template.find("max-width:640px"))
    template = template[:k] + confetti + "\n" + template[k:]
    eyebrow = re.search(r"<p [^>]*>The weekly brief</p>", template)
    template = template[:eyebrow.start()] + ribbon + template[eyebrow.end():]
    for marker, row in (("Sourced from", stats),
                        ("[CLOSING_REFLECTION]", growth + "\n" + thanks)):
        k = before_row(marker)
        template = template[:k] + row + "\n" + template[k:]
    return template


if __name__ == "__main__":
    read = lambda n: open(os.path.join(HERE, n), encoding="utf-8").read()
    counts = [int(a) for a in sys.argv[1:3]]
    sys.stdout.write(assemble(read("newsletter.html"), read("anniversary-blocks.html"), *counts))
