import os
import unittest
from app import app, db
from s3_utils import S3Handler
from models import User, Course
from flask import current_app

class TestS3Integration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['AWS_BUCKET_NAME'] = os.getenv('AWS_BUCKET_NAME')
        self.app.config['AWS_REGION'] = os.getenv('AWS_REGION', 'eu-north-1')
        self.client = self.app.test_client()
        self.s3 = S3Handler()
        
        # Create test file
        self.test_file_path = 'test_upload.txt'
        with open(self.test_file_path, 'w') as f:
            f.write('Test content for S3 upload')
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_s3_connection(self):
        """Test S3 connection and bucket access"""
        print("\n=== Testing S3 Connection ===")
        try:
            # Test bucket access
            self.s3.s3_client.head_bucket(Bucket=self.s3.bucket_name)
            print("✓ Successfully connected to S3 bucket")
            self.assertTrue(True)
        except Exception as e:
            print(f"✗ Failed to connect to S3: {str(e)}")
            self.fail(f"S3 connection failed: {str(e)}")
    
    def test_file_upload(self):
        """Test file upload to S3"""
        print("\n=== Testing File Upload ===")
        try:
            with open(self.test_file_path, 'rb') as file:
                url = self.s3.upload_file(file, folder='test')
                print(f"✓ File uploaded successfully to: {url}")
                self.assertIsNotNone(url)
                self.assertTrue(url.startswith('https://'))
                return url
        except Exception as e:
            print(f"✗ Upload failed: {str(e)}")
            self.fail(f"Upload failed: {str(e)}")
    
    def test_file_deletion(self):
        """Test file deletion from S3"""
        print("\n=== Testing File Deletion ===")
        try:
            # First upload a file
            with open(self.test_file_path, 'rb') as file:
                url = self.s3.upload_file(file, folder='test')
            
            # Then delete it
            success = self.s3.delete_file(url)
            print(f"✓ File deleted successfully: {success}")
            self.assertTrue(success)
        except Exception as e:
            print(f"✗ Deletion failed: {str(e)}")
            self.fail(f"Deletion failed: {str(e)}")
    
    def test_profile_image_upload(self):
        """Test profile image upload workflow"""
        print("\n=== Testing Profile Image Upload ===")
        try:
            # Create test image file
            test_image_path = 'test_image.jpg'
            with open(test_image_path, 'wb') as f:
                f.write(b'fake image content')
            
            # Upload image
            with open(test_image_path, 'rb') as file:
                url = self.s3.upload_file(file, folder='profiles')
                print(f"✓ Profile image uploaded successfully to: {url}")
                self.assertIsNotNone(url)
            
            # Clean up
            os.remove(test_image_path)
            self.s3.delete_file(url)
        except Exception as e:
            print(f"✗ Profile image test failed: {str(e)}")
            self.fail(f"Profile image test failed: {str(e)}")
    
    def test_course_thumbnail_upload(self):
        """Test course thumbnail upload workflow"""
        print("\n=== Testing Course Thumbnail Upload ===")
        try:
            # Create test thumbnail file
            test_thumbnail_path = 'test_thumbnail.jpg'
            with open(test_thumbnail_path, 'wb') as f:
                f.write(b'fake thumbnail content')
            
            # Upload thumbnail
            with open(test_thumbnail_path, 'rb') as file:
                url = self.s3.upload_file(file, folder='thumbnails')
                print(f"✓ Course thumbnail uploaded successfully to: {url}")
                self.assertIsNotNone(url)
            
            # Clean up
            os.remove(test_thumbnail_path)
            self.s3.delete_file(url)
        except Exception as e:
            print(f"✗ Course thumbnail test failed: {str(e)}")
            self.fail(f"Course thumbnail test failed: {str(e)}")

def run_tests():
    """Run all S3 integration tests"""
    print("\n=== Starting S3 Integration Tests ===")
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests() 