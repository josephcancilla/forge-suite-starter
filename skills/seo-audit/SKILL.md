---
name: seo-audit
description: "Quick SEO audit to find what's broken and what to fix first"
---

# seo-audit

Use this skill when the user wants an SEO health check on a site or page.

## Command Template

# SEO Audit

## When to Use
Your site isn't ranking, traffic dropped, or you want a baseline SEO health check.

## What I Need
- URL to audit
- Target keywords (if known)
- Main business goal (leads, sales, awareness)

## Quick Audit Checklist

### 1. Technical Foundations
- [ ] Site loads in <3 seconds (test: PageSpeed Insights)
- [ ] Mobile-friendly (test: Google Mobile-Friendly Test)
- [ ] HTTPS enabled
- [ ] No crawl errors (check Google Search Console)
- [ ] Sitemap exists and submitted
- [ ] Robots.txt not blocking important pages

### 2. On-Page Essentials
For each important page:
- [ ] Title tag includes target keyword (<60 chars)
- [ ] Meta description is compelling (<160 chars)
- [ ] H1 exists and includes keyword
- [ ] URL is clean and descriptive
- [ ] Images have alt text
- [ ] Internal links to related content

### 3. Content Quality
- [ ] Content matches search intent
- [ ] Answers the query better than competitors
- [ ] Has unique value (not rehashed content)
- [ ] Updated recently (if time-sensitive topic)
- [ ] Word count competitive with ranking pages

### 4. Authority Signals
- [ ] Backlinks from relevant sites
- [ ] Brand mentions
- [ ] Author credentials shown (E-E-A-T)

## Priority Framework

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| Site not indexed | Critical | Low | FIX NOW |
| Slow load time | High | Medium | This week |
| Missing title tags | High | Low | This week |
| Thin content | High | High | This month |
| No backlinks | Medium | High | Ongoing |

## Output Format

```
## SEO Audit: [URL]

**Overall Health:** 🔴 Poor / 🟡 Needs Work / 🟢 Good

**Critical Issues (fix immediately):**
1. [Issue] - [How to fix]

**High Priority (this week):**
1. [Issue] - [How to fix]
2. [Issue] - [How to fix]

**Medium Priority (this month):**
1. [Issue] - [How to fix]

**What's Working:**
- [Good thing]
- [Good thing]

**Quick Wins:**
1. [Easy fix with good impact]
2. [Easy fix with good impact]

**Next Steps:**
1. [First action]
2. [Second action]
```

## Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Not ranking for brand | Add brand to title tags |
| Low CTR | Rewrite meta descriptions |
| High bounce rate | Improve above-fold content |
| Slow site | Compress images, enable caching |
| Thin content | Expand with useful detail |

## Attribution
Framework adapted from Corey Haines' seo-audit skill (MIT License)
