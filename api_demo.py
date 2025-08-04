"""
Simple API Demo for Edtech Questions Database
This demonstrates how to query the database for different use cases
"""

import sqlite3
import random
from typing import List, Dict, Any, Optional

class EdtechQuestionsAPI:
    def __init__(self, db_path: str = 'edtech_questions_database.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_questions_by_subject(self, subject: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get questions from a specific subject."""
        table_map = {
            'english': 'english_questions',
            'mathematics': 'mathematics_questions', 
            'general_knowledge': 'general_knowledge_questions'
        }
        
        if subject.lower() not in table_map:
            raise ValueError(f"Subject must be one of: {list(table_map.keys())}")
        
        table_name = table_map[subject.lower()]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT id, question_number, question_text, option_a, option_b, 
                       option_c, option_d, correct_answer, question_type
                FROM {table_name}
                ORDER BY RANDOM()
                LIMIT ?
            """, (limit,))
            
            questions = []
            for row in cursor.fetchall():
                questions.append({
                    'id': row[0],
                    'question_number': row[1],
                    'question_text': row[2],
                    'options': {
                        'A': row[3],
                        'B': row[4],
                        'C': row[5],
                        'D': row[6]
                    },
                    'correct_answer': row[7],
                    'question_type': row[8],
                    'subject': subject
                })
            
            return questions
    
    def get_quiz_questions(self, subject: str, question_type: Optional[str] = None, 
                          count: int = 10) -> List[Dict[str, Any]]:
        """Generate a quiz with specified parameters."""
        table_map = {
            'english': 'english_questions',
            'mathematics': 'mathematics_questions',
            'general_knowledge': 'general_knowledge_questions'
        }
        
        table_name = table_map[subject.lower()]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if question_type:
                query = f"""
                    SELECT id, question_number, question_text, option_a, option_b, 
                           option_c, option_d, correct_answer, question_type
                    FROM {table_name}
                    WHERE question_type = ?
                    ORDER BY RANDOM()
                    LIMIT ?
                """
                cursor.execute(query, (question_type, count))
            else:
                query = f"""
                    SELECT id, question_number, question_text, option_a, option_b, 
                           option_c, option_d, correct_answer, question_type
                    FROM {table_name}
                    ORDER BY RANDOM()
                    LIMIT ?
                """
                cursor.execute(query, (count,))
            
            quiz_questions = []
            for row in cursor.fetchall():
                quiz_questions.append({
                    'id': row[0],
                    'question_number': row[1],
                    'question_text': row[2],
                    'options': {
                        'A': row[3],
                        'B': row[4],
                        'C': row[5],
                        'D': row[6]
                    },
                    'correct_answer': row[7],
                    'question_type': row[8],
                    'subject': subject
                })
            
            return quiz_questions
    
    def get_mixed_quiz(self, count_per_subject: int = 5) -> List[Dict[str, Any]]:
        """Generate a mixed quiz with questions from all subjects."""
        all_questions = []
        
        for subject in ['english', 'mathematics', 'general_knowledge']:
            questions = self.get_questions_by_subject(subject, count_per_subject)
            all_questions.extend(questions)
        
        # Shuffle the questions
        random.shuffle(all_questions)
        return all_questions
    
    def get_question_types_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Get available question types for a subject."""
        table_map = {
            'english': 'english_questions',
            'mathematics': 'mathematics_questions',
            'general_knowledge': 'general_knowledge_questions'
        }
        
        table_name = table_map[subject.lower()]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT question_type, COUNT(*) as count
                FROM {table_name}
                GROUP BY question_type
                ORDER BY count DESC
            """)
            
            return [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        stats = {'subjects': {}, 'total_questions': 0}
        
        tables = {
            'English': 'english_questions',
            'Mathematics': 'mathematics_questions',
            'General Knowledge': 'general_knowledge_questions'
        }
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for subject, table_name in tables.items():
                # Get total count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total = cursor.fetchone()[0]
                
                # Get question types
                cursor.execute(f"""
                    SELECT question_type, COUNT(*) 
                    FROM {table_name} 
                    GROUP BY question_type
                """)
                types = dict(cursor.fetchall())
                
                stats['subjects'][subject] = {
                    'total_questions': total,
                    'question_types': types
                }
                stats['total_questions'] += total
        
        return stats

def demo_api_usage():
    """Demonstrate API usage with examples."""
    api = EdtechQuestionsAPI()
    
    print("🚀 EDTECH QUESTIONS DATABASE API DEMO")
    print("=" * 60)
    
    # Demo 1: Get database statistics
    print("\n📊 Database Statistics:")
    stats = api.get_database_stats()
    print(f"Total Questions: {stats['total_questions']}")
    for subject, data in stats['subjects'].items():
        print(f"{subject}: {data['total_questions']} questions")
    
    # Demo 2: Get English questions
    print("\n🇬🇧 Sample English Questions:")
    english_questions = api.get_questions_by_subject('english', 2)
    for i, q in enumerate(english_questions, 1):
        print(f"\n{i}. [{q['question_type']}] {q['question_text']}")
        for option, text in q['options'].items():
            print(f"   {option}) {text}")
        print(f"   ✅ Answer: {q['correct_answer']}")
    
    # Demo 3: Get Mathematics arithmetic questions
    print("\n🔢 Mathematics Arithmetic Questions:")
    math_questions = api.get_quiz_questions('mathematics', 'Arithmetic', 2)
    for i, q in enumerate(math_questions, 1):
        print(f"\n{i}. {q['question_text']}")
        for option, text in q['options'].items():
            print(f"   {option}) {text}")
        print(f"   ✅ Answer: {q['correct_answer']}")
    
    # Demo 4: Mixed quiz
    print("\n🎯 Mixed Subject Quiz (2 questions each):")
    mixed_quiz = api.get_mixed_quiz(2)
    for i, q in enumerate(mixed_quiz, 1):
        print(f"\n{i}. [{q['subject']} - {q['question_type']}]")
        print(f"   {q['question_text']}")
        for option, text in q['options'].items():
            print(f"   {option}) {text}")
        print(f"   ✅ Answer: {q['correct_answer']}")
    
    # Demo 5: Question types breakdown
    print("\n📋 Available Question Types:")
    for subject in ['english', 'mathematics', 'general_knowledge']:
        print(f"\n{subject.title()}:")
        types = api.get_question_types_by_subject(subject)
        for type_info in types:
            print(f"  • {type_info['type']}: {type_info['count']} questions")
    
    print("\n" + "=" * 60)
    print("✅ API Demo Complete! Database is ready for integration.")

if __name__ == "__main__":
    demo_api_usage()
