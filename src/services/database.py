"""
Database service for managing SQLite database operations
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

class DatabaseService:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../data/reports.db')

        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(self):
        """Create all database tables"""
        with self.get_connection() as conn:
            # Activities table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type VARCHAR(50) NOT NULL,
                    sub_category VARCHAR(50),
                    sub_category_other TEXT,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    start_time TIME,
                    end_time TIME,
                    venue VARCHAR(200),
                    collaboration_sponsor TEXT,
                    highlights TEXT,
                    key_takeaway TEXT,
                    summary TEXT,
                    follow_up_plan TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Speakers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS speakers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    title_position VARCHAR(100),
                    organization VARCHAR(150),
                    contact_info VARCHAR(200),
                    presentation_title VARCHAR(200),
                    profile_image_path VARCHAR(500),
                    profile_text TEXT,
                    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
                )
            ''')

            # Participants table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL,
                    participant_type VARCHAR(20) NOT NULL,
                    count INTEGER NOT NULL,
                    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
                )
            ''')

            # Report preparers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS report_preparers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    designation VARCHAR(100),
                    signature_image_path VARCHAR(500),
                    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
                )
            ''')

            # Activity photos table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS activity_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL,
                    photo_path VARCHAR(500) NOT NULL,
                    photo_type VARCHAR(20) DEFAULT 'activity',
                    caption TEXT,
                    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
                )
            ''')

            conn.commit()

    def save_activity(self, activity_data: Dict[str, Any]) -> int:
        """Save or update activity data"""
        with self.get_connection() as conn:
            if 'id' in activity_data and activity_data['id']:
                # Update existing activity
                activity_id = activity_data['id']
                conn.execute('''
                    UPDATE activities SET
                        activity_type=?, sub_category=?, sub_category_other=?,
                        start_date=?, end_date=?, start_time=?, end_time=?,
                        venue=?, collaboration_sponsor=?, highlights=?,
                        key_takeaway=?, summary=?, follow_up_plan=?,
                        updated_at=?
                    WHERE id=?
                ''', (
                    activity_data.get('activity_type'),
                    activity_data.get('sub_category'),
                    activity_data.get('sub_category_other'),
                    activity_data.get('start_date'),
                    activity_data.get('end_date'),
                    activity_data.get('start_time'),
                    activity_data.get('end_time'),
                    activity_data.get('venue'),
                    activity_data.get('collaboration_sponsor'),
                    activity_data.get('highlights'),
                    activity_data.get('key_takeaway'),
                    activity_data.get('summary'),
                    activity_data.get('follow_up_plan'),
                    datetime.now(),
                    activity_id
                ))
            else:
                # Insert new activity
                cursor = conn.execute('''
                    INSERT INTO activities (
                        activity_type, sub_category, sub_category_other,
                        start_date, end_date, start_time, end_time,
                        venue, collaboration_sponsor, highlights,
                        key_takeaway, summary, follow_up_plan
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    activity_data.get('activity_type'),
                    activity_data.get('sub_category'),
                    activity_data.get('sub_category_other'),
                    activity_data.get('start_date'),
                    activity_data.get('end_date'),
                    activity_data.get('start_time'),
                    activity_data.get('end_time'),
                    activity_data.get('venue'),
                    activity_data.get('collaboration_sponsor'),
                    activity_data.get('highlights'),
                    activity_data.get('key_takeaway'),
                    activity_data.get('summary'),
                    activity_data.get('follow_up_plan')
                ))
                activity_id = cursor.lastrowid

            conn.commit()
            return activity_id

    def save_speakers(self, activity_id: int, speakers: List[Dict[str, Any]]):
        """Save speaker data for an activity"""
        with self.get_connection() as conn:
            # Remove existing speakers for this activity
            conn.execute('DELETE FROM speakers WHERE activity_id=?', (activity_id,))

            # Insert new speakers
            for speaker in speakers:
                conn.execute('''
                    INSERT INTO speakers (
                        activity_id, name, title_position, organization,
                        contact_info, presentation_title, profile_image_path, profile_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    activity_id,
                    speaker.get('name'),
                    speaker.get('title_position'),
                    speaker.get('organization'),
                    speaker.get('contact_info'),
                    speaker.get('presentation_title'),
                    speaker.get('profile_image_path'),
                    speaker.get('profile_text')
                ))

            conn.commit()

    def save_participants(self, activity_id: int, participants: List[Dict[str, Any]]):
        """Save participant data for an activity"""
        with self.get_connection() as conn:
            # Remove existing participants for this activity
            conn.execute('DELETE FROM participants WHERE activity_id=?', (activity_id,))

            # Insert new participants
            for participant in participants:
                conn.execute('''
                    INSERT INTO participants (activity_id, participant_type, count)
                    VALUES (?, ?, ?)
                ''', (
                    activity_id,
                    participant.get('participant_type'),
                    participant.get('count')
                ))

            conn.commit()

    def save_report_preparers(self, activity_id: int, preparers: List[Dict[str, Any]]):
        """Save report preparer data for an activity"""
        with self.get_connection() as conn:
            # Remove existing preparers for this activity
            conn.execute('DELETE FROM report_preparers WHERE activity_id=?', (activity_id,))

            # Insert new preparers
            for preparer in preparers:
                conn.execute('''
                    INSERT INTO report_preparers (
                        activity_id, name, designation, signature_image_path
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    activity_id,
                    preparer.get('name'),
                    preparer.get('designation'),
                    preparer.get('signature_image_path')
                ))

            conn.commit()

    def save_activity_photos(self, activity_id: int, photos: List[Dict[str, Any]]):
        """Save activity photo data for an activity"""
        with self.get_connection() as conn:
            # Remove existing photos for this activity
            conn.execute('DELETE FROM activity_photos WHERE activity_id=?', (activity_id,))

            # Insert new photos
            for photo in photos:
                conn.execute('''
                    INSERT INTO activity_photos (activity_id, photo_path, photo_type, caption)
                    VALUES (?, ?, ?, ?)
                ''', (
                    activity_id,
                    photo.get('photo_path'),
                    photo.get('photo_type', 'activity'),
                    photo.get('caption')
                ))

            conn.commit()

    def get_activity(self, activity_id: int) -> Optional[Dict[str, Any]]:
        """Get activity data by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM activities WHERE id=?', (activity_id,))
            activity = cursor.fetchone()

            if activity:
                return dict(activity)
            return None

    def get_speakers(self, activity_id: int) -> List[Dict[str, Any]]:
        """Get all speakers for an activity"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM speakers WHERE activity_id=?', (activity_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_participants(self, activity_id: int) -> List[Dict[str, Any]]:
        """Get all participants for an activity"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM participants WHERE activity_id=?', (activity_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_report_preparers(self, activity_id: int) -> List[Dict[str, Any]]:
        """Get all report preparers for an activity"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM report_preparers WHERE activity_id=?', (activity_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_activity_photos(self, activity_id: int) -> List[Dict[str, Any]]:
        """Get all activity photos"""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM activity_photos WHERE activity_id=?', (activity_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_full_activity_data(self, activity_id: int) -> Optional[Dict[str, Any]]:
        """Get complete activity data including all related tables"""
        activity = self.get_activity(activity_id)
        if not activity:
            return None

        return {
            'activity': activity,
            'speakers': self.get_speakers(activity_id),
            'participants': self.get_participants(activity_id),
            'report_preparers': self.get_report_preparers(activity_id),
            'photos': self.get_activity_photos(activity_id)
        }

    def list_activities(self) -> List[Dict[str, Any]]:
        """List all activities"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, activity_type, start_date, venue, created_at
                FROM activities
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]