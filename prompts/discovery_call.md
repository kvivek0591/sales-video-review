# Discovery Call Analysis Prompt

Use this prompt template when analyzing discovery calls with Claude Code.

## Prerequisites

Load the call review data first:
```
Read output/<call_name>/call_review.json
Read output/<call_name>/index.json
```

## Analysis Prompt

```
Analyze this discovery call using the call_review.json data and frames.

## 1. Pain Point Analysis

Review the detected pain points and answer:
- What are the prospect's top 3 pain points by severity?
- Which pain points were explicitly stated vs. implied?
- Were there pain points mentioned that the automated detection missed?
- How deeply did the rep explore each pain point?

## 2. Qualification Assessment

Based on the transcript, evaluate:
- **Budget**: Were budget/investment discussions initiated? By whom?
- **Authority**: Who are the decision makers? Was this clarified?
- **Need**: How urgent is the problem? What happens if unsolved?
- **Timeline**: What's driving their timeline? Any hard deadlines?

Provide a qualification score (1-5) with justification.

## 3. Discovery Quality

Analyze the questioning approach:
- Ratio of open vs. closed questions
- Did the rep uncover root causes or stay surface-level?
- Were there missed opportunities to dig deeper?
- How well did questions flow from previous answers?

## 4. Objection Handling

For each detected objection:
- What was the objection?
- How did the rep respond?
- Was the objection fully addressed or just acknowledged?
- Suggested improvement for handling

## 5. Visual Engagement Analysis

Review frames during key moments:
- Pain point discussions: What was the prospect's body language?
- Objection moments: Did visual cues indicate concerns before verbal objection?
- Feature discussions: Which features generated visible interest?

Reference specific frames: "At frame_0045.jpg (timestamp 03:45), the prospect..."

## 6. Talk Ratio Assessment

Review speaker_analysis metrics:
- What percentage did each party speak?
- In discovery, the prospect should talk 60%+ of the time
- If rep talked too much, which segments could have been questions instead?

## 7. Next Steps Clarity

Based on action items detected:
- Were clear next steps established?
- Who owns each action item?
- Are there implicit commitments that should be explicit?

## 8. Recommendations

Provide 3-5 specific, actionable recommendations for:
- Follow-up messaging/positioning
- Topics to explore in next call
- Stakeholders to involve
- Potential objections to prepare for
```

## Quick Analysis (Shorter Version)

```
Quick discovery call review using call_review.json:

1. Top pain points found (with confidence):
2. Qualification signals (BANT):
3. Talk ratio assessment:
4. Key objections and how handled:
5. Clear next steps established? Y/N
6. One thing to do differently next call:
```

## Frame-Specific Analysis

```
Analyze frames during these key moments in the discovery call:

1. First 2 minutes (rapport building):
   - Review frames 1-5 for initial engagement
   - Body language: open/closed? Engaged/distracted?

2. Pain point revelation moments:
   - [Reference timestamps from pain_points_identified]
   - Look for: leaning in, nodding, frustration expressions

3. Objection moments:
   - [Reference timestamps from objections_detected]
   - Look for: crossed arms, leaning back, furrowed brow

4. Interest/buying signal moments:
   - [Reference timestamps from buying_signals]
   - Look for: leaning forward, taking notes, smiling
```
