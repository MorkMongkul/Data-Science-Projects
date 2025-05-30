import os
import logging
from app import app, db
from models import User, Course
from s3_utils import S3Handler
from flask import current_app

def migrate_profile_images():
    """Migrate user profile images to S3"""
    with app.app_context():
        s3 = S3Handler()
        users = User.query.filter(User.profile_image_url.isnot(None)).all()
        
        print("\n=== Migrating Profile Images ===")
        for user in users:
            if user.profile_image_url and not user.profile_image_url.startswith('https://'):
                try:
                    # Get local file path
                    local_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', 
                                            os.path.basename(user.profile_image_url))
                    
                    if os.path.exists(local_path):
                        print(f"\nProcessing user: {user.username}")
                        print(f"Local file: {local_path}")
                        
                        # Upload to S3
                        with open(local_path, 'rb') as file:
                            s3_url = s3.upload_file(file, folder='profiles')
                            if s3_url:
                                user.profile_image_url = s3_url
                                db.session.commit()
                                print(f"Successfully migrated to: {s3_url}")
                            else:
                                print(f"Failed to upload for user {user.username}")
                except Exception as e:
                    print(f"Error migrating profile image for user {user.username}: {str(e)}")

def migrate_course_thumbnails():
    """Migrate course thumbnails to S3"""
    with app.app_context():
        s3 = S3Handler()
        courses = Course.query.filter(Course.thumbnail_url.isnot(None)).all()
        
        print("\n=== Migrating Course Thumbnails ===")
        for course in courses:
            if course.thumbnail_url and not course.thumbnail_url.startswith('https://'):
                try:
                    # Get local file path
                    local_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', 
                                            os.path.basename(course.thumbnail_url))
                    
                    if os.path.exists(local_path):
                        print(f"\nProcessing course: {course.title}")
                        print(f"Local file: {local_path}")
                        
                        # Upload to S3
                        with open(local_path, 'rb') as file:
                            s3_url = s3.upload_file(file, folder='thumbnails')
                            if s3_url:
                                course.thumbnail_url = s3_url
                                db.session.commit()
                                print(f"Successfully migrated to: {s3_url}")
                            else:
                                print(f"Failed to upload for course {course.title}")
                except Exception as e:
                    print(f"Error migrating thumbnail for course {course.title}: {str(e)}")

def verify_migration():
    """Verify that files have been migrated correctly"""
    with app.app_context():
        print("\n=== Verifying Migration ===")
        
        # Check profile images
        users = User.query.filter(User.profile_image_url.isnot(None)).all()
        s3_profiles = sum(1 for user in users if user.profile_image_url.startswith('https://'))
        print(f"\nProfile Images:")
        print(f"Total users with images: {len(users)}")
        print(f"Successfully migrated to S3: {s3_profiles}")
        
        # Check course thumbnails
        courses = Course.query.filter(Course.thumbnail_url.isnot(None)).all()
        s3_thumbnails = sum(1 for course in courses if course.thumbnail_url.startswith('https://'))
        print(f"\nCourse Thumbnails:")
        print(f"Total courses with thumbnails: {len(courses)}")
        print(f"Successfully migrated to S3: {s3_thumbnails}")

if __name__ == '__main__':
    print("Starting S3 Migration Demo...")
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Run migrations
        migrate_profile_images()
        migrate_course_thumbnails()
        
        # Verify results
        verify_migration()
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        raise 