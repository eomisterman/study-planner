# Study Planner Design Document

## Project Overview
A command-line tool that takes a video-based course outline (JSON format), daily study time limit, and start date to generate a balanced study schedule in Markdown format with checkboxes for progress tracking.

## Core Requirements (MVP)
- Parse JSON course outline with video lectures and quizzes
- Distribute content across weekdays only based on daily time limit
- Generate Markdown schedule with checkboxes for tracking progress
- Handle oversized content by splitting across multiple days
- Strict daily time limits (never exceed maximum)

## Input Format
**JSON Structure:**
```json
{
  "course_title": "AWS SAA Course",
  "sections": [
    {
      "title": "S3 Fundamentals",
      "items": [
        {"title": "S3 PreSigned URLs", "type": "video", "duration": "11:11"},
        {"title": "S3 Quiz", "type": "quiz", "duration": "15:00"}
      ]
    }
  ]
}
```

**Command Line Interface:**
```bash
python study_planner.py course.json 60 2024-01-15
```

## Design Decisions

### Time Management
- **Daily limit = pure content time** (no overhead calculation)
- **Strict time limits** - never exceed maximum daily minutes
- **Oversized content handling**: Split across multiple days
  - Final day rule: If remaining time ≤ 25% of daily limit, item gets full day
  - If remaining time > 25%, continue adding more content
- **Light days**: Left as-is, user decides whether to continue

### Scheduling Logic
- **Weekdays only** (Monday-Friday)
- **Start on given date** (if weekend, start following Monday)
- **Continuous scheduling** (no gaps between study days)
- **Linear progression** through course content

### Data Structure
- **Unified duration field** for both videos and quizzes (consistency)
- **Type field** maintained for future scheduling intelligence and analytics

### Output Format
**Markdown with checkboxes:**
```markdown
# Course Study Schedule

## Day 1 - Monday, January 15, 2024 (58 minutes)
- [ ] S3 PreSigned URLs (11:11)
- [ ] DEMO - Creating PresignedURLs (18:23)
```

## Input Validation

### Daily Limit Validation
- **Minimum**: 20 minutes (error with informative message)
- **4+ hours**: Random silly warning but proceed
  - "5 hours of studying? That's ambitious! Don't forget to blink occasionally."
  - "6 hours a day? Even marathon runners take breaks. But hey, you do you!"
  - "4.5 hours daily? I admire your enthusiasm, but remember - sleep is also important!"
- **Maximum**: 8 hours (error)

### Time Format Validation
- **Accept all variations**: "5:30", "05:30", "0:45", "00:45"
- **Error on invalid formats**: "25:99", "abc:def"

### Date Validation
- **Past dates**: Error with informative message
- **Invalid formats**: Error (e.g., "2024-13-45")
- **Weekend start dates**: Auto-adjust to following Monday

### JSON Structure Validation
- **Required top-level fields**: `course_title`, `sections`
- **Required section fields**: `title`, `items`
- **Required item fields**: `title`, `type`, `duration`
- **Error handling**: Malformed JSON, missing fields, empty course content

## Architecture

### MVP Architecture: Modular Pipeline
```python
def main():
    course_data = parse_course_json(input_file)
    scheduled_days = schedule_course(course_data, daily_limit, start_date)
    markdown = generate_markdown(scheduled_days)
    write_output(markdown)
```

**Rationale**: Simple, testable, focused scope. Easy to understand and maintain for MVP.

### Error Handling Strategy
- **Fail fast**: Validate all inputs before processing
- **Informative messages**: Clear error descriptions with examples
- **Graceful degradation**: Where possible, auto-correct minor issues (weekend → Monday)

## Future Development Ideas

### Enhanced Scheduling Features
- **Weekend inclusion option**: User preference for 7-day vs 5-day schedules
- **Holiday/blackout date support**: Skip specified dates
- **Flexible day selection**: "Never schedule on Sundays", custom patterns
- **Schedule adjustment tools**: Shift entire remaining schedule by X days
- **Restart from specific point**: Resume from any course section

### Advanced Time Management
- **Study session composition**: Balance video/quiz ratios per day
- **Buffer time options**: Add overhead factors for breaks, note-taking
- **Minimum/maximum gaps**: Control spacing between study sessions
- **Split content preferences**: Keep related videos together when possible

### Configuration System
- **YAML/JSON config files**: User preferences and defaults
- **Profile management**: Different configs for different courses/subjects
- **Custom scheduling rules**: "Always end sessions with videos", "Max 2 quizzes per day"

### Enhanced Output Formats
- **Calendar view**: Visual monthly/weekly layout
- **CSV export**: Import into spreadsheets or other tools
- **Multiple markdown styles**: Different formatting options
- **Progress tracking**: Completion percentages, time spent analytics

### User Experience Improvements
- **Interactive mode**: Guided setup with prompts
- **Schedule preview**: Show summary before generating full schedule
- **Validation warnings**: Highlight potential issues before processing
- **Multiple input formats**: Support CSV, YAML input alongside JSON

### Analytics and Reporting
- **Progress tracking**: Time spent vs. planned
- **Schedule adherence**: Days ahead/behind
- **Content type analysis**: Video vs. quiz time distribution
- **Study pattern insights**: Most productive days, completion rates

### Architecture Evolution
- **Class-based refactor**: Better state management for complex features
- **Plugin system**: Extensible scheduling algorithms
- **Database integration**: Persistent progress tracking
- **Web interface**: Browser-based schedule management

### Integration Possibilities
- **Calendar app sync**: Export to Google Calendar, Outlook
- **Note-taking integration**: Links to Obsidian, Notion
- **Learning management**: Connect with course platforms
- **Mobile companion**: Simple progress tracking app

## Technical Considerations

### Dependencies (MVP)
- `datetime`: Date calculations and validation
- `json`: Course data parsing
- `argparse`: Command-line interface
- Standard library only (no external dependencies)

### File Structure
```
study_planner.py          # Main pipeline script
sample_course.json        # Example input file
README.md                 # Usage instructions and examples
design_document.md        # This document
```

### Testing Strategy
- Unit tests for each pipeline component
- Input validation test cases
- Edge case handling (oversized content, light days)
- Sample course data for testing

## Success Metrics
- **Primary**: Successfully generates balanced study schedules
- **Secondary**: Handles edge cases gracefully with clear error messages
- **Tertiary**: Easy to use and understand for non-technical users

---

*This design document serves as the foundation for MVP development and roadmap for future enhancements.*