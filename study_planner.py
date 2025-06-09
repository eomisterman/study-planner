#!/usr/bin/env python3
"""
Study Planner - Transform video course outlines into balanced study schedules.

A command-line tool that takes JSON course outlines and generates Markdown
study schedules with progress tracking checkboxes.
"""

import argparse
import json
import sys
import re
from datetime import datetime, timedelta


def validate_daily_limit(minutes):
    """Validate daily study time limit with amusing warnings for extreme values."""
    print(f"   ⏰ Validating daily limit: {minutes} minutes")
    
    # Check for minimum 20 minutes
    if minutes < 20:
        print(f"   ❌ Error: Daily limit too low: {minutes} minutes")
        print("   Minimum study time is 20 minutes per day.")
        print("   Even a short daily session helps build momentum!")
        sys.exit(1)
    
    # Check for maximum 8 hours (480 minutes)
    if minutes > 480:
        print(f"   ❌ Error: Daily limit too high: {minutes} minutes ({minutes/60:.1f} hours)")
        print("   Maximum study time is 8 hours (480 minutes) per day.")
        print("   Remember: sustainable learning beats burnout every time!")
        sys.exit(1)
    
    # Amusing warnings for 4+ hours (240+ minutes)
    if minutes >= 240:
        hours = minutes / 60
        print(f"   ⚠️  High intensity detected: {minutes} minutes ({hours:.1f} hours/day)")
        if minutes >= 360:  # 6+ hours
            print("   🔥 That's some serious dedication! Make sure to:")
            print("      • Take regular breaks every hour")
            print("      • Stay hydrated and eat well")
            print("      • Get enough sleep for retention")
        elif minutes >= 300:  # 5+ hours
            print("   📚 Marathon study mode activated!")
            print("      • Remember to take breaks")
            print("      • Consider splitting into morning/evening sessions")
        else:  # 4+ hours
            print("   💪 Ambitious goals! Don't forget to pace yourself.")
    
    print(f"   ✅ Daily limit validated: {minutes} minutes ({minutes/60:.1f} hours)")
    return minutes


def validate_start_date(date_string):
    """Parse and validate start date with auto-correction for weekends."""
    print(f"   📅 Validating start date: {date_string}")
    
    # Check basic format first
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, date_string):
        print(f"   ❌ Error: Invalid date format: {date_string}")
        print("   Please use YYYY-MM-DD format (e.g., 2024-01-15)")
        sys.exit(1)
    
    # Parse the date
    try:
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError as e:
        print(f"   ❌ Error: Invalid date: {date_string}")
        print("   Please check that the month (01-12) and day are valid.")
        print("   Example: 2024-01-15 (January 15, 2024)")
        sys.exit(1)
    
    # Check if date is in the past
    today = datetime.now().date()
    if parsed_date < today:
        print(f"   ❌ Error: Start date cannot be in the past: {date_string}")
        print(f"   Today is {today.strftime('%Y-%m-%d')}")
        print("   Please choose today's date or a future date.")
        sys.exit(1)
    
    # Auto-correct weekend dates to following Monday
    weekday = parsed_date.weekday()  # Monday = 0, Sunday = 6
    if weekday == 5:  # Saturday
        corrected_date = parsed_date + timedelta(days=2)
        print(f"   📅 Weekend date detected: {date_string} is a Saturday")
        print(f"   🔄 Auto-corrected to following Monday: {corrected_date.strftime('%Y-%m-%d')}")
        return corrected_date
    elif weekday == 6:  # Sunday
        corrected_date = parsed_date + timedelta(days=1)
        print(f"   📅 Weekend date detected: {date_string} is a Sunday")
        print(f"   🔄 Auto-corrected to following Monday: {corrected_date.strftime('%Y-%m-%d')}")
        return corrected_date
    else:
        # Weekday - use as-is
        weekday_name = parsed_date.strftime('%A')
        print(f"   ✅ Valid weekday: {date_string} ({weekday_name})")
        return parsed_date


def parse_duration(duration_str):
    """Parse duration string (MM:SS format) and convert to minutes."""
    # Remove whitespace
    duration_str = duration_str.strip()
    
    # Check format: MM:SS or M:SS
    duration_pattern = r'^(\d{1,2}):(\d{2})$'
    match = re.match(duration_pattern, duration_str)
    
    if not match:
        raise ValueError(f"Invalid duration format: '{duration_str}'. Expected MM:SS (e.g., '15:30', '05:45')")
    
    minutes = int(match.group(1))
    seconds = int(match.group(2))
    
    # Validate seconds (0-59)
    if seconds >= 60:
        raise ValueError(f"Invalid seconds in duration: '{duration_str}'. Seconds must be 00-59")
    
    # Convert to total minutes (rounded up if seconds > 0)
    total_minutes = minutes
    if seconds > 0:
        total_minutes += 1  # Round up for any partial minute
    
    return total_minutes


def validate_course_structure(course_data):
    """Validate the overall structure of the course data."""
    if not isinstance(course_data, dict):
        raise ValueError(f"Course file must contain a JSON object, got {type(course_data).__name__}")
    
    # Check required top-level fields
    if 'course_title' not in course_data:
        raise ValueError("Missing required field: 'course_title'")
    
    if 'sections' not in course_data:
        raise ValueError("Missing required field: 'sections'")
    
    # Validate course_title
    if not isinstance(course_data['course_title'], str) or not course_data['course_title'].strip():
        raise ValueError("Field 'course_title' must be a non-empty string")
    
    # Validate sections
    if not isinstance(course_data['sections'], list):
        raise ValueError("Field 'sections' must be a list")
    
    if len(course_data['sections']) == 0:
        raise ValueError("Course must have at least one section")
    
    return True


def validate_section(section, section_index):
    """Validate a single section structure."""
    if not isinstance(section, dict):
        raise ValueError(f"Section {section_index + 1} must be an object, got {type(section).__name__}")
    
    # Check required fields
    if 'title' not in section:
        raise ValueError(f"Section {section_index + 1}: Missing required field 'title'")
    
    if 'items' not in section:
        raise ValueError(f"Section {section_index + 1}: Missing required field 'items'")
    
    # Validate title
    if not isinstance(section['title'], str) or not section['title'].strip():
        raise ValueError(f"Section {section_index + 1}: Field 'title' must be a non-empty string")
    
    # Validate items
    if not isinstance(section['items'], list):
        raise ValueError(f"Section {section_index + 1}: Field 'items' must be a list")
    
    if len(section['items']) == 0:
        raise ValueError(f"Section {section_index + 1} ('{section['title']}'): Must have at least one item")
    
    return True


def validate_item(item, section_title, item_index):
    """Validate a single item structure."""
    if not isinstance(item, dict):
        raise ValueError(f"Section '{section_title}', Item {item_index + 1}: Must be an object, got {type(item).__name__}")
    
    # Check required fields
    required_fields = ['title', 'type', 'duration']
    for field in required_fields:
        if field not in item:
            raise ValueError(f"Section '{section_title}', Item {item_index + 1}: Missing required field '{field}'")
    
    # Validate title
    if not isinstance(item['title'], str) or not item['title'].strip():
        raise ValueError(f"Section '{section_title}', Item {item_index + 1}: Field 'title' must be a non-empty string")
    
    # Validate type
    if not isinstance(item['type'], str) or not item['type'].strip():
        raise ValueError(f"Section '{section_title}', Item {item_index + 1}: Field 'type' must be a non-empty string")
    
    # Validate duration
    if not isinstance(item['duration'], str) or not item['duration'].strip():
        raise ValueError(f"Section '{section_title}', Item {item_index + 1}: Field 'duration' must be a non-empty string")
    
    # Parse and validate duration format
    try:
        duration_minutes = parse_duration(item['duration'])
        if duration_minutes <= 0:
            raise ValueError(f"Section '{section_title}', Item {item_index + 1}: Duration must be greater than 0 minutes")
    except ValueError as e:
        raise ValueError(f"Section '{section_title}', Item {item_index + 1}: {str(e)}")
    
    return duration_minutes


def parse_course_json(input_file):
    """Parse and validate JSON course file."""
    print(f"📖 Parsing course file: {input_file}")
    
    try:
        # Read and parse JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        print("   ✅ JSON file loaded successfully")
        
        # Validate overall structure
        validate_course_structure(course_data)
        print("   ✅ Course structure validated")
        
        # Process and validate each section
        total_items = 0
        total_duration_minutes = 0
        
        for section_index, section in enumerate(course_data['sections']):
            # Validate section structure
            validate_section(section, section_index)
            
            # Process items in this section
            section_duration = 0
            for item_index, item in enumerate(section['items']):
                # Validate item structure and get duration
                item_duration = validate_item(item, section['title'], item_index)
                
                # Add duration to item for later use
                item['duration_minutes'] = item_duration
                section_duration += item_duration
                total_items += 1
            
            # Add section metadata
            section['total_duration_minutes'] = section_duration
            total_duration_minutes += section_duration
            
            print(f"   ✅ Section '{section['title']}': {len(section['items'])} items, {section_duration} minutes")
        
        # Add course metadata
        course_data['total_items'] = total_items
        course_data['total_duration_minutes'] = total_duration_minutes
        
        print("   📊 Course Summary:")
        print(f"      Title: {course_data['course_title']}")
        print(f"      Sections: {len(course_data['sections'])}")
        print(f"      Total Items: {total_items}")
        print(f"      Total Duration: {total_duration_minutes} minutes ({total_duration_minutes/60:.1f} hours)")
        
        return course_data
        
    except FileNotFoundError:
        print(f"   ❌ Error: Course file not found: {input_file}")
        raise
    except json.JSONDecodeError as e:
        print(f"   ❌ Error: Invalid JSON format in {input_file}")
        print(f"      {str(e)}")
        raise
    except ValueError as e:
        print(f"   ❌ Error: Invalid course structure in {input_file}")
        print(f"      {str(e)}")
        raise
    except Exception as e:
        print(f"   ❌ Error: Failed to parse course file: {str(e)}")
        raise


def generate_weekday_sequence(start_date, num_days_needed):
    """Generate sequence of weekday dates starting from start_date."""
    weekdays = []
    current_date = start_date
    days_added = 0
    
    while days_added < num_days_needed:
        # Only add weekdays (Monday=0 to Friday=4)
        if current_date.weekday() < 5:
            weekdays.append(current_date)
            days_added += 1
        current_date += timedelta(days=1)
    
    return weekdays


def create_split_item(original_item, part_number, total_parts, duration_minutes):
    """Create a split item with proper labeling."""
    split_item = original_item.copy()
    split_item['title'] = f"{original_item['title']} (Part {part_number}/{total_parts})"
    split_item['duration_minutes'] = duration_minutes
    split_item['is_split'] = True
    split_item['original_title'] = original_item['title']
    split_item['part_number'] = part_number
    split_item['total_parts'] = total_parts
    return split_item


def handle_oversized_item(item, daily_limit, remaining_time_today):
    """
    Handle items that exceed daily limit using the 25% rule.
    
    Returns tuple: (items_for_today, items_for_future_days)
    """
    item_duration = item['duration_minutes']
    
    # Check if item exceeds daily limit
    if item_duration <= daily_limit:
        # Item fits within daily limit, normal handling
        return ([item], [])
    
    # Item exceeds daily limit - needs splitting
    print(f"   🔧 Oversized item detected: '{item['title']}' ({item_duration}min > {daily_limit}min limit)")
    
    # Apply 25% rule for current day
    quarter_limit = daily_limit * 0.25
    
    if remaining_time_today <= quarter_limit:
        # Remaining time is ≤ 25% of daily limit → give item full day(s)
        print(f"   📊 25% rule applied: {remaining_time_today}min remaining ≤ {quarter_limit:.1f}min (25% of {daily_limit}min)")
        print(f"   🎯 Item will get dedicated day(s)")
        items_for_today = []
        items_for_future = [item]  # Will be split across future days
    else:
        # Remaining time > 25% → continue adding content to current day
        print(f"   📊 25% rule applied: {remaining_time_today}min remaining > {quarter_limit:.1f}min (25% of {daily_limit}min)")
        print(f"   ➕ Adding partial content to current day")
        
        # Split item: part for today + remainder for future
        today_duration = remaining_time_today
        future_duration = item_duration - today_duration
        
        # Create split items
        today_item = create_split_item(item, 1, 2, today_duration)
        future_item = create_split_item(item, 2, 2, future_duration)
        
        items_for_today = [today_item]
        items_for_future = [future_item]
    
    # Handle items that still exceed daily limit for future days
    final_future_items = []
    for future_item in items_for_future:
        if future_item['duration_minutes'] > daily_limit:
            # Split large item across multiple full days
            total_duration = future_item['duration_minutes']
            num_full_days = total_duration // daily_limit
            remainder = total_duration % daily_limit
            
            total_parts = num_full_days + (1 if remainder > 0 else 0)
            
            print(f"   ✂️  Splitting '{future_item.get('original_title', future_item['title'])}' across {total_parts} days")
            
            # Create parts
            for part in range(total_parts):
                if part < num_full_days:
                    # Full day part
                    part_duration = daily_limit
                else:
                    # Remainder part
                    part_duration = remainder
                
                if 'is_split' in future_item and future_item['is_split']:
                    # This is already a split item, update numbering
                    base_title = future_item['original_title']
                    part_num = part + future_item['part_number']
                    total_parts_adjusted = future_item['total_parts'] + total_parts - 1
                else:
                    # First time splitting
                    base_title = future_item['title']
                    part_num = part + 1
                    total_parts_adjusted = total_parts
                
                split_part = create_split_item(future_item, part_num, total_parts_adjusted, part_duration)
                final_future_items.append(split_part)
        else:
            # Item fits in daily limit
            final_future_items.append(future_item)
    
    return (items_for_today, final_future_items)


def schedule_course(course_data, daily_limit, start_date):
    """Generate balanced study schedule from course data."""
    print(f"📅 Scheduling course: {course_data['course_title']}")
    print(f"   Daily limit: {daily_limit} minutes")
    print(f"   Start date: {start_date}")
    
    try:
        # Estimate number of days needed (rough calculation with buffer for splitting)
        total_minutes = course_data['total_duration_minutes']
        estimated_days = max(1, (total_minutes + daily_limit - 1) // daily_limit)  # Round up
        
        # Generate weekday sequence (with extra buffer for oversized content)
        weekdays = generate_weekday_sequence(start_date, estimated_days + 10)
        
        # Initialize scheduling variables
        scheduled_days = []
        current_day_index = 0
        current_day_minutes = 0
        current_day_items = []
        
        # Process all items from all sections in order
        all_items = []
        for section in course_data['sections']:
            for item in section['items']:
                # Add section context to item
                item_with_context = item.copy()
                item_with_context['section_title'] = section['title']
                all_items.append(item_with_context)
        
        print(f"   📋 Processing {len(all_items)} items across {len(course_data['sections'])} sections")
        
        # Keep track of future items from splits
        future_items_queue = []
        
        # Schedule each item
        item_index = 0
        while item_index < len(all_items) or future_items_queue:
            # Get next item (either from main list or future queue)
            if future_items_queue:
                item = future_items_queue.pop(0)
                item_source = "split"
            else:
                item = all_items[item_index]
                item_index += 1
                item_source = "original"
            
            item_duration = item['duration_minutes']
            remaining_time_today = daily_limit - current_day_minutes
            
            # Check if item fits in current day
            if item_duration <= remaining_time_today:
                # Item fits - add it to current day
                current_day_items.append(item)
                current_day_minutes += item_duration
                source_info = f"({item_source})" if item_source == "split" else ""
                print(f"   ✅ Item: '{item['title']}' ({item_duration}min) → Day {current_day_index + 1} {source_info}")
                
            else:
                # Item doesn't fit - handle based on whether it's oversized
                if item_duration > daily_limit:
                    # Oversized item - use special handling
                    items_for_today, items_for_future = handle_oversized_item(item, daily_limit, remaining_time_today)
                    
                    # Add items for today
                    for today_item in items_for_today:
                        current_day_items.append(today_item)
                        current_day_minutes += today_item['duration_minutes']
                        print(f"   ✅ Item: '{today_item['title']}' ({today_item['duration_minutes']}min) → Day {current_day_index + 1} (partial)")
                    
                    # Queue items for future days
                    future_items_queue.extend(items_for_future)
                    
                    # If current day has items, finalize it
                    if current_day_items:
                        day_info = {
                            "day_number": len(scheduled_days) + 1,
                            "date": weekdays[current_day_index],
                            "date_string": weekdays[current_day_index].strftime('%A, %B %d, %Y'),
                            "items": current_day_items.copy(),
                            "total_minutes": current_day_minutes
                        }
                        scheduled_days.append(day_info)
                        print(f"   📅 Day {day_info['day_number']} completed: {current_day_minutes} minutes ({len(current_day_items)} items)")
                        print()
                        
                        # Reset for next day
                        current_day_index += 1
                        current_day_items = []
                        current_day_minutes = 0
                
                else:
                    # Normal item that doesn't fit - finalize current day and start new day
                    if current_day_items:  # Only save if we have items
                        day_info = {
                            "day_number": len(scheduled_days) + 1,
                            "date": weekdays[current_day_index],
                            "date_string": weekdays[current_day_index].strftime('%A, %B %d, %Y'),
                            "items": current_day_items.copy(),
                            "total_minutes": current_day_minutes
                        }
                        scheduled_days.append(day_info)
                        print(f"   📅 Day {day_info['day_number']} completed: {current_day_minutes} minutes ({len(current_day_items)} items)")
                        print()
                    
                    # Move to next day and add the item
                    current_day_index += 1
                    current_day_items = [item]
                    current_day_minutes = item_duration
                    print(f"   🔄 Moving to Day {current_day_index + 1}")
                    source_info = f"({item_source})" if item_source == "split" else ""
                    print(f"   ✅ Item: '{item['title']}' ({item_duration}min) → Day {current_day_index + 1} {source_info}")
        
        # Don't forget the last day
        if current_day_items:
            day_info = {
                "day_number": len(scheduled_days) + 1,
                "date": weekdays[current_day_index],
                "date_string": weekdays[current_day_index].strftime('%A, %B %d, %Y'),
                "items": current_day_items.copy(),
                "total_minutes": current_day_minutes
            }
            scheduled_days.append(day_info)
            print(f"   📅 Final Day {day_info['day_number']} completed: {current_day_minutes} minutes ({len(current_day_items)} items)")
        
        print(f"   🎯 Scheduling complete: {len(scheduled_days)} days total")
        
        # Summary
        total_scheduled_minutes = sum(day['total_minutes'] for day in scheduled_days)
        split_items_count = sum(1 for day in scheduled_days for item in day['items'] if item.get('is_split', False))
        
        print(f"   📊 Schedule Summary:")
        print(f"      Total days: {len(scheduled_days)}")
        print(f"      Total time: {total_scheduled_minutes} minutes ({total_scheduled_minutes/60:.1f} hours)")
        print(f"      Average per day: {total_scheduled_minutes/len(scheduled_days):.1f} minutes")
        if split_items_count > 0:
            print(f"      Split items: {split_items_count} (due to oversized content)")
        
        return scheduled_days
        
    except Exception as e:
        print(f"❌ Error scheduling course: {e}")
        raise


def generate_markdown(scheduled_days):
    """Generate Markdown output with checkboxes."""
    print(f"📝 Generating Markdown for {len(scheduled_days)} days")
    try:
        # TODO: Implement Markdown generation in Phase 4
        # For now, return placeholder markdown
        return "# Study Schedule\n\n*Generated by Study Planner*"
    except Exception as e:
        print(f"❌ Error generating Markdown: {e}")
        raise


def write_output(markdown_content, output_filename):
    """Write Markdown content to file."""
    print(f"💾 Writing output to: {output_filename}")
    try:
        # TODO: Implement file output in Phase 4
        # For now, just show what would be written
        print("Preview of output:")
        print("-" * 40)
        print(markdown_content)
        print("-" * 40)
        print(f"✅ Would write to: {output_filename}")
    except Exception as e:
        print(f"❌ Error writing output: {e}")
        raise


def main():
    """Main pipeline function."""
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Transform video course outlines into balanced study schedules.",
        epilog="""
Examples:
  python study_planner.py sample_course.json 60 2024-01-15
    Generate a schedule with 60 minutes per day starting January 15, 2024
    
  python study_planner.py aws_course.json 90 2024-02-01
    Generate a schedule with 90 minutes per day starting February 1, 2024
    
  python study_planner.py course.json 120 2024-03-15
    Generate a schedule with 2 hours per day starting March 15, 2024

Output:
  Creates a Markdown file with checkboxes for progress tracking
  Schedule includes only weekdays (Monday-Friday)
  Content is balanced across days respecting your time limits
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "course_file",
        help="JSON file containing course outline with sections and items"
    )
    
    parser.add_argument(
        "daily_minutes", 
        type=int,
        help="Maximum study time per day (minimum: 20 minutes, maximum: 480 minutes)"
    )
    
    parser.add_argument(
        "start_date",
        help="Start date in YYYY-MM-DD format (if weekend, will start following Monday)"
    )
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    # Extract arguments for pipeline
    input_file = args.course_file
    daily_limit = args.daily_minutes
    start_date = args.start_date
    
    # Basic argument validation
    print("🔍 Validating arguments...")
    
    # Check if course file exists and is readable
    try:
        with open(input_file, 'r') as f:
            pass  # Just check if we can open it
        print(f"   ✅ Course file found: {input_file}")
    except FileNotFoundError:
        print(f"   ❌ Error: Course file not found: {input_file}")
        print("   Make sure the file exists and the path is correct.")
        sys.exit(1)
    except PermissionError:
        print(f"   ❌ Error: Cannot read course file: {input_file}")
        print("   Check file permissions.")
        sys.exit(1)
    
    # Daily limit validation
    validated_daily_limit = validate_daily_limit(daily_limit)
    
    # Comprehensive date validation with auto-correction
    validated_start_date = validate_start_date(start_date)
    
    print("   🎯 All validation passed!")
    print()
    
    print("Study Planner")
    print(f"Course File: {input_file}")
    print(f"Daily Limit: {validated_daily_limit} minutes")
    print(f"Start Date: {validated_start_date}")
    print()
    
    try:
        # Execute the full pipeline
        print("🚀 Starting pipeline...")
        
        # Phase 1: Parse course data
        course_data = parse_course_json(input_file)
        
        # Phase 2: Generate schedule
        scheduled_days = schedule_course(course_data, validated_daily_limit, validated_start_date)
        
        # Phase 3: Generate Markdown
        markdown = generate_markdown(scheduled_days)
        
        # Phase 4: Write output file
        output_filename = f"{course_data['course_title'].lower().replace(' ', '_')}_schedule.md"
        write_output(markdown, output_filename)
        
        print()
        print("✅ Pipeline completed successfully!")
        
    except Exception as e:
        print()
        print(f"💥 Pipeline failed: {e}")
        print("Check the error above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()