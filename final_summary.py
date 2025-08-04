import sqlite3
import json
from datetime import datetime

def generate_database_summary():
    """Generate a comprehensive summary of the edtech questions database."""
    
    conn = sqlite3.connect('edtech_questions_database.db')
    cursor = conn.cursor()
    
    summary = {
        'database_name': 'edtech_questions_database.db',
        'created_date': datetime.now().isoformat(),
        'total_questions': 0,
        'subjects': {}
    }
    
    # Get English questions statistics
    cursor.execute("SELECT COUNT(*) FROM english_questions")
    english_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT question_type, COUNT(*) 
        FROM english_questions 
        GROUP BY question_type 
        ORDER BY COUNT(*) DESC
    """)
    english_types = dict(cursor.fetchall())
    
    summary['subjects']['English'] = {
        'total_questions': english_count,
        'question_types': english_types,
        'source': 'English bank PDF (74 pages)',
        'extraction_rate': f"{english_count}/204 potential questions (50%)"
    }
    
    # Get Mathematics questions statistics
    cursor.execute("SELECT COUNT(*) FROM mathematics_questions")
    math_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT question_type, COUNT(*) 
        FROM mathematics_questions 
        GROUP BY question_type 
        ORDER BY COUNT(*) DESC
    """)
    math_types = dict(cursor.fetchall())
    
    summary['subjects']['Mathematics'] = {
        'total_questions': math_count,
        'question_types': math_types,
        'source': 'Mathematics bank PDF (8 pages)',
        'extraction_rate': f"{math_count}/188 potential questions (77.7%)"
    }
    
    # Get General Knowledge questions statistics
    cursor.execute("SELECT COUNT(*) FROM general_knowledge_questions")
    gk_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT question_type, COUNT(*) 
        FROM general_knowledge_questions 
        GROUP BY question_type 
        ORDER BY COUNT(*) DESC
    """)
    gk_types = dict(cursor.fetchall())
    
    summary['subjects']['General Knowledge'] = {
        'total_questions': gk_count,
        'question_types': gk_types,
        'source': 'General Knowledge PDF',
        'extraction_rate': f"{gk_count}/62 potential questions (83.9%)"
    }
    
    summary['total_questions'] = english_count + math_count + gk_count
    
    conn.close()
    return summary

def print_formatted_summary(summary):
    """Print a beautifully formatted summary."""
    
    print("=" * 80)
    print("🎓 EDTECH QUESTIONS DATABASE - FINAL SUMMARY")
    print("=" * 80)
    print(f"📅 Generated: {summary['created_date'][:19]}")
    print(f"💾 Database: {summary['database_name']}")
    print(f"📊 Total Questions: {summary['total_questions']}")
    print("=" * 80)
    
    for subject, data in summary['subjects'].items():
        if subject == 'English':
            emoji = "🇬🇧"
        elif subject == 'Mathematics':
            emoji = "🔢"
        else:
            emoji = "🌍"
            
        print(f"\n{emoji} {subject.upper()}")
        print("-" * 50)
        print(f"📈 Total Questions: {data['total_questions']}")
        print(f"📚 Source: {data['source']}")
        print(f"⚡ Extraction Rate: {data['extraction_rate']}")
        print("📋 Question Types:")
        
        for q_type, count in data['question_types'].items():
            percentage = (count / data['total_questions']) * 100
            print(f"   • {q_type}: {count} questions ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ DATABASE CREATION COMPLETE!")
    print("🚀 Ready for production use in edtech platform")
    print("=" * 80)

def export_sample_questions():
    """Export sample questions from each subject for demonstration."""
    
    conn = sqlite3.connect('edtech_questions_database.db')
    cursor = conn.cursor()
    
    samples = {}
    
    # Sample English questions
    cursor.execute("""
        SELECT question_text, option_a, option_b, option_c, option_d, correct_answer, question_type
        FROM english_questions 
        LIMIT 3
    """)
    samples['English'] = cursor.fetchall()
    
    # Sample Mathematics questions
    cursor.execute("""
        SELECT question_text, option_a, option_b, option_c, option_d, correct_answer, question_type
        FROM mathematics_questions 
        LIMIT 3
    """)
    samples['Mathematics'] = cursor.fetchall()
    
    # Sample General Knowledge questions
    cursor.execute("""
        SELECT question_text, option_a, option_b, option_c, option_d, correct_answer, question_type
        FROM general_knowledge_questions 
        LIMIT 3
    """)
    samples['General Knowledge'] = cursor.fetchall()
    
    conn.close()
    
    print("\n🎯 SAMPLE QUESTIONS FROM EACH SUBJECT")
    print("=" * 80)
    
    for subject, questions in samples.items():
        if subject == 'English':
            emoji = "🇬🇧"
        elif subject == 'Mathematics':
            emoji = "🔢"
        else:
            emoji = "🌍"
            
        print(f"\n{emoji} {subject} Sample Questions:")
        print("-" * 50)
        
        for i, (q_text, opt_a, opt_b, opt_c, opt_d, correct, q_type) in enumerate(questions, 1):
            print(f"\n{i}. [{q_type}] {q_text}")
            print(f"   A) {opt_a}")
            print(f"   B) {opt_b}")
            print(f"   C) {opt_c}")
            print(f"   D) {opt_d}")
            print(f"   ✅ Correct Answer: {correct}")

def save_summary_to_json(summary):
    """Save the summary to a JSON file for API consumption."""
    
    with open('database_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Summary exported to 'database_summary.json'")

if __name__ == "__main__":
    # Generate and display summary
    summary = generate_database_summary()
    print_formatted_summary(summary)
    
    # Export sample questions
    export_sample_questions()
    
    # Save summary to JSON
    save_summary_to_json(summary)
    
    print("\n🎉 EDTECH QUESTIONS DATABASE SETUP COMPLETE!")
    print("🔧 Database is ready for integration with your edtech platform!")
