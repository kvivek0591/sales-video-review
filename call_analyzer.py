#!/usr/bin/env python3
"""
Call Analyzer - Pattern Detection for Sales and Client Calls

Analyzes transcript data to detect:
- Pain points and challenges
- Objections and concerns
- Buying signals and interest indicators
- Action items and commitments
- Question classification (discovery vs confirmation)

Usage:
    python call_analyzer.py <index_json> [--call-type discovery|demo|checkin] [--output-dir <dir>]
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class DetectedPattern:
    """A detected pattern in the transcript."""
    pattern_type: str  # pain_point, objection, buying_signal, action_item
    text: str
    timestamp_seconds: float
    timestamp: str
    speaker_id: Optional[str]
    speaker_name: Optional[str]
    confidence: str  # high, medium, low
    matched_phrase: str


@dataclass
class Question:
    """A detected question with classification."""
    text: str
    timestamp_seconds: float
    timestamp: str
    speaker_id: Optional[str]
    speaker_name: Optional[str]
    question_type: str  # open_discovery, closed_confirmation, clarifying, rhetorical


# Pattern dictionaries with phrases to match
PAIN_POINT_PATTERNS = [
    (r'\b(our biggest challenge|our main challenge|biggest problem)\b', 'high'),
    (r'\b(we struggle with|we\'re struggling with|struggling to)\b', 'high'),
    (r'\b(pain point|frustrating|frustration)\b', 'high'),
    (r'\b(taking too long|takes too long|too slow)\b', 'medium'),
    (r'\b(difficult to|hard to|challenging to)\b', 'medium'),
    (r'\b(can\'t|cannot|unable to)\b', 'medium'),
    (r'\b(wasting time|waste of time|time consuming)\b', 'medium'),
    (r'\b(inefficient|inefficiency|bottleneck)\b', 'medium'),
    (r'\b(problem is|issue is|challenge is)\b', 'medium'),
    (r'\b(keeps breaking|breaks often|unreliable)\b', 'medium'),
    (r'\b(manual process|manually|by hand)\b', 'low'),
    (r'\b(outdated|legacy|old system)\b', 'low'),
    (r'\b(workaround|hack|band-aid)\b', 'low'),
]

OBJECTION_PATTERNS = [
    (r'\b(we\'ve tried|we tried|tried before)\b', 'high'),
    (r'\b(budget|too expensive|cost too much|can\'t afford)\b', 'high'),
    (r'\b(not sure if|not convinced|skeptical)\b', 'high'),
    (r'\b(need to think|think about it|consider it)\b', 'high'),
    (r'\b(talk to my|check with my|run it by)\b', 'high'),
    (r'\b(already have|currently using|existing solution)\b', 'medium'),
    (r'\b(too complex|too complicated|learning curve)\b', 'medium'),
    (r'\b(don\'t have time|no bandwidth|too busy)\b', 'medium'),
    (r'\b(not a priority|lower priority|back burner)\b', 'medium'),
    (r'\b(contract|locked in|commitment)\b', 'medium'),
    (r'\b(security concerns|compliance|regulations)\b', 'medium'),
    (r'\b(integration|doesn\'t integrate|compatibility)\b', 'low'),
    (r'\b(not now|maybe later|down the road)\b', 'low'),
]

BUYING_SIGNAL_PATTERNS = [
    (r'\b(what\'s the next step|next steps|how do we proceed)\b', 'high'),
    (r'\b(how quickly|how soon|when can we|timeline)\b', 'high'),
    (r'\b(what\'s the pricing|how much|cost|investment)\b', 'high'),
    (r'\b(can you send|send me|share with me)\b', 'high'),
    (r'\b(implementation|onboarding|getting started)\b', 'high'),
    (r'\b(pilot|trial|proof of concept|poc)\b', 'high'),
    (r'\b(decision maker|who else|stakeholder)\b', 'medium'),
    (r'\b(exactly what we need|perfect for|solves our)\b', 'medium'),
    (r'\b(impressive|love that|like that|that\'s great)\b', 'medium'),
    (r'\b(compared to|versus|vs|better than)\b', 'medium'),
    (r'\b(case study|reference|customer example)\b', 'medium'),
    (r'\b(tell me more|elaborate|explain)\b', 'low'),
    (r'\b(interesting|intriguing|curious)\b', 'low'),
]

ACTION_ITEM_PATTERNS = [
    (r'\b(i\'ll send|i will send|let me send)\b', 'high'),
    (r'\b(let\'s schedule|schedule a|set up a)\b', 'high'),
    (r'\b(by friday|by monday|by end of|by next week)\b', 'high'),
    (r'\b(follow up|following up|reach out)\b', 'high'),
    (r'\b(action item|to-do|task)\b', 'high'),
    (r'\b(i\'ll check|let me check|look into)\b', 'medium'),
    (r'\b(get back to you|circle back|touch base)\b', 'medium'),
    (r'\b(put together|prepare|draft)\b', 'medium'),
    (r'\b(introduce you to|connect you with|loop in)\b', 'medium'),
    (r'\b(share with the team|discuss internally|talk to)\b', 'low'),
]

# Question classification patterns
OPEN_DISCOVERY_PATTERNS = [
    r'^(what|how|why|tell me|describe|explain|walk me through)',
    r'^(can you tell|could you explain|would you describe)',
    r'(what does|what do you|what are|what is your)',
    r'(how does|how do you|how are)',
]

CLOSED_CONFIRMATION_PATTERNS = [
    r'^(is it|are you|do you|does it|can you|will you|would you)',
    r'^(have you|has it|did you)',
    r'(right\?|correct\?|yes\?|no\?)',
    r'^(so you\'re saying|so it\'s|so this)',
]

CLARIFYING_PATTERNS = [
    r'(what do you mean|could you clarify|can you elaborate)',
    r'(did you say|are you saying|do you mean)',
    r'(sorry|pardon|excuse me|come again)',
]


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def detect_patterns(text: str, patterns: list[tuple[str, str]], pattern_type: str,
                   timestamp_seconds: float, speaker_id: Optional[str],
                   speaker_name: Optional[str]) -> list[DetectedPattern]:
    """Detect patterns in text and return matches."""
    detected = []
    text_lower = text.lower()

    for pattern, confidence in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            detected.append(DetectedPattern(
                pattern_type=pattern_type,
                text=text,
                timestamp_seconds=timestamp_seconds,
                timestamp=seconds_to_timestamp(timestamp_seconds),
                speaker_id=speaker_id,
                speaker_name=speaker_name,
                confidence=confidence,
                matched_phrase=match.group(0)
            ))
            break  # Only count each segment once per pattern type

    return detected


def classify_question(text: str) -> Optional[str]:
    """Classify a question by type."""
    text_lower = text.lower().strip()

    # Check if it's actually a question
    if '?' not in text:
        return None

    for pattern in CLARIFYING_PATTERNS:
        if re.search(pattern, text_lower):
            return 'clarifying'

    for pattern in OPEN_DISCOVERY_PATTERNS:
        if re.search(pattern, text_lower):
            return 'open_discovery'

    for pattern in CLOSED_CONFIRMATION_PATTERNS:
        if re.search(pattern, text_lower):
            return 'closed_confirmation'

    # Default to rhetorical if has question mark but doesn't match patterns
    return 'rhetorical'


def analyze_transcript(frames: list[dict]) -> dict:
    """Analyze frames data for patterns and questions."""
    pain_points = []
    objections = []
    buying_signals = []
    action_items = []
    questions = []

    seen_texts = set()  # Avoid duplicate analysis of same text

    for frame in frames:
        text = frame.get('transcript_segment', '')
        if not text or text == '[No transcript available]':
            continue

        # Skip if we've already analyzed this exact text
        if text in seen_texts:
            continue
        seen_texts.add(text)

        timestamp_seconds = frame.get('timestamp_seconds', 0)
        speaker_id = frame.get('speaker_id')
        speaker_name = frame.get('speaker_name')

        # Detect patterns
        pain_points.extend(detect_patterns(
            text, PAIN_POINT_PATTERNS, 'pain_point',
            timestamp_seconds, speaker_id, speaker_name
        ))

        objections.extend(detect_patterns(
            text, OBJECTION_PATTERNS, 'objection',
            timestamp_seconds, speaker_id, speaker_name
        ))

        buying_signals.extend(detect_patterns(
            text, BUYING_SIGNAL_PATTERNS, 'buying_signal',
            timestamp_seconds, speaker_id, speaker_name
        ))

        action_items.extend(detect_patterns(
            text, ACTION_ITEM_PATTERNS, 'action_item',
            timestamp_seconds, speaker_id, speaker_name
        ))

        # Classify questions
        question_type = classify_question(text)
        if question_type:
            questions.append(Question(
                text=text,
                timestamp_seconds=timestamp_seconds,
                timestamp=seconds_to_timestamp(timestamp_seconds),
                speaker_id=speaker_id,
                speaker_name=speaker_name,
                question_type=question_type
            ))

    return {
        'pain_points': pain_points,
        'objections': objections,
        'buying_signals': buying_signals,
        'action_items': action_items,
        'questions': questions
    }


def generate_call_review(index_data: dict, call_type: str = 'discovery') -> dict:
    """Generate comprehensive call review from index data."""

    video_file = index_data.get('video_file', 'unknown')
    duration = index_data.get('duration_seconds', 0)
    frames = index_data.get('frames', [])
    speaker_analysis = index_data.get('speaker_analysis', {})

    # Analyze transcript patterns
    analysis = analyze_transcript(frames)

    # Count questions by type
    question_counts = {}
    for q in analysis['questions']:
        qtype = q.question_type
        question_counts[qtype] = question_counts.get(qtype, 0) + 1

    # Build the call review structure
    review = {
        'call_metadata': {
            'video_file': video_file,
            'duration_seconds': duration,
            'call_type': call_type,
            'analysis_version': '1.0'
        },
        'speaker_analysis': speaker_analysis,
        'transcript_analysis': {
            'questions_asked': {
                'total': len(analysis['questions']),
                'by_type': question_counts,
                'details': [asdict(q) for q in analysis['questions']]
            },
            'pain_points_identified': {
                'total': len(analysis['pain_points']),
                'high_confidence': len([p for p in analysis['pain_points'] if p.confidence == 'high']),
                'details': [asdict(p) for p in analysis['pain_points']]
            },
            'objections_detected': {
                'total': len(analysis['objections']),
                'high_confidence': len([o for o in analysis['objections'] if o.confidence == 'high']),
                'details': [asdict(o) for o in analysis['objections']]
            },
            'buying_signals': {
                'total': len(analysis['buying_signals']),
                'high_confidence': len([b for b in analysis['buying_signals'] if b.confidence == 'high']),
                'details': [asdict(b) for b in analysis['buying_signals']]
            },
            'action_items': {
                'total': len(analysis['action_items']),
                'details': [asdict(a) for a in analysis['action_items']]
            }
        },
        'visual_analysis': {
            'total_frames': len(frames),
            'engagement_timeline': [],  # To be filled by Claude analysis
            'notable_reactions': []  # To be filled by Claude analysis
        },
        'summary': {
            'key_metrics': {
                'duration_minutes': round(duration / 60, 1),
                'total_speakers': speaker_analysis.get('total_speakers', 0),
                'total_turns': speaker_analysis.get('total_turns', 0),
                'questions_asked': len(analysis['questions']),
                'pain_points_found': len(analysis['pain_points']),
                'objections_raised': len(analysis['objections']),
                'buying_signals_detected': len(analysis['buying_signals']),
                'action_items_identified': len(analysis['action_items'])
            },
            'call_health_indicators': generate_health_indicators(
                analysis, speaker_analysis, call_type
            )
        }
    }

    return review


def generate_health_indicators(analysis: dict, speaker_analysis: dict, call_type: str) -> dict:
    """Generate health indicators based on call type."""
    indicators = {}

    # Talk ratio analysis
    speakers = speaker_analysis.get('speakers', [])
    if len(speakers) >= 2:
        # Assume first speaker with highest talk time is one party
        sorted_speakers = sorted(speakers, key=lambda s: s.get('talk_time_pct', 0), reverse=True)
        top_speaker_pct = sorted_speakers[0].get('talk_time_pct', 50)

        if call_type == 'discovery':
            # In discovery, prospect should talk more (60%+)
            if top_speaker_pct < 40:
                indicators['talk_ratio'] = {
                    'status': 'needs_attention',
                    'message': 'Rep may be talking too much. In discovery calls, aim for prospect to talk 60%+ of the time.'
                }
            else:
                indicators['talk_ratio'] = {
                    'status': 'good',
                    'message': f'Good balance with top speaker at {top_speaker_pct}%'
                }
        elif call_type == 'demo':
            # In demos, more rep talking is expected
            indicators['talk_ratio'] = {
                'status': 'good',
                'message': f'Demo talk distribution: {top_speaker_pct}% for primary speaker'
            }

    # Question quality
    questions = analysis.get('questions', [])
    open_discovery = sum(1 for q in questions if q.question_type == 'open_discovery')
    closed = sum(1 for q in questions if q.question_type == 'closed_confirmation')

    if questions:
        open_ratio = open_discovery / len(questions)
        if call_type == 'discovery' and open_ratio < 0.4:
            indicators['question_quality'] = {
                'status': 'needs_attention',
                'message': f'Only {open_ratio*100:.0f}% open-ended questions. Consider more discovery questions.'
            }
        else:
            indicators['question_quality'] = {
                'status': 'good',
                'message': f'{open_ratio*100:.0f}% open-ended, {(1-open_ratio)*100:.0f}% closed questions'
            }

    # Pain point discovery
    pain_points = analysis.get('pain_points', [])
    if call_type == 'discovery':
        if len(pain_points) == 0:
            indicators['pain_discovery'] = {
                'status': 'needs_attention',
                'message': 'No clear pain points identified. Dig deeper into challenges.'
            }
        elif len(pain_points) >= 2:
            indicators['pain_discovery'] = {
                'status': 'good',
                'message': f'Identified {len(pain_points)} pain points'
            }
        else:
            indicators['pain_discovery'] = {
                'status': 'moderate',
                'message': 'One pain point identified. Consider exploring more.'
            }

    # Objection handling
    objections = analysis.get('objections', [])
    if objections:
        indicators['objections'] = {
            'status': 'attention_needed',
            'message': f'{len(objections)} objection(s) detected. Review handling in transcript.'
        }

    # Buying signals
    buying_signals = analysis.get('buying_signals', [])
    if buying_signals:
        high_signals = [b for b in buying_signals if b.confidence == 'high']
        indicators['buying_intent'] = {
            'status': 'positive',
            'message': f'{len(buying_signals)} buying signals detected ({len(high_signals)} high confidence)'
        }

    # Action items
    action_items = analysis.get('action_items', [])
    if action_items:
        indicators['next_steps'] = {
            'status': 'good',
            'message': f'{len(action_items)} action items identified'
        }
    else:
        indicators['next_steps'] = {
            'status': 'needs_attention',
            'message': 'No clear next steps identified. Ensure follow-up is defined.'
        }

    return indicators


def main():
    parser = argparse.ArgumentParser(
        description='Analyze call transcripts for patterns, objections, and buying signals.'
    )
    parser.add_argument('index_json', help='Path to index.json from video_processor')
    parser.add_argument('--call-type', '-c', choices=['discovery', 'demo', 'checkin'],
                        default='discovery', help='Type of call (default: discovery)')
    parser.add_argument('--output-dir', '-o', help='Output directory (default: same as index.json)')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.index_json):
        print(f"Error: Index file not found: {args.index_json}")
        sys.exit(1)

    # Load index data
    print(f"Loading index from: {args.index_json}")
    with open(args.index_json, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # Determine output directory
    output_dir = args.output_dir or os.path.dirname(args.index_json)

    # Generate call review
    print(f"Analyzing call (type: {args.call_type})...")
    review = generate_call_review(index_data, args.call_type)

    # Write call_review.json
    review_path = os.path.join(output_dir, 'call_review.json')
    with open(review_path, 'w', encoding='utf-8') as f:
        json.dump(review, f, indent=2, ensure_ascii=False)

    # Print summary
    summary = review['summary']['key_metrics']
    indicators = review['summary']['call_health_indicators']

    print(f"\n{'='*60}")
    print("Call Analysis Complete")
    print(f"{'='*60}")
    print(f"Duration: {summary['duration_minutes']} minutes")
    print(f"Speakers: {summary['total_speakers']}")
    print(f"Questions asked: {summary['questions_asked']}")
    print(f"Pain points found: {summary['pain_points_found']}")
    print(f"Objections raised: {summary['objections_raised']}")
    print(f"Buying signals: {summary['buying_signals_detected']}")
    print(f"Action items: {summary['action_items_identified']}")

    print(f"\nHealth Indicators:")
    for key, indicator in indicators.items():
        status_icon = {'good': '+', 'positive': '+', 'moderate': '~',
                      'needs_attention': '!', 'attention_needed': '!'}.get(indicator['status'], '?')
        print(f"  [{status_icon}] {key}: {indicator['message']}")

    print(f"\nOutput: {review_path}")
    print(f"{'='*60}\n")

    return review


if __name__ == '__main__':
    main()
