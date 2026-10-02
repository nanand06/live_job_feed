# live_job_feed

A self-updating dashboard of **US software, data and ML internships and new-grad roles**, built from the
[SimplifyJobs / Pitt CSC](https://github.com/SimplifyJobs/Summer2027-Internships) internship and
[new-grad](https://github.com/SimplifyJobs/New-Grad-Positions) lists.

**Dashboard:** https://nanand06.github.io/live_job_feed/

## How it works

- `job_check.py` downloads both SimplifyJobs `listings.json` files, keeps active roles in the
  *Software* and *AI/ML/Data* categories with at least one US location, and writes `site/jobs.json`
  (last 14 days). Run with a number of hours instead (`python3 job_check.py 2.5`) to print a plain-text
  digest of roles added in that window.
- `.github/workflows/refresh.yml` runs the script on a schedule timed just after each SimplifyJobs scrape
  batch (about 7:05 PM, 10:05 PM, 11:05 AM, 3:05 AM and 6:05 AM ET), commits the new `jobs.json`, and
  deploys `site/` to GitHub Pages.
- `site/index.html` renders the data: search, intern / new-grad and area filters, a posted-within window,
  and per-browser "seen" checkboxes.

## Caveats

The timestamp on each role is when the SimplifyJobs bot *found* it, not when the company posted it.
Most roles land in the 6 PM and 8–9 PM ET batches, so a role posted at 11 AM typically shows a ~6 PM time.

## Run locally

```sh
python3 job_check.py --json 14 site/jobs.json
python3 -m http.server -d site 8000   # then open http://localhost:8000
```
