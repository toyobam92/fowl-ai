"""Greenhouse job board API: https://boards-api.greenhouse.io/v1/boards/{token}/jobs"""

from scrapers.base import Job, get_json, strip_html

API = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"


def fetch(token: str) -> list[Job]:
    data = get_json(API.format(token=token))
    company = token.replace("-", " ").title()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(Job(
            url=j["absolute_url"],
            company=j.get("company_name") or company,
            title=j["title"],
            ats_type="greenhouse",
            jd_text=strip_html(j.get("content", "")),
            location=(j.get("location") or {}).get("name", ""),
        ))
    return jobs
