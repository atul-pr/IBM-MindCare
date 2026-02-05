"""
Database Module - SQLite for chat history and mood tracking
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = 'chatbot.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Mood tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood_score INTEGER NOT NULL CHECK(mood_score >= 1 AND mood_score <= 5),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crisis events log (for analytics, anonymized)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crisis_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crisis_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

def save_message(sender, message):
    """
    Save chat message to database
    
    Args:
        sender (str): 'user' or 'bot'
        message (str): Message content
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO messages (sender, message) VALUES (?, ?)',
            (sender, message)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving message: {e}")

def save_mood(mood_score):
    """
    Save mood rating to database
    
    Args:
        mood_score (int): Mood rating 1-5
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO mood_logs (mood_score) VALUES (?)',
            (mood_score,)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving mood: {e}")

def get_mood_history(limit=30):
    """
    Get recent mood history
    
    Args:
        limit (int): Number of recent entries to fetch
        
    Returns:
        list: Mood history entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT mood_score, timestamp FROM mood_logs ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'mood': row['mood_score'],
                'date': row['timestamp']
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching mood history: {e}")
        return []

def log_crisis_event(crisis_type):
    """
    Log crisis event for analytics (anonymized)
    
    Args:
        crisis_type (str): Type of crisis detected
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO crisis_events (crisis_type) VALUES (?)',
            (crisis_type,)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging crisis event: {e}")

def get_chat_history(limit=50):
    """
    Get recent chat history
    
    Args:
        limit (int): Number of messages to fetch
        
    Returns:
        list: Chat messages
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT sender, message, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'sender': row['sender'],
                'message': row['message'],
                'timestamp': row['timestamp']
            }
            for row in reversed(rows)  # Reverse to show oldest first
        ]
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return []
