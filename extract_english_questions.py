#!/usr/bin/env python3
"""
English Question Bank Extractor
Extracts questions from English bank PDF text and stores them in SQLite database
"""

import re
import sqlite3
import logging
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnglishQuestionExtractor:
    def __init__(self, db_path: str = "english_questions.db"):
        self.db_path = db_path
        
        # Regex patterns based on document analysis
        self.QUESTION_PATTERN = r'^(\*?\d+\.\*|By\*\d+\.\*|Question\s+\d+:)\s*(.*)$'
        self.OPTION_PATTERN = r'^[\*\-\s]*([A-Z])\)\s*(.*?)\s*([✔✅])?$'
        self.SIMPLE_OPTION_PATTERN = r'^\*?\s*([A-Z])\)\s*(.*?)\s*([✔✅])?$'
        self.STAR_OPTION_PATTERN = r'^\*\s*(.*?)\s*([✔✅])?$'
        self.PAGE_PATTERN = r'===== Page \d+ ====='
        
    def create_database(self):
        """Create the SQLite database and questions table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS english_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_number TEXT NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer CHAR(1) NOT NULL,
                question_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database created at {self.db_path}")
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and formatting characters"""
        # Remove asterisks around text (e.g., "*bite off*" → "bite off")
        if text.startswith('*') and text.endswith('*') and len(text) > 2:
            text = text[1:-1]
        
        # Remove backticks
        text = text.replace('```', '')
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def extract_question_number(self, question_pattern_match: str) -> str:
        """Extract just the numeric part from question pattern"""
        # Extract digits from patterns like "2292.*", "By*2293.*", "*1153.*", "Question 1098:"
        number_match = re.search(r'\d+', question_pattern_match)
        return number_match.group() if number_match else ""
    
    def determine_question_type(self, question_text: str) -> str:
        """Determine the type of question based on content"""
        question_lower = question_text.lower()
        
        if 'grammatical name' in question_lower or 'grammar' in question_lower:
            return 'grammar'
        elif 'sound' in question_lower or 'pronunciation' in question_lower:
            return 'pronunciation'
        elif 'meaning' in question_lower or 'nearest meaning' in question_lower:
            return 'vocabulary'
        elif 'choose the option' in question_lower:
            return 'multiple_choice'
        elif '----------' in question_text or '___' in question_text:
            return 'fill_in_blank'
        else:
            return 'general'
    
    def parse_questions(self, content: str) -> List[Dict]:
        """Parse questions from the extracted PDF text"""
        # Split by pages if page markers exist, otherwise process as single block
        if self.PAGE_PATTERN in content:
            pages = re.split(self.PAGE_PATTERN, content)[1:]  # Skip first empty split
        else:
            pages = [content]
        
        questions = []
        
        for page_num, page in enumerate(pages, 1):
            lines = page.splitlines()
            current_question = None
            pending_checkmark = False
            
            for line_num, line in enumerate(lines):
                original_line = line
                line = line.strip()
                
                # Skip empty lines and informational text
                if not line or line in ['✅', '✔'] or 'Here are the questions' in line:
                    # Check if this is a standalone checkmark for the previous option
                    if line in ['✅', '✔'] and current_question and current_question['options']:
                        pending_checkmark = True
                    continue
                
                # Try to match question number pattern
                question_match = re.match(self.QUESTION_PATTERN, line)
                if question_match:
                    # Save previous question if exists
                    if current_question:
                        self._finalize_question(current_question, questions)
                    
                    # Start new question
                    number = self.extract_question_number(question_match.group(1))
                    text = self.clean_text(question_match.group(2))
                    
                    current_question = {
                        'number': number,
                        'text': text,
                        'options': {},
                        'correct_answer': None,
                        'page': page_num,
                        'option_order': []  # Track order of options
                    }
                    
                    logger.debug(f"Found question {number}: {text[:50]}...")
                    continue
                
                # Try to match option pattern
                option_match = re.match(self.OPTION_PATTERN, line)
                if not option_match:
                    option_match = re.match(self.SIMPLE_OPTION_PATTERN, line)
                
                # Handle star-format options (like "* similar")
                star_match = None
                if not option_match:
                    star_match = re.match(self.STAR_OPTION_PATTERN, line)
                
                if (option_match or star_match) and current_question:
                    if option_match:
                        letter = option_match.group(1)
                        option_text = self.clean_text(option_match.group(2))
                        has_checkmark = bool(option_match.group(3))
                        
                        # Check if option is marked correct with asterisks
                        is_correct_asterisk = (option_match.group(2).strip().startswith('*') and 
                                             option_match.group(2).strip().endswith('*'))
                    else:  # star_match
                        # For star format, assign letters A, B, C, D in order
                        option_count = len(current_question['option_order'])
                        if option_count < 4:
                            letter = chr(ord('A') + option_count)
                            option_text = self.clean_text(star_match.group(1))
                            has_checkmark = bool(star_match.group(2))
                            is_correct_asterisk = False
                        else:
                            continue  # Skip if we already have 4 options
                    
                    # Apply pending checkmark to the last option if no current checkmark
                    if pending_checkmark and not has_checkmark and len(current_question['option_order']) > 0:
                        last_option = current_question['option_order'][-1]
                        current_question['correct_answer'] = last_option
                        logger.debug(f"  Applied pending checkmark to option {last_option}")
                        pending_checkmark = False
                    
                    is_correct = has_checkmark or is_correct_asterisk
                    
                    current_question['options'][letter] = option_text
                    current_question['option_order'].append(letter)
                    
                    if is_correct:
                        current_question['correct_answer'] = letter
                        logger.debug(f"  Correct answer: {letter}) {option_text}")
                    
                    continue
                
                # Check for standalone checkmark after option processing
                if line in ['✅', '✔'] and current_question and current_question['option_order']:
                    if not current_question['correct_answer']:
                        last_option = current_question['option_order'][-1]
                        current_question['correct_answer'] = last_option
                        logger.debug(f"  Applied standalone checkmark to option {last_option}")
                    continue
                
                # If line doesn't match question or option pattern, it might be continuation text
                if current_question and current_question['text']:
                    # Check if this looks like continuation of question text
                    if not re.match(r'^[A-Z]\)', line) and len(line) > 10 and 'question' not in line.lower():
                        current_question['text'] += ' ' + self.clean_text(line)
            
            # Don't forget the last question in the page
            if current_question:
                self._finalize_question(current_question, questions)
        
        logger.info(f"Extracted {len(questions)} questions from {len(pages)} pages")
        return questions
    
    def _finalize_question(self, question: Dict, questions: List[Dict]):
        """Finalize and add question to list if complete"""
        # Clean up the question dict by removing helper fields
        if 'option_order' in question:
            del question['option_order']
        
        if self.is_question_complete(question):
            questions.append(question)
        else:
            logger.warning(f"Discarding incomplete question {question['number']}")
    
    def is_question_complete(self, question: Dict) -> bool:
        """Check if a question has all required components"""
        required_options = {'A', 'B', 'C', 'D'}
        has_all_options = required_options.issubset(set(question['options'].keys()))
        has_correct_answer = question['correct_answer'] is not None
        has_text = bool(question['text'])
        
        if not has_all_options:
            logger.warning(f"Question {question['number']} missing options: "
                          f"has {list(question['options'].keys())}")
        if not has_correct_answer:
            logger.warning(f"Question {question['number']} has no correct answer marked")
        
        return has_all_options and has_correct_answer and has_text
    
    def save_to_database(self, questions: List[Dict]):
        """Save extracted questions to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM english_questions')
        
        saved_count = 0
        for question in questions:
            if not self.is_question_complete(question):
                logger.warning(f"Skipping incomplete question {question['number']}")
                continue
            
            question_type = self.determine_question_type(question['text'])
            
            try:
                cursor.execute('''
                    INSERT INTO english_questions 
                    (question_number, question_text, option_a, option_b, option_c, option_d, 
                     correct_answer, question_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    question['number'],
                    question['text'],
                    question['options'].get('A', ''),
                    question['options'].get('B', ''),
                    question['options'].get('C', ''),
                    question['options'].get('D', ''),
                    question['correct_answer'],
                    question_type
                ))
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving question {question['number']}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {saved_count} questions to database")
        return saved_count
    
    def extract_and_save(self, text_file_path: str):
        """Main method to extract questions from text file and save to database"""
        logger.info(f"Starting extraction from {text_file_path}")
        
        # Read the extracted text
        with open(text_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create database
        self.create_database()
        
        # Parse questions
        questions = self.parse_questions(content)
        
        # Save to database
        saved_count = self.save_to_database(questions)
        
        logger.info(f"Extraction complete! {saved_count} questions saved to {self.db_path}")
        
        return questions, saved_count
    
    def print_sample_questions(self, limit: int = 3):
        """Print a few sample questions from the database for verification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question_number, question_text, option_a, option_b, option_c, option_d, 
                   correct_answer, question_type
            FROM english_questions 
            ORDER BY CAST(question_number AS INTEGER)
            LIMIT ?
        ''', (limit,))
        
        questions = cursor.fetchall()
        conn.close()
        
        print(f"\n=== Sample Questions from Database ===")
        for q in questions:
            print(f"\nQuestion {q[0]} ({q[7]}):")
            print(f"Text: {q[1]}")
            print(f"A) {q[2]}")
            print(f"B) {q[3]}")
            print(f"C) {q[4]}")
            print(f"D) {q[5]}")
            print(f"Correct Answer: {q[6]}")
            print("-" * 50)


def main():
    """Main function to run the extraction"""
    extractor = EnglishQuestionExtractor()
    
    # Extract questions from the complete text file
    questions, saved_count = extractor.extract_and_save('english_bank_complete.txt')
    
    # Print some sample questions for verification
    extractor.print_sample_questions(3)
    
    # Print summary statistics
    conn = sqlite3.connect(extractor.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM english_questions')
    total_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT question_type, COUNT(*) FROM english_questions GROUP BY question_type')
    type_counts = cursor.fetchall()
    
    conn.close()
    
    print(f"\n=== Extraction Summary ===")
    print(f"Total questions in database: {total_count}")
    print(f"Question types:")
    for q_type, count in type_counts:
        print(f"  {q_type}: {count}")


if __name__ == "__main__":
    main()
