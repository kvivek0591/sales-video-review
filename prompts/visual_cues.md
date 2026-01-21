# Visual Cues Analysis Guide

Reference guide for analyzing visual cues in call frames with Claude Code.

## How to Analyze Frames

When Claude Code reads frames, look for these visual indicators to supplement transcript analysis.

### Loading Frames

```
Read output/<call_name>/frames/frame_0001.jpg
Read output/<call_name>/frames/frame_0025.jpg
```

Or read the index to know which frames to examine:
```
Read output/<call_name>/index.json
```

---

## Engagement Indicators

### High Engagement
- **Leaning forward**: Body angled toward camera/screen
- **Active eye contact**: Looking directly at camera or presenter
- **Nodding**: Head movement indicating agreement/understanding
- **Taking notes**: Writing, typing, or looking down at notes
- **Smiling/positive expression**: Genuine smile reaching eyes
- **Open posture**: Arms uncrossed, hands visible

### Low Engagement
- **Leaning back**: Distanced from camera/screen
- **Looking away**: Eyes on phone, other screen, or off-camera
- **Crossed arms**: Defensive or closed posture
- **Flat expression**: Neutral or bored appearance
- **Multitasking visible**: Typing unrelated to call, looking at phone
- **Fidgeting**: Playing with objects, frequent position shifts

---

## Emotional States

### Interest/Excitement
- Raised eyebrows
- Wide eyes
- Leaning in
- Taking notes suddenly
- Nodding enthusiastically

### Confusion
- Furrowed brow
- Tilted head
- Squinting at screen
- Looking at colleagues (if visible)
- Hand on chin/face

### Concern/Skepticism
- Furrowed brow
- Pursed lips
- Arms crossed
- Leaning back
- Looking away momentarily

### Agreement
- Nodding
- Smiling
- Open body language
- Verbal acknowledgment (check transcript)

### Frustration
- Tense jaw
- Frown
- Looking away
- Deep sighs (if visible)
- Rubbing temples/face

---

## Timing Correlation

### When to Check Frames

Cross-reference frames with transcript moments:

**Pain Point Discussions**
- Check frames when pain points are mentioned
- Look for: Recognition, nodding, frustration, relief

**Objection Moments**
- Check frames when objections are raised
- Look for: Concern before objection, skepticism during, resolution after

**Feature Demonstrations**
- Check frames during key feature reveals
- Look for: Interest, confusion, note-taking, questions

**Pricing Discussions**
- Check frames when cost is discussed
- Look for: Concern, calculation face, acceptance

**Next Steps**
- Check frames during closing
- Look for: Engagement, enthusiasm, hesitation

---

## Analysis Prompt Template

```
Analyze visual engagement in this call by examining key frames.

For each frame, note:
1. Frame filename and timestamp
2. Participant positions/postures
3. Facial expressions visible
4. Body language indicators
5. Environment/background context
6. Correlation with transcript at that moment

Focus on frames at these key moments:
- [List timestamps from pain_points in call_review.json]
- [List timestamps from objections in call_review.json]
- [List timestamps from buying_signals in call_review.json]
```

---

## Multi-Person Calls

When analyzing calls with multiple participants:

### Layout Analysis
- Who is visible?
- How are they positioned?
- Who appears to be the primary contact?

### Group Dynamics
- Who reacts to whom?
- Side conversations visible?
- Deference patterns (looking to someone before speaking)

### Champion Identification
- Who shows most enthusiasm?
- Who asks the most engaged questions?
- Who takes notes?

### Skeptic Identification
- Who shows most skepticism?
- Who remains disengaged?
- Who asks challenging questions?

---

## Screen Share Frames

When the frame shows a screen share:

### What to Note
- What's being shown?
- Is it customized to their context?
- Can you see their reaction (if picture-in-picture)?

### Engagement During Screen Share
- Are they focused on the screen?
- Are they distracted/multitasking?
- Did they switch their video off?

---

## Environmental Context

### Professional Indicators
- Office environment vs. home
- Meeting room vs. desk
- Quality of setup (lighting, camera, background)

### Attention Indicators
- Distractions visible?
- Interruptions (people walking by, notifications)?
- Multi-monitor setup (might be looking elsewhere)?

---

## Creating an Engagement Timeline

Use this template to create a visual engagement timeline:

```
| Timestamp | Frame | Topic (from transcript) | Engagement | Notes |
|-----------|-------|------------------------|------------|-------|
| 00:00:30 | frame_0006.jpg | Introduction | 4/5 | Smiling, open posture |
| 00:02:15 | frame_0027.jpg | Pain discussion | 5/5 | Leaning in, nodding |
| 00:05:45 | frame_0069.jpg | Pricing | 3/5 | Leaned back, arms crossed |
| ... | ... | ... | ... | ... |
```

Plot this to identify:
- High points to replicate
- Low points to address
- Pattern changes to investigate
