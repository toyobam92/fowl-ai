"""Ashby posting API: https://api.ashbyhq.com/posting-api/job-board/{token}"""

from scrapers.base import Job, get_json, strip_html

API = "https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true"


def fetch(token: str) -> list[Job]:
    data = get_json(API.format(token=token))
    company = token.replace("-", " ").title()
    jobs = []
    for j in data.get("jobs", []):
        if j.get("isListed") is False:
            continue
        jobs.append(Job(
            url=j.get("jobUrl") or j.get("applyUrl", ""),
            company=company,
            title=j["title"],
            ats_type="ashby",
            jd_text=strip_html(j.get("descriptionHtml") or j.get("descriptionPlain", "")),
            location=j.get("location", ""),
            is_remote=j.get("isRemote"),
        ))
    return jobs
