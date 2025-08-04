import re
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_general_knowledge_questions(text_file_path):
    """Extract general knowledge questions from the converted text file."""
    logger.info(f"Starting general knowledge extraction from {text_file_path}")
    
    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Clean up content first
    content = re.sub(r'\n+', '\n', content)  # Remove multiple newlines
    content = content.replace('●​', '●')  # Clean up bullet points
    
    # Find all question blocks using a more flexible approach
    # Look for numbered questions followed by bullet point options
    questions = []
    
    # Split content into lines and process sequentially
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this line starts with a number followed by a dot
        question_match = re.match(r'^(\d+)\.\s*(.+)', line)
        if question_match:
            question_num = question_match.group(1)
            question_text = question_match.group(2).strip()
            
            # Collect the full question text (it might span multiple lines)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('●'):
                if lines[i].strip() and not re.match(r'^\d+\.\s*', lines[i].strip()):
                    question_text += ' ' + lines[i].strip()
                i += 1
            
            # Now collect the options
            options = []
            while i < len(lines) and lines[i].strip().startswith('●'):
                option_text = lines[i].strip().replace('●', '').strip()
                if option_text:
                    options.append(option_text)
                i += 1
            
            # Process this question if we have enough options
            if len(question_text) >= 10 and len(options) >= 2:
                # Ensure we have exactly 4 options
                while len(options) < 4:
                    options.append("")
                
                question_type = determine_question_type(question_text)
                
                question_data = {
                    'question_number': f"GK_{int(question_num):03d}",
                    'question_text': question_text,
                    'option_a': options[0] if len(options) > 0 else "",
                    'option_b': options[1] if len(options) > 1 else "",
                    'option_c': options[2] if len(options) > 2 else "",
                    'option_d': options[3] if len(options) > 3 else "",
                    'correct_answer': 'A',  # Default to A since we don't have clear indicators
                    'question_type': question_type,
                    'difficulty': 'Medium'
                }
                
                questions.append(question_data)
                logger.debug(f"Extracted question {question_num}: {question_text[:50]}...")
            else:
                logger.warning(f"Skipped question {question_num}: insufficient text or options")
        else:
            i += 1
    
    # Also try to find questions without numbers but with clear question structure
    # Look for lines ending with question marks followed by bullet points
    additional_questions = []
    lines = content.split('\n')
    i = 0
    question_counter = len(questions) + 1
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for question-like patterns
        if (line.endswith('?') or 
            line.endswith('is') or 
            line.endswith('are') or
            ('where' in line.lower() and not line.startswith('●')) or
            ('what' in line.lower() and not line.startswith('●')) or
            ('which' in line.lower() and not line.startswith('●'))):
            
            question_text = line
            i += 1
            
            # Check if followed by options
            options = []
            while i < len(lines) and lines[i].strip().startswith('●'):
                option_text = lines[i].strip().replace('●', '').strip()
                if option_text:
                    options.append(option_text)
                i += 1
            
            if len(question_text) >= 10 and len(options) >= 2:
                # Ensure we have exactly 4 options
                while len(options) < 4:
                    options.append("")
                
                question_type = determine_question_type(question_text)
                
                question_data = {
                    'question_number': f"GK_{question_counter:03d}",
                    'question_text': question_text,
                    'option_a': options[0] if len(options) > 0 else "",
                    'option_b': options[1] if len(options) > 1 else "",
                    'option_c': options[2] if len(options) > 2 else "",
                    'option_d': options[3] if len(options) > 3 else "",
                    'correct_answer': 'A',
                    'question_type': question_type,
                    'difficulty': 'Medium'
                }
                
                additional_questions.append(question_data)
                question_counter += 1
                logger.debug(f"Extracted additional question: {question_text[:50]}...")
        else:
            i += 1
    
    # Combine all questions
    all_questions = questions + additional_questions
    
    logger.info(f"Extracted {len(all_questions)} valid general knowledge questions ({len(questions)} numbered + {len(additional_questions)} additional)")
    return all_questions

def determine_question_type(question_text):
    """Determine the type of general knowledge question based on content."""
    question_lower = question_text.lower()
    
    # Define keywords for different categories
    if any(word in question_lower for word in ['nigeria', 'nigerian', 'lagos', 'abuja', 'state', 'capital', 'warri', 'ondo', 'ekiti', 'jigawa']):
        return 'Nigerian Geography/Politics'
    elif any(word in question_lower for word in ['mountain', 'ocean', 'country', 'continent', 'capital', 'river', 'kilmanjaro', 'everest', 'tanzania']):
        return 'World Geography'
    elif any(word in question_lower for word in ['cup', 'olympics', 'sport', 'football', 'soccer', 'fifa', 'goal', 'score']):
        return 'Sports'
    elif any(word in question_lower for word in ['founded', 'inventor', 'discovered', 'history', 'century', 'tiktok', 'spacex']):
        return 'History/Technology'
    elif any(word in question_lower for word in ['colour', 'color', 'science', 'chemical', 'element', 'primary colours', 'water']):
        return 'Science'
    elif any(word in question_lower for word in ['idiom', 'saying', 'expression', 'phrase', 'apple of', 'feather in', 'chip of']):
        return 'Language/Idioms'
    elif any(word in question_lower for word in ['day', 'celebrated', 'holiday', 'festival', "woman's day"]):
        return 'Culture/Events'
    elif any(word in question_lower for word in ['astronomer', 'astrologer', 'surveyor', 'connoisseur', 'horticulturist']):
        return 'Professions'
    else:
        return 'General Knowledge'

def save_to_database(questions, db_path='edtech_questions_database.db'):
    """Save general knowledge questions to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    saved_count = 0
    for question in questions:
        try:
            cursor.execute("""
                INSERT INTO general_knowledge_questions 
                (question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, question_type, category, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                question['question_number'],
                question['question_text'],
                question['option_a'],
                question['option_b'],
                question['option_c'],
                question['option_d'],
                question['correct_answer'],
                question['question_type'],
                question['question_type'],  # Use question_type as category as well
                question['difficulty']
            ))
            saved_count += 1
        except Exception as e:
            logger.error(f"Error saving question: {e}")
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved {saved_count} general knowledge questions to database")
    return saved_count

def print_sample_questions(questions, num_samples=5):
    """Print sample questions for verification."""
    print("\n=== Sample General Knowledge Questions ===")
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
        print("\n=== General Knowledge Extraction Summary ===")
        print("Total questions in database: 0")
        return
        
    # Count by type
    type_counts = {}
    for q in questions:
        q_type = q['question_type']
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
    
    print(f"\n=== General Knowledge Extraction Summary ===")
    print(f"Total questions in database: {len(questions)}")
    print("Question types:")
    for q_type, count in sorted(type_counts.items()):
        print(f"  {q_type}: {count}")

if __name__ == "__main__":
    # Extract questions from the general knowledge text file
    questions = extract_general_knowledge_questions('general_knowledge_bank.txt')
    
    if questions:
        # Save to database
        save_to_database(questions)
        
        # Print samples and statistics
        print_sample_questions(questions)
        print_statistics(questions)
    else:
        print("No valid general knowledge questions found.")
    
    print(f"\nGeneral Knowledge extraction complete! {len(questions)} questions saved")
