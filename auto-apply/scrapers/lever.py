"""Lever postings API: https://api.lever.co/v0/postings/{token}?mode=json"""

from scrapers.base import Job, get_json

API = "https://api.lever.co/v0/postings/{token}?mode=json"


def fetch(token: str) -> list[Job]:
    data = get_json(API.format(token=token))
    company = token.replace("-", " ").title()
    jobs = []
    for j in data:
        cats = j.get("categories") or {}
        location = cats.get("location") or ""
        workplace = (j.get("workplaceType") or "").lower()  # remote|hybrid|onsite when present
        jobs.append(Job(
            url=j["hostedUrl"],
            company=company,
            title=j["text"],
            ats_type="lever",
            jd_text=j.get("descriptionPlain")
                    or " ".join(f"{l.get('text', '')}: {l.get('content', '')}"
                                for l in j.get("lists", [])),
            location=location,
            is_remote=(workplace == "remote") if workplace else None,
        ))
    return jobs
