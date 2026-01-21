# DISC Profile Analysis Prompt

Use this prompt to analyze calls through the lens of DISC personality profiles—understanding communication styles, interpersonal dynamics, and tailoring your approach.

## DISC Overview

| Type | Traits | Communication Style |
|------|--------|---------------------|
| **D** (Dominance) | Direct, results-oriented, decisive, competitive | Gets to the point, values efficiency, wants control |
| **I** (Influence) | Enthusiastic, optimistic, collaborative, expressive | Tells stories, builds rapport, seeks recognition |
| **S** (Steadiness) | Patient, reliable, team-oriented, calm | Listens carefully, avoids conflict, values stability |
| **C** (Conscientiousness) | Analytical, precise, systematic, quality-focused | Asks detailed questions, wants data, avoids risk |

## Prerequisites

Load the call review data first:
```
Read output/<call_name>/call_review.json
Read output/<call_name>/index.json
```

## Option A: Infer DISC Profiles from Call

```
Analyze this call to infer DISC profiles for each participant.

For each speaker, evaluate these indicators:

### Speech Patterns
- **Pace**: Fast and direct (D/I) vs. measured and thoughtful (S/C)
- **Volume**: Assertive (D) vs. animated (I) vs. soft (S) vs. even (C)
- **Interruptions**: Frequent (D) vs. enthusiastic overlaps (I) vs. waits turn (S/C)

### Language Indicators
- **D signals**: "Bottom line", "results", "let's move", "decide", "now"
- **I signals**: "Excited", "team", "people", "imagine", story-telling
- **S signals**: "We've always", "everyone agrees", "step by step", "comfortable"
- **C signals**: "Data shows", "specifically", "accuracy", "what if", "prove"

### Question Style
- **D**: Few questions, challenges assertions, "what's the ROI?"
- **I**: Big picture questions, "who else is doing this?"
- **S**: Process questions, "how does this affect the team?"
- **C**: Detailed questions, "what's the error rate?"

### Visual Cues (from frames)
- **D**: Direct eye contact, minimal gestures, impatient body language
- **I**: Animated expressions, hand gestures, smiling frequently
- **S**: Calm demeanor, nodding, relaxed posture
- **C**: Thoughtful expressions, note-taking, reserved reactions

For each participant, provide:
1. Primary DISC type (and secondary if clear)
2. Confidence level (high/medium/low)
3. Evidence from transcript and frames
```

## Option B: User-Provided Profiles

```
Analyze this call using the following known DISC profiles:

[Participant 1]: [D/I/S/C]
[Participant 2]: [D/I/S/C]

With these profiles in mind, evaluate the call dynamics and provide coaching recommendations.
```

## DISC Dynamics Analysis

```
## 1. Communication Style Alignment

For each interaction between participants:
- Where did communication styles align well?
- Where were there friction points due to style mismatch?
- Example: A high-D rep rushing through details with a high-C prospect

## 2. Style Adaptation Assessment

Did the rep adapt their style to match the prospect?

| Prospect Type | Ideal Adaptation | Did Rep Do This? |
|---------------|------------------|------------------|
| High-D | Be direct, focus on results, skip small talk | Y/N + evidence |
| High-I | Build rapport, share stories, show enthusiasm | Y/N + evidence |
| High-S | Slow down, emphasize stability, involve team | Y/N + evidence |
| High-C | Provide data, answer details, allow processing time | Y/N + evidence |

## 3. Missed Opportunities

Based on the prospect's DISC profile:
- What approach would have resonated better?
- Which objections were predictable given their type?
- How could pain points have been framed differently?

## 4. Visual Engagement by DISC Type

Review frames for type-specific engagement signals:

**High-D prospect signs of interest:**
- Leaning forward during ROI discussion
- Nodding at efficiency claims
- Impatience during setup/context

**High-I prospect signs of interest:**
- Animated reactions to success stories
- Engagement during collaborative discussion
- Excitement about vision/possibilities

**High-S prospect signs of interest:**
- Comfort signals during team impact discussion
- Relief when risks are addressed
- Engagement when hearing about support/training

**High-C prospect signs of interest:**
- Note-taking during specifications
- Engagement with data/proof points
- Thoughtful processing (may look disengaged but analyzing)
```

## Coaching Recommendations

```
## Tailored Communication Strategies

Based on the prospect's DISC profile, provide specific coaching:

### For High-D Prospects
- Lead with results and ROI
- Be concise—they'll ask if they want more
- Let them feel in control of the conversation
- Challenge them slightly (they respect pushback)
- Avoid: excessive small talk, too many details upfront

### For High-I Prospects
- Start with rapport and personal connection
- Share customer success stories
- Paint a vision of the future state
- Keep energy high and positive
- Avoid: diving into specs too early, being overly formal

### For High-S Prospects
- Don't rush—build trust gradually
- Emphasize how the team will be supported
- Address change management concerns proactively
- Provide reassurance about implementation
- Avoid: pushing for quick decisions, ignoring team impact

### For High-C Prospects
- Come prepared with data and documentation
- Answer questions thoroughly—they're evaluating competence
- Give them time to process (silence is okay)
- Acknowledge risks and how they're mitigated
- Avoid: overselling, vague claims, rushing analysis

## Specific Action Items for Next Call

Based on this analysis, the rep should:
1. [Specific adaptation for this prospect's type]
2. [Material/data to prepare based on their type]
3. [Topics to revisit framed for their type]
4. [Communication adjustments to make]
```

## Quick DISC Assessment

```
Quick DISC analysis of this call:

1. Prospect's likely DISC type: [D/I/S/C]
   Evidence: [2-3 signals from call]

2. Rep's apparent DISC type: [D/I/S/C]

3. Style compatibility: [High/Medium/Low]
   Why: [Brief explanation]

4. One thing to adapt for next call:
   [Specific recommendation based on DISC]
```

## Combined Analysis with Call Review

```
Integrate DISC insights with the call_review.json analysis:

1. **Pain Points by DISC Lens**
   - How did the prospect express pain? (D: frustration with inefficiency, I: impact on team morale, S: disruption concerns, C: quality/accuracy issues)
   - Which framing would resonate most for follow-up?

2. **Objections by DISC Lens**
   - Were objections type-predictable? (D: control/time, I: buy-in/excitement, S: change/risk, C: proof/details)
   - How should each be addressed given their type?

3. **Buying Signals by DISC Lens**
   - What would a buying signal look like for their type?
   - D: "Let's do it" / I: "The team will love this" / S: "This feels right" / C: "The numbers work"
   - Were these present?

4. **Next Steps Strategy**
   - Frame the follow-up for their DISC type
   - D: Clear decision timeline
   - I: Exciting next milestone
   - S: Comfortable next step with support
   - C: Detailed proposal for review
```
