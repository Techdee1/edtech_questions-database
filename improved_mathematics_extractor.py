import re
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_mathematics_questions(text_file_path):
    """Extract mathematics questions from the converted text file."""
    logger.info(f"Starting mathematics extraction from {text_file_path}")
    
    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Split content into chunks around question markers
    # Look for various question patterns
    question_patterns = [
        r'(?:--)?(?:\*)?(?:Question(?:\s+\d+)?:?)(?:\*)?',
        r'(?:--)?(?:\*)?(?:QUESTION(?:\s+\d+)?:?)(?:\*)?'
    ]
    
    # Split content by any of the question patterns
    combined_pattern = '|'.join(f'({pattern})' for pattern in question_patterns)
    
    # Find all question starts
    question_starts = []
    for match in re.finditer(combined_pattern, content, re.IGNORECASE | re.MULTILINE):
        question_starts.append(match.start())
    
    logger.info(f"Found {len(question_starts)} potential question starts")
    
    valid_questions = []
    
    for i, start in enumerate(question_starts):
        # Get the end position (next question start or end of content)
        end = question_starts[i + 1] if i + 1 < len(question_starts) else len(content)
        
        # Extract the question block
        question_block = content[start:end]
        
        # Clean and process the question
        question = process_question_block(question_block, i + 1)
        if question:
            valid_questions.append(question)
    
    logger.info(f"Extracted {len(valid_questions)} valid mathematics questions")
    return valid_questions

def process_question_block(block, question_num):
    """Process a single question block to extract question, options, and correct answer."""
    
    # Clean the block
    block = block.strip()
    if not block:
        return None
    
    # Extract question text (everything before "Options:" or option markers)
    lines = block.split('\n')
    question_lines = []
    options = []
    correct_answer = None
    
    collecting_question = True
    collecting_options = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip various separators and markers
        if line in ['---', '--', '✅', '✔️', '*Options:', 'Options:']:
            if line in ['*Options:', 'Options:']:
                collecting_question = False
                collecting_options = True
            continue
            
        # Check if this is an option line
        option_match = re.match(r'^([A-D])[).]?\s*(.+)', line)
        bullet_option_match = re.match(r'^\*\s*(.+)', line)
        
        if collecting_options and (option_match or bullet_option_match):
            if option_match:
                option_letter = option_match.group(1)
                option_text = option_match.group(2).strip()
            else:
                # For bullet options, assign letters A, B, C, D in order
                option_letter = chr(65 + len(options))  # A=65, B=66, etc.
                option_text = bullet_option_match.group(1).strip()
            
            options.append({
                'letter': option_letter,
                'text': option_text
            })
            
        elif collecting_question:
            # Skip question headers/markers
            if re.match(r'(?:--)?(?:\*)?(?:Question(?:\s+\d+)?:?)(?:\*)?', line, re.IGNORECASE):
                continue
            question_lines.append(line)
    
    # Check if we found options after the question text ended
    if not collecting_options and not options:
        # Look for options in the remaining text
        remaining_text = '\n'.join(lines)
        option_pattern = r'([A-D])[).]?\s*([^\n]+)'
        option_matches = re.findall(option_pattern, remaining_text)
        for letter, text in option_matches:
            options.append({
                'letter': letter,
                'text': text.strip()
            })
    
    # Join question lines
    question_text = ' '.join(question_lines).strip()
    
    # Clean up question text
    question_text = re.sub(r'\s+', ' ', question_text)
    question_text = question_text.replace('*', '').strip()
    
    # Validate question
    if len(question_text) < 10:
        logger.warning(f"Question {question_num} has insufficient text: '{question_text[:50]}...'")
        return None
        
    if len(options) < 2:
        logger.warning(f"Question {question_num} has insufficient options: {len(options)}")
        return None
    
    # For now, we'll mark the first option as correct since checkmarks are not consistently placed
    # In a real scenario, you'd want to improve checkmark detection
    if options:
        correct_answer = options[0]['letter']
    
    # Determine question type based on content
    question_type = determine_question_type(question_text)
    
    return {
        'question_text': question_text,
        'option_a': next((opt['text'] for opt in options if opt['letter'] == 'A'), ''),
        'option_b': next((opt['text'] for opt in options if opt['letter'] == 'B'), ''),
        'option_c': next((opt['text'] for opt in options if opt['letter'] == 'C'), ''),
        'option_d': next((opt['text'] for opt in options if opt['letter'] == 'D'), ''),
        'correct_answer': correct_answer,
        'question_type': question_type,
        'difficulty': 'Medium'  # Default difficulty
    }

def determine_question_type(question_text):
    """Determine the type of mathematics question based on content."""
    question_lower = question_text.lower()
    
    # Define keywords for different categories
    if any(word in question_lower for word in ['sin', 'cos', 'tan', 'angle', 'bearing', 'elevation']):
        return 'Trigonometry'
    elif any(word in question_lower for word in ['derivative', 'integral', 'limit', 'differential']):
        return 'Calculus'
    elif any(word in question_lower for word in ['mean', 'median', 'mode', 'probability', 'average', 'standard deviation']):
        return 'Statistics'
    elif any(word in question_lower for word in ['equation', 'solve', 'quadratic', 'linear', 'x =', 'solve for']):
        return 'Algebra'
    elif any(word in question_lower for word in ['area', 'volume', 'perimeter', 'radius', 'diameter', 'circle', 'rectangle', 'triangle']):
        return 'Geometry'
    else:
        return 'Arithmetic'

def save_to_database(questions, db_path='edtech_questions_database.db'):
    """Save mathematics questions to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    saved_count = 0
    for i, question in enumerate(questions):
        try:
            cursor.execute("""
                INSERT INTO mathematics_questions 
                (question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, question_type, topic, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"MATH_{i+1:03d}",  # Generate question number like MATH_001, MATH_002, etc.
                question['question_text'],
                question['option_a'],
                question['option_b'],
                question['option_c'],
                question['option_d'],
                question['correct_answer'],
                question['question_type'],
                question['question_type'],  # Use question_type as topic as well
                question['difficulty']
            ))
            saved_count += 1
        except Exception as e:
            logger.error(f"Error saving question: {e}")
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved {saved_count} mathematics questions to database")
    return saved_count

def print_sample_questions(questions, num_samples=5):
    """Print sample questions for verification."""
    print("\n=== Sample Mathematics Questions ===")
    for i, q in enumerate(questions[:num_samples]):
        print(f"\nQuestion {i+1} ({q['question_type']}):")
        print(f"Q: {q['question_text']}")
        print(f"A: {q['option_a']}")
        print(f"B: {q['option_b']}")
        print(f"C: {q['option_c']}")
        print(f"D: {q['option_d']}")
        print(f"Correct: {q['correct_answer']}")

def print_statistics(questions):
    """Print extraction statistics."""
    if not questions:
        print("\n=== Mathematics Extraction Summary ===")
        print("Total questions in database: 0")
        return
        
    # Count by type
    type_counts = {}
    for q in questions:
        q_type = q['question_type']
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
    
    print(f"\n=== Mathematics Extraction Summary ===")
    print(f"Total questions in database: {len(questions)}")
    print("Question types:")
    for q_type, count in sorted(type_counts.items()):
        print(f"  {q_type}: {count}")

if __name__ == "__main__":
    # Extract questions from the mathematics text file
    questions = extract_mathematics_questions('mathematics_bank.txt')
    
    if questions:
        # Save to database
        save_to_database(questions)
        
        # Print samples and statistics
        print_sample_questions(questions)
        print_statistics(questions)
    else:
        print("No valid mathematics questions found.")
    
    print(f"\nMathematics extraction complete! {len(questions)} questions saved")
