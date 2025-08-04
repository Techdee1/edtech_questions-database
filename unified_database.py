#!/usr/bin/env python3
"""
Unified Questions Database Manager
Creates and manages a single database with separate tables for English, Mathematics, and General Knowledge
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedQuestionDatabase:
    def __init__(self, db_path: str = "edtech_questions_database.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_all_tables(self):
        """Create all subject tables in the unified database"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # English Questions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS english_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_number TEXT NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
                question_type TEXT,
                difficulty_level TEXT DEFAULT 'medium',
                source TEXT DEFAULT 'english_bank_pdf',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Mathematics Questions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mathematics_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_number TEXT NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
                question_type TEXT,
                topic TEXT,
                difficulty_level TEXT DEFAULT 'medium',
                source TEXT DEFAULT 'mathematics_bank_pdf',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # General Knowledge Questions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS general_knowledge_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_number TEXT NOT NULL,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
                question_type TEXT,
                category TEXT,
                difficulty_level TEXT DEFAULT 'medium',
                source TEXT DEFAULT 'general_knowledge_pdf',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Metadata table for database info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                total_questions INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                extraction_source TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        logger.info(f"All tables created in {self.db_path}")
        return conn
    
    def get_table_stats(self):
        """Get statistics for all tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        stats = {}
        tables = ['english_questions', 'mathematics_questions', 'general_knowledge_questions']
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                
                cursor.execute(f'SELECT COUNT(DISTINCT question_type) FROM {table}')
                types_count = cursor.fetchone()[0]
                
                cursor.execute(f'SELECT question_type, COUNT(*) FROM {table} GROUP BY question_type ORDER BY COUNT(*) DESC')
                type_distribution = cursor.fetchall()
                
                stats[table] = {
                    'total_questions': count,
                    'question_types': types_count,
                    'type_distribution': type_distribution
                }
            except sqlite3.OperationalError:
                stats[table] = {'total_questions': 0, 'question_types': 0, 'type_distribution': []}
        
        conn.close()
        return stats
    
    def migrate_english_questions(self, old_db_path: str = "english_questions.db"):
        """Migrate existing English questions to the unified database"""
        try:
            # Connect to old database
            old_conn = sqlite3.connect(old_db_path)
            old_cursor = old_conn.cursor()
            
            # Get all questions from old database
            old_cursor.execute('''
                SELECT question_number, question_text, option_a, option_b, option_c, option_d, 
                       correct_answer, question_type, created_at
                FROM english_questions
            ''')
            questions = old_cursor.fetchall()
            old_conn.close()
            
            # Insert into new unified database
            conn = self.connect()
            cursor = conn.cursor()
            
            # Clear existing English questions if any
            cursor.execute('DELETE FROM english_questions')
            
            # Insert migrated questions
            for question in questions:
                cursor.execute('''
                    INSERT INTO english_questions 
                    (question_number, question_text, option_a, option_b, option_c, option_d, 
                     correct_answer, question_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', question)
            
            conn.commit()
            logger.info(f"Migrated {len(questions)} English questions to unified database")
            
            # Update metadata
            cursor.execute('''
                INSERT OR REPLACE INTO database_metadata 
                (table_name, total_questions, extraction_source, notes)
                VALUES (?, ?, ?, ?)
            ''', ('english_questions', len(questions), old_db_path, 'Migrated from separate English database'))
            
            conn.commit()
            conn.close()
            return len(questions)
            
        except Exception as e:
            logger.error(f"Error migrating English questions: {e}")
            return 0
    
    def print_database_summary(self):
        """Print a summary of the unified database"""
        stats = self.get_table_stats()
        
        print(f"\n{'='*60}")
        print(f"EDTECH QUESTIONS DATABASE SUMMARY")
        print(f"{'='*60}")
        print(f"Database: {self.db_path}")
        
        total_questions = 0
        for table, data in stats.items():
            subject = table.replace('_questions', '').replace('_', ' ').title()
            count = data['total_questions']
            total_questions += count
            
            print(f"\n{subject}:")
            print(f"  Total Questions: {count}")
            if data['type_distribution']:
                print(f"  Question Types:")
                for q_type, type_count in data['type_distribution']:
                    percentage = (type_count / count * 100) if count > 0 else 0
                    print(f"    {q_type}: {type_count} ({percentage:.1f}%)")
        
        print(f"\nGRAND TOTAL: {total_questions} questions across all subjects")
        print(f"{'='*60}")
    
    def get_random_questions(self, subject: str, count: int = 10, question_type: str = None):
        """Get random questions from a specific subject"""
        table_name = f"{subject}_questions"
        conn = self.connect()
        cursor = conn.cursor()
        
        query = f'''
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, 
                   correct_answer, question_type
            FROM {table_name}
            WHERE 1=1
        '''
        params = []
        
        if question_type:
            query += ' AND question_type = ?'
            params.append(question_type)
        
        query += ' ORDER BY RANDOM() LIMIT ?'
        params.append(count)
        
        cursor.execute(query, params)
        questions = cursor.fetchall()
        conn.close()
        
        return questions


def main():
    """Main function to set up the unified database"""
    db = UnifiedQuestionDatabase()
    
    # Create all tables
    db.create_all_tables()
    
    # Migrate existing English questions
    migrated_count = db.migrate_english_questions()
    
    # Print summary
    db.print_database_summary()
    
    print(f"\n✅ Unified database setup complete!")
    print(f"📁 Database file: {db.db_path}")
    print(f"📊 Migrated {migrated_count} English questions")
    print(f"🔧 Ready for Mathematics and General Knowledge extraction")


if __name__ == "__main__":
    main()
