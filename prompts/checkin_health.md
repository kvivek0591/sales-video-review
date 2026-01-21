# Client Check-in Health Analysis Prompt

Use this prompt template when analyzing client health check-ins with Claude Code.

## Prerequisites

Load the call review data first:
```
Read output/<call_name>/call_review.json
Read output/<call_name>/index.json
```

## Analysis Prompt

```
Analyze this client check-in call using the call_review.json data and frames.

## 1. Relationship Health Score

Based on the conversation tone and content, assess:

| Dimension | Score (1-10) | Evidence |
|-----------|--------------|----------|
| Satisfaction | ? | ? |
| Engagement | ? | ? |
| Trust | ? | ? |
| Advocacy potential | ? | ? |

Overall Health Score: __/10

## 2. Satisfaction Signals

Positive indicators detected:
- Success stories shared
- Compliments or praise
- Referral/expansion mentions
- Feature appreciation

Negative indicators:
- Complaints or frustrations
- Comparisons to alternatives
- Unmet expectations
- Support escalations mentioned

## 3. Usage & Adoption Analysis

From the conversation, assess:
- How actively are they using the product?
- Which features are they leveraging?
- What's underutilized?
- Training/support needs indicated?

## 4. Expansion Opportunities

Detect signals for:
- New use cases mentioned
- Additional users/seats
- New departments or teams
- Complementary products/features
- Budget for growth

Quote relevant buying signals from call_review.json.

## 5. Risk Indicators

Churn risk assessment:
- Champion changes mentioned?
- Budget pressures?
- Competitive evaluations?
- Contract/renewal concerns?
- Declining usage mentioned?

Risk Level: Low / Medium / High

## 6. Visual Engagement Analysis

Throughout the check-in, analyze frames for:
- Overall demeanor: Friendly, neutral, frustrated?
- Energy level: Engaged, going through motions, distracted?
- Body language shifts: When did they lean in/back?

## 7. Pain Points & Requests

Catalog all feature requests and pain points:

| Item | Type | Priority (their view) | Impact |
|------|------|----------------------|--------|
| ? | Request/Pain | High/Med/Low | ? |

## 8. Action Items

From action_items detected:
- Our commitments:
- Their commitments:
- Deadlines established:
- Follow-up needed:

## 9. Stakeholder Mapping

Based on mentions in the call:
- Who else uses the product?
- Who are the power users?
- Who are the decision makers for renewal?
- New stakeholders to engage?

## 10. Health Trend

Compare to previous check-ins (if available):
- Improving / Stable / Declining
- Key changes noted
- Momentum direction

## 11. Recommended Actions

Based on analysis:
1. Immediate follow-ups needed:
2. Proactive engagement opportunities:
3. Risk mitigation steps:
4. Expansion plays to pursue:
5. Success stories to capture:
```

## Quick Health Check (Shorter Version)

```
Quick client health analysis using call_review.json:

1. Health Score (1-10): __ (justify)
2. Satisfaction signals (+/-):
3. Churn risk level (Low/Med/High):
4. Expansion opportunities:
5. Key action items:
6. One thing to do this week:
```

## Expansion-Focused Analysis

```
Analyze this check-in specifically for expansion opportunities:

1. Current usage scope:
   - Users/seats
   - Departments
   - Use cases

2. Expansion signals detected:
   - New teams mentioned
   - Additional use cases discussed
   - Positive ROI/value mentions
   - Champion enthusiasm level

3. Buying signals (from call_review.json):
   - List and assess each

4. Barriers to expansion:
   - Budget constraints
   - Approvals needed
   - Competing priorities

5. Recommended expansion strategy:
   - Timing
   - Approach
   - Stakeholders to engage
   - Value proposition to lead with
```

## At-Risk Account Analysis

```
Analyze this check-in for churn risk indicators:

1. Verbal risk signals:
   - Frustrations expressed
   - Competitor mentions
   - ROI questions
   - Usage decline admission

2. Non-verbal risk signals (from frames):
   - Disengaged body language
   - Short/curt responses
   - Lack of enthusiasm

3. Objections raised:
   - List from call_review.json
   - How were they addressed?

4. Champion health:
   - Still engaged?
   - Still has authority?
   - Organizational changes?

5. Risk mitigation plan:
   - Immediate actions
   - Escalation needed?
   - Executive engagement?
   - Value reinforcement needed?
```
