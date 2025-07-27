

def create_map_reduce_timeline_prompt():
    """Create a prompt for Map-Reduce timeline extraction method"""
    return """Extract and organize all chronological events from the following text into a clear timeline with bullet points.

CRITICAL REQUIREMENTS:
1. Use EXACT times as mentioned in the text (e.g., "7:12 PM" not "around 7 PM")
2. Include specific actions and details (e.g., "shut down work laptop" not "finished work")
3. Maintain chronological order precisely
4. Include all time markers mentioned
5. Be specific about who did what action
6. Focus on all significant events and actions mentioned
7. CAPTURE CONTEXT CLUES: Include descriptive details like "while still half-asleep", "Early morning", "phone buzzed"
8. PRESERVE COMPLETE CONTEXT: Don't just extract actions, include the full context of how/when events occurred
9. INCLUDE DESCRIPTIVE PHRASES: Capture phrases like "Early morning (while still half-asleep)" as complete timeline entries

Format the timeline as:
• [EXACT TIME] - [SPECIFIC ACTION/EVENT WITH CONTEXT]
• [EXACT TIME] - [SPECIFIC ACTION/EVENT WITH CONTEXT]
• [EXACT TIME] - [SPECIFIC ACTION/EVENT WITH CONTEXT]

If a time is not specified, use "Time not specified" but still include the event with full context.

EXAMPLES OF GOOD TIMELINE ENTRIES:
• "Early morning (while still half-asleep) - Phone buzzed with low-priority alert notification"
• "7:12 PM - Shut down work laptop after dealing with backlog tickets"
• "Time not specified - Received alert notification while still half-asleep"

Text to analyze:
{text}

Timeline:"""

def create_refine_timeline_prompt():
    """Create a prompt for Refine timeline method - improves existing timeline with new information"""
    return """You have an existing timeline summary and new information. Improve the timeline by:

PRECISION REQUIREMENTS:
1. Use EXACT times from the text (no approximations)
2. Include specific details and actions
3. Maintain chronological order
4. Add new events with precise timing
5. Correct any inaccuracies in the existing timeline
6. Be specific about actions and outcomes
7. Focus on all significant events and actions mentioned
8. Preserve existing accurate information while adding new details
9. CAPTURE CONTEXT CLUES: Include descriptive details like "while still half-asleep", "Early morning", "phone buzzed"
10. PRESERVE COMPLETE CONTEXT: Don't just extract actions, include the full context of how/when events occurred
11. INCLUDE DESCRIPTIVE PHRASES: Capture phrases like "Early morning (while still half-asleep)" as complete timeline entries

EXAMPLES OF GOOD TIMELINE ENTRIES:
• "Early morning (while still half-asleep) - Phone buzzed with low-priority alert notification"
• "7:12 PM - Shut down work laptop after dealing with backlog tickets"
• "Time not specified - Received alert notification while still half-asleep"

Existing timeline:
{existing_summary}

New information to add:
{text}

Improved timeline (maintain bullet point format):"""

def create_merge_timeline_prompt():
    """Create a prompt for merging multiple timeline summaries (used in Map-Reduce method)"""
    return """Merge these timeline summaries into one comprehensive chronological timeline with bullet points.

MERGE REQUIREMENTS:
1. Use EXACT times from all sources
2. Eliminate duplicates while preserving all unique events
3. Maintain precise chronological order
4. Include specific actions and details
5. Resolve any time conflicts by using the most specific time mentioned
6. Format as bullet points with exact times
7. Focus on all significant events and actions mentioned
8. Ensure all critical events are preserved
9. CAPTURE CONTEXT CLUES: Include descriptive details like "while still half-asleep", "Early morning", "phone buzzed"
10. PRESERVE COMPLETE CONTEXT: Don't just extract actions, include the full context of how/when events occurred
11. INCLUDE DESCRIPTIVE PHRASES: Capture phrases like "Early morning (while still half-asleep)" as complete timeline entries

EXAMPLES OF GOOD TIMELINE ENTRIES:
• "Early morning (while still half-asleep) - Phone buzzed with low-priority alert notification"
• "7:12 PM - Shut down work laptop after dealing with backlog tickets"
• "Time not specified - Received alert notification while still half-asleep"

Timeline summaries to merge:
{text}

Merged Timeline:""" 