# Study Planner

A command-line tool that transforms video course outlines into balanced, trackable study schedules. Input your course content, daily time limit, and start date - get back a structured Markdown schedule with checkboxes to track your progress.

## 🎯 Purpose

Originally built to create balanced study plans for AWS certification courses, this tool helps you:
- Distribute course content evenly across weekdays
- Respect your daily time constraints
- Handle oversized content intelligently
- Track progress with interactive checkboxes

## 🚀 Quick Start

```bash
# Generate a study schedule
python study_planner.py sample_course.json 60 2024-01-15

# Output: A Markdown file with your personalized study plan
```

## 📋 Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

## 📁 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/study-planner.git
cd study-planner
```

2. Run with your course data:
```bash
python study_planner.py your_course.json [daily_minutes] [start_date]
```

## 📖 Usage

### Basic Command
```bash
python study_planner.py <course_file> <daily_minutes> <start_date>
```

**Parameters:**
- `course_file`: JSON file containing your course outline
- `daily_minutes`: Maximum study time per day (20-480 minutes)
- `start_date`: When to start (YYYY-MM-DD format)

### Example
```bash
python study_planner.py aws_saa_course.json 90 2024-02-01
```

## 📄 Input Format

Create a JSON file with your course structure:

```json
{
  "course_title": "AWS Solutions Architect Associate",
  "sections": [
    {
      "title": "S3 Fundamentals",
      "items": [
        {"title": "S3 Introduction", "type": "video", "duration": "15:30"},
        {"title": "S3 Hands-on Lab", "type": "video", "duration": "22:45"},
        {"title": "S3 Knowledge Check", "type": "quiz", "duration": "10:00"}
      ]
    }
  ]
}
```

**Supported time formats:** `5:30`, `05:30`, `0:45`, `00:45`

## 📅 Output Format

Generates a Markdown study schedule:

```markdown
# AWS Solutions Architect Associate Study Schedule

**Start Date:** February 1, 2024  
**Daily Limit:** 90 minutes  

## Day 1 - Thursday, February 1, 2024 (87 minutes)
- [ ] S3 Introduction (15:30)
- [ ] S3 Hands-on Lab (22:45)
- [ ] S3 Deep Dive (25:15)
- [ ] EC2 Basics (23:30)

## Day 2 - Friday, February 2, 2024 (78 minutes)
- [ ] S3 Knowledge Check (10:00)
- [ ] EC2 Instance Types (35:45)
- [ ] EC2 Security Groups (32:15)
```

## ⚙️ How It Works

1. **Smart Scheduling**: Distributes content across weekdays only
2. **Strict Time Limits**: Never exceeds your daily maximum
3. **Oversized Content**: Automatically splits long videos across multiple days
4. **Balanced Distribution**: Optimizes daily workload while respecting constraints

## 🔧 Development Status

**Current Version:** MVP (Minimum Viable Product)

**Features:**
- ✅ JSON course parsing
- ✅ Weekday-only scheduling  
- ✅ Markdown output with checkboxes
- ✅ Input validation and error handling
- 🚧 *In Development*

**Coming Soon:**
- Weekend scheduling options
- Holiday/blackout date support
- Multiple output formats
- Configuration files
- Progress tracking

## 📚 Examples

See `sample_course.json` for a complete example course structure.

## 🐛 Troubleshooting

### Common Issues

**"Daily limit must be at least 20 minutes"**
- Increase your daily study time to at least 20 minutes

**"Start date cannot be in the past"**
- Use a current or future date in YYYY-MM-DD format

**"Invalid duration format"**
- Check that all durations use MM:SS format (e.g., "15:30")

### Getting Help

- Check the [design document](design_document.md) for detailed information
- Review `sample_course.json` for proper formatting
- Open an issue if you encounter bugs

## 🤝 Contributing

This project started as a personal tool for AWS certification study planning. Contributions are welcome!

**Before contributing:**
1. Review the [design document](design_document.md)
2. Check existing issues
3. Open an issue to discuss major changes

**Development setup:**
```bash
git clone https://github.com/yourusername/study-planner.git
cd study-planner
# No additional setup required - uses standard library only
```

## 📜 License

*License to be determined*

## 🙏 Acknowledgments

Born from the need to create balanced study schedules for AWS certification while maintaining a sustainable learning pace. Special thanks to the iterative design process that helped refine the core algorithms.

---

**Note:** This project is currently in active development. Features and usage may change as we work toward the first stable release.