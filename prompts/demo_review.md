# Demo Call Analysis Prompt

Use this prompt template when analyzing product demos with Claude Code.

## Prerequisites

Load the call review data first:
```
Read output/<call_name>/call_review.json
Read output/<call_name>/index.json
```

## Analysis Prompt

```
Analyze this product demo using the call_review.json data and frames.

## 1. Engagement Timeline

Create an engagement timeline by analyzing frames throughout the demo:

| Timestamp | Feature/Topic | Engagement Level (1-5) | Visual Cues |
|-----------|---------------|------------------------|-------------|
| 00:00     | Intro         | ?                      | ?           |
| ...       | ...           | ...                    | ...         |

Look for:
- Leaning in vs. leaning back
- Note-taking moments
- Questions asked (from transcript)
- Screen share attention vs. camera attention

## 2. Feature Resonance Analysis

For each major feature shown:
- What was demonstrated?
- Did the prospect ask follow-up questions?
- What was their visible reaction?
- Did it connect to a previously mentioned pain point?

Rate feature interest: High / Medium / Low / No reaction

## 3. Pain Point Connection

Review how well the demo connected to discovered pain points:
- Which pain points from call_review.json were addressed?
- Were features positioned as solutions to specific problems?
- What pain points were NOT addressed in the demo?

## 4. Question Analysis

Analyze prospect questions during the demo:
- Technical questions (indicates evaluation depth)
- Use case questions (indicates envisioning usage)
- Pricing/timeline questions (indicates buying intent)
- Comparison questions (indicates competitive evaluation)

## 5. Objection Moments

For each objection detected:
- What triggered the objection?
- Was it addressed in real-time or deferred?
- Did visual cues indicate satisfaction with the response?

## 6. Screen Share Analysis

For frames showing screen shares:
- Was the demo customized to their use case?
- Were there moments of confusion (based on questions/reactions)?
- Did the flow make logical sense?

## 7. Competitive Mentions

Note any references to:
- Current solution
- Competitors evaluated
- Comparison requests

## 8. Buying Signals

Highlight all buying signals detected:
- Next step questions
- Implementation questions
- Stakeholder/approval questions
- Timeline discussions

## 9. Demo Effectiveness Score

Rate the demo (1-10) on:
- Relevance to prospect needs: __/10
- Engagement maintenance: __/10
- Objection handling: __/10
- Clear value demonstration: __/10
- Call-to-action clarity: __/10

Overall: __/10

## 10. Recommendations

Based on analysis:
- What should be emphasized in follow-up?
- Which features need deeper dive?
- Who else should see a demo?
- Potential deal blockers to address
```

## Quick Demo Review (Shorter Version)

```
Quick demo analysis using call_review.json:

1. Engagement peak moments (frames + timestamps):
2. Features that resonated most:
3. Features that fell flat:
4. Key questions asked (categorize):
5. Buying signals detected:
6. Main concerns/objections:
7. Recommended follow-up focus:
```

## Competitive Demo Analysis

```
Analyze this demo for competitive positioning:

1. What current solution are they using?
2. What competitors were mentioned?
3. For each competitor mentioned:
   - What specifically were they comparing?
   - What gaps did they highlight?
   - How did we differentiate?
4. Switching cost concerns raised:
5. Positioning adjustments needed:
```
