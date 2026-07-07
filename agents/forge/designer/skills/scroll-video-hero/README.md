---
name: scroll-video-hero
owner: forge-designer
status: ROADMAPPED — saved but not yet wired
gate: a marketing sub-agent provisioned + L0 active
source: Maverick AI / Emergent Scroll Video Hero Setup Guide (2026 Edition)
installed: 2026-05-17
---

# Scroll Video Hero — Saved Skill (Not Yet Wired)

Forge Designer capability to build scroll-controlled video-hero landing pages
that preserve a reference site's visual language and replace its hero with a
full-viewport scroll-driven video.

## Status
**ROADMAPPED.** The master prompt is saved; the bin mode is not yet wired into
`forge-designer`. Wiring begins after the activation gate clears.

## Activation Gate
After a marketing sub-agent (social media + content) is provisioned
and at L0+. A funnel sub-agent is the natural integration point for landing-page
publishing — wiring should account for both.

## Build Dependencies (must be true before wiring)
1. A marketing sub-agent provisioned + L0 active.
2. A related directory/product build complete; CRM migration finished.
3. Chosen video-generation pipeline online (the operator's video-gen tool of choice).
4. `forge-designer --mode=scroll-video-hero --video=<path> --ref=<url>` mode
   spec'd by SpecMan with blind-spot pass.
5. Stack decision: Next.js + GSAP ScrollTrigger (continuous scrub) OR canvas
   image-sequence playback (cinematic, Apple-style). Pick on perf + mobile
   behavior, not aesthetics alone.

## What it does
Given (a) a reference website URL pasted into the build context and (b) an MP4
video file, produces a landing page that:

- Matches the reference site's colors, UI system, typography, spacing, layout
  rhythm, navigation, and UX behavior.
- Replaces the original hero/header with a scroll-controlled video that
  dominates the first viewport.
- Drives video timeline directly from scroll position (stepped cue-point
  fallback if continuous scrubbing is unstable on the target stack).
- Ships reduced-motion + mobile-safe fallbacks.
- Sanitizes the reference site's brand identity to neutral placeholders.

## Why it exists
Emergent.sh ships this as a templated workflow (Landing Page mode + this TXT
prompt + Claude 4.7 Opus). The operator chose to build it native to the Commander instead of
routing through Emergent. Forge Designer already has every primitive needed
(`frontend-design`, `web-design-guidelines`, `shadcn-ui`,
`vercel-react-best-practices`, Vercel MCP deploy path) — only the mode wrapper
and the video-pipeline hook are missing.

## Source Files
- `master-prompt.txt` — verbatim prompt (Maverick AI / 2026 Edition).
- Walkthrough PDF: `~/Desktop/Emergent_Scroll_Video_Hero_Guide.pdf`.

## Wiring Spec (placeholder, not yet authored)
SpecMan to author the wiring spec at gate-clear time. Spec must address:
- Mode flag: `--mode=scroll-video-hero`.
- Inputs: `--video=<path>` (MP4) + `--ref=<url-or-html>` (reference site).
- Higgsfield integration: optional `--higgsfield-prompt=<text>` to generate
  video inline before designing.
- Output: full project scaffold (Next.js page, scroll-link wiring, fallback
  paths, design tokens, deploy target).
- Quality checklist (from source guide): MP4 is hero / scroll-linked / matches
  reference colors+UI+UX / placeholders / first viewport feels like reference
  rebuilt around the video.
