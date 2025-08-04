# 🎓 Edtech Questions Database

A comprehensive SQLite database containing **300 multiple-choice questions** across three subjects: English, Mathematics, and General Knowledge. Perfect for edtech platforms, quiz applications, and educational assessments.

## 📊 Database Overview

| Subject | Questions | Extraction Rate | Source |
|---------|-----------|----------------|---------|
| 🇬🇧 **English** | 102 | 50% (102/204) | 74-page PDF |
| 🔢 **Mathematics** | 146 | 77.7% (146/188) | 8-page PDF |
| 🌍 **General Knowledge** | 52 | 83.9% (52/62) | Multi-page PDF |
| **TOTAL** | **300** | **65.8%** | 3 PDF sources |

## 🗄️ Database Structure

### Tables
- `english_questions` - English language questions with grammar, vocabulary, pronunciation, etc.
- `mathematics_questions` - Math questions covering arithmetic, algebra, geometry, trigonometry, etc.
- `general_knowledge_questions` - General knowledge covering geography, sports, science, culture, etc.

### Common Schema
```sql
CREATE TABLE [subject]_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_number TEXT NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    question_type TEXT,
    [subject_specific_fields],
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 📚 Question Types Breakdown

### 🇬🇧 English (102 questions)
- **Multiple Choice**: 30 questions (29.4%)
- **General**: 17 questions (16.7%)
- **Vocabulary**: 15 questions (14.7%)
- **Fill in Blank**: 15 questions (14.7%)
- **Grammar**: 13 questions (12.7%)
- **Pronunciation**: 12 questions (11.8%)

### 🔢 Mathematics (146 questions)
- **Arithmetic**: 71 questions (48.6%)
- **Trigonometry**: 42 questions (28.8%)
- **Algebra**: 17 questions (11.6%)
- **Geometry**: 9 questions (6.2%)
- **Statistics**: 6 questions (4.1%)
- **Calculus**: 1 question (0.7%)

### 🌍 General Knowledge (52 questions)
- **General Knowledge**: 20 questions (38.5%)
- **Nigerian Geography/Politics**: 9 questions (17.3%)
- **Sports**: 7 questions (13.5%)
- **World Geography**: 6 questions (11.5%)
- **Science**: 3 questions (5.8%)
- **Language/Idioms**: 3 questions (5.8%)
- **History/Technology**: 2 questions (3.8%)
- **Culture/Events**: 2 questions (3.8%)

## 🚀 Quick Start

### 1. Database Setup
```bash
# The database file is ready to use
cp edtech_questions_database.db /your/project/path/
```

### 2. Python Usage
```python
import sqlite3

# Connect to database
conn = sqlite3.connect('edtech_questions_database.db')
cursor = conn.cursor()

# Get 10 random English questions
cursor.execute("""
    SELECT question_text, option_a, option_b, option_c, option_d, correct_answer
    FROM english_questions 
    ORDER BY RANDOM() 
    LIMIT 10
""")

questions = cursor.fetchall()
conn.close()
```

### 3. Using the API Demo
```bash
python api_demo.py
```

## 🛠️ API Interface

The included `api_demo.py` provides a complete API interface:

```python
from api_demo import EdtechQuestionsAPI

api = EdtechQuestionsAPI()

# Get questions by subject
english_questions = api.get_questions_by_subject('english', limit=10)

# Generate a quiz
quiz = api.get_quiz_questions('mathematics', question_type='Arithmetic', count=5)

# Mixed subject quiz
mixed_quiz = api.get_mixed_quiz(count_per_subject=3)

# Get statistics
stats = api.get_database_stats()
```

## 📁 Project Files

| File | Description |
|------|-------------|
| `edtech_questions_database.db` | **Main SQLite database** |
| `api_demo.py` | API interface and usage examples |
| `final_summary.py` | Comprehensive database summary generator |
| `database_summary.json` | JSON export of database statistics |
| `unified_database.py` | Database management utilities |
| `extract_english_questions.py` | English questions extractor |
| `improved_mathematics_extractor.py` | Mathematics questions extractor |
| `improved_general_knowledge_extractor.py` | General knowledge extractor |

## 🎯 Sample Questions

### English
```
Q: Choose the option which indicates the word class of the capitalized word: 
   The table was covered with PLAIN cloth.
A) adjective  B) verb  C) adverb  D) noun
✅ Answer: A
```

### Mathematics
```
Q: What is the value of 0.316 ÷ 0.79?
A) 0.025  B) 2.5  C) 0.40  D) 40.0
✅ Answer: A
```

### General Knowledge
```
Q: What do you call a score in soccer?
A) homerun  B) Goal  C) net  D) none of the above
✅ Answer: B
```

## 🔧 Technical Details

### Extraction Process
1. **PDF to Text**: Used `pdftotext` to convert PDF files to plain text
2. **Pattern Recognition**: Custom regex patterns to identify questions and options
3. **Data Validation**: Ensured minimum text length and option count requirements
4. **Type Classification**: Automatic categorization based on content analysis
5. **Database Storage**: Structured storage with proper schema validation

### Data Quality
- **English**: 50% extraction rate due to mixed formatting in source PDF
- **Mathematics**: 77.7% extraction rate with consistent question patterns
- **General Knowledge**: 83.9% extraction rate with clear bullet-point structure

## 🎮 Use Cases

- **Educational Platforms**: Ready-to-use question bank for online learning
- **Quiz Applications**: Generate dynamic quizzes by subject or type
- **Assessment Tools**: Create standardized tests and evaluations
- **Practice Systems**: Student practice and self-assessment
- **API Integration**: RESTful API backend for mobile/web apps

## 📊 Integration Examples

### Flask Web API
```python
from flask import Flask, jsonify
from api_demo import EdtechQuestionsAPI

app = Flask(__name__)
api = EdtechQuestionsAPI()

@app.route('/api/quiz/<subject>/<int:count>')
def get_quiz(subject, count):
    questions = api.get_questions_by_subject(subject, count)
    return jsonify(questions)
```

### React Frontend
```javascript
// Fetch questions from API
const fetchQuiz = async (subject, count) => {
  const response = await fetch(`/api/quiz/${subject}/${count}`);
  return await response.json();
};
```

## 🤝 Contributing

To extend the database:
1. Add new extraction scripts for additional subjects
2. Improve existing extractors for better accuracy
3. Add new question types or categories
4. Enhance the API with additional functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- Original PDF sources for comprehensive question content
- Python ecosystem for text processing and database management
- SQLite for reliable, lightweight database storage

---

**Ready for production use in your edtech platform! 🚀**