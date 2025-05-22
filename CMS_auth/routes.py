import logging
import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func

from app import app, db
from models import User, Course, Enrollment, Role, CourseVideo
from forms import (
    LoginForm, RegistrationForm, UserUpdateForm, CourseForm, 
    EnrollmentForm, PasswordChangeForm, CourseVideoForm
)
from auth import admin_required, instructor_required, instructor_or_admin_required

# Home page
@app.route('/')
def index():
    # Get some stats for the homepage
    course_count = Course.query.filter_by(is_active=True).count()
    user_count = User.query.count()
    enrollment_count = Enrollment.query.count()
    
    # Get featured courses (most enrolled)
    featured_courses = db.session.query(
        Course, func.count(Enrollment.id).label('enrollment_count')
    ).join(
        Enrollment
    ).filter(
        Course.is_active == True
    ).group_by(
        Course.id
    ).order_by(
        func.count(Enrollment.id).desc()
    ).limit(3).all()
    
    return render_template('index.html', 
                           course_count=course_count,
                           user_count=user_count,
                           enrollment_count=enrollment_count,
                           featured_courses=[c[0] for c in featured_courses])

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.info("Login route accessed")
    if current_user.is_authenticated:
        logging.info(f"User {current_user.username} is already authenticated")
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    logging.info(f"Request method: {request.method}")
    if form.validate_on_submit():
        logging.info(f"Form validated, attempting login for user: {form.username.data}")
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            logging.info(f"User found: {user.username}")
            if user.check_password(form.password.data):
                logging.info("Password check successful")
                login_user(user)
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(next_page or url_for('dashboard'))
            else:
                logging.warning("Password check failed")
                flash('Login failed. Please check your username and password.', 'danger')
        else:
            logging.warning(f"No user found with username: {form.username.data}")
            flash('Login failed. Please check your username and password.', 'danger')
    else:
        if form.errors:
            logging.warning(f"Form validation errors: {form.errors}")
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# User dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        # Admin dashboard stats
        user_count = User.query.count()
        course_count = Course.query.count()
        enrollment_count = Enrollment.query.count()
        
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
        
        return render_template('dashboard.html', 
                               user_count=user_count,
                               course_count=course_count,
                               enrollment_count=enrollment_count,
                               recent_users=recent_users,
                               recent_courses=recent_courses)
    
    elif current_user.is_instructor():
        # Instructor dashboard
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
        
        # Get enrollment data for instructor's courses
        course_enrollment_data = {}
        for course in courses:
            course_enrollment_data[course.id] = len(course.enrollments)
        
        return render_template('dashboard.html', 
                               courses=courses,
                               course_enrollment_data=course_enrollment_data)
    
    else:  # Student
        # Get enrolled courses
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        enrolled_courses = [enrollment.course for enrollment in enrollments]
        
        # Get available courses for enrollment
        available_courses = Course.query.filter(
            Course.is_active == True,
            ~Course.id.in_([course.id for course in enrolled_courses])
        ).all()
        
        return render_template('dashboard.html', 
                               enrolled_courses=enrolled_courses,
                               available_courses=available_courses)

# User profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserUpdateForm(
        original_username=current_user.username,
        original_email=current_user.email
    )
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        
        # Only admin can change roles
        if current_user.is_admin():
            current_user.role = form.role.data
            
        current_user.profile_image_url = form.profile_image_url.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.role.data = current_user.role
        form.profile_image_url.data = current_user.profile_image_url
    
    # Password change form
    password_form = PasswordChangeForm()
    
    return render_template('profile.html', form=form, password_form=password_form)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    
    return redirect(url_for('profile'))

# Admin routes
@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserUpdateForm(original_username=user.username, original_email=user.email)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = form.role.data
        user.profile_image_url = form.profile_image_url.data
        
        db.session.commit()
        flash(f'User {user.username} has been updated!', 'success')
        return redirect(url_for('admin_users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.role.data = user.role
        form.profile_image_url.data = user.profile_image_url
    
    return render_template('admin/users.html', form=form, user=user)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting self
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/enrollments')
@admin_required
def admin_enrollments():
    enrollments = Enrollment.query.all()
    return render_template('admin/enrollments.html', enrollments=enrollments)

@app.route('/admin/enrollments/delete/<int:enrollment_id>', methods=['POST'])
@admin_required
def admin_delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    db.session.delete(enrollment)
    db.session.commit()
    
    flash('Enrollment has been deleted!', 'success')
    return redirect(url_for('admin_enrollments'))

# Course routes
@app.route('/courses')
def courses_index():
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('courses/index.html', courses=courses)

def save_thumbnail(thumbnail_file):
    """Save the uploaded thumbnail and return its URL path."""
    if not thumbnail_file:
        return None
        
    filename = secure_filename(thumbnail_file.filename)
    # Create upload folder if it doesn't exist
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Save the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    thumbnail_file.save(file_path)
    
    # Return the URL path using url_for
    return url_for('uploaded_file', filename=filename)

@app.route('/courses/create', methods=['GET', 'POST'])
@instructor_or_admin_required
def create_course():
    form = CourseForm()
    
    if form.validate_on_submit():
        # Handle thumbnail upload
        thumbnail_url = form.thumbnail_url.data
        if form.thumbnail.data:
            thumbnail_url = save_thumbnail(form.thumbnail.data)
            
        course = Course(
            title=form.title.data,
            description=form.description.data,
            code=form.code.data,
            instructor_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_active=form.is_active.data,
            max_students=form.max_students.data,
            thumbnail_url=thumbnail_url
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course {course.title} has been created!', 'success')
        return redirect(url_for('courses_index'))
    
    return render_template('courses/create.html', form=form)

@app.route('/courses/<int:course_id>')
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = None
    
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            course_id=course.id, 
            student_id=current_user.id
        ).first()
    
    # Get instructor info
    instructor = User.query.get(course.instructor_id)
    
    # Get enrollment count
    enrollment_count = len(course.enrollments)
    
    return render_template('courses/view.html', 
                           course=course, 
                           enrollment=enrollment,
                           instructor=instructor,
                           enrollment_count=enrollment_count)

@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@instructor_or_admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if current user is the instructor or an admin
    if not current_user.is_admin() and course.instructor_id != current_user.id:
        flash('You do not have permission to edit this course.', 'danger')
        return redirect(url_for('courses_index'))
    
    form = CourseForm(original_code=course.code)
    
    if form.validate_on_submit():
        # Handle thumbnail upload
        thumbnail_url = form.thumbnail_url.data
        if form.thumbnail.data:
            # Delete old thumbnail if it exists and is a local file
            if course.thumbnail_url and 'uploaded_file' in course.thumbnail_url:
                old_filename = os.path.basename(course.thumbnail_url)
                old_file = os.path.join(current_app.config['UPLOAD_FOLDER'], old_filename)
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            thumbnail_url = save_thumbnail(form.thumbnail.data)
            
        course.title = form.title.data
        course.description = form.description.data
        course.code = form.code.data
        course.start_date = form.start_date.data
        course.end_date = form.end_date.data
        course.is_active = form.is_active.data
        course.max_students = form.max_students.data
        course.thumbnail_url = thumbnail_url
        
        db.session.commit()
        
        flash(f'Course {course.title} has been updated!', 'success')
        return redirect(url_for('view_course', course_id=course.id))
    
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        form.code.data = course.code
        form.start_date.data = course.start_date
        form.end_date.data = course.end_date
        form.is_active.data = course.is_active
        form.max_students.data = course.max_students
        form.thumbnail_url.data = course.thumbnail_url
    
    return render_template('courses/edit.html', form=form, course=course)

@app.route('/courses/delete/<int:course_id>', methods=['POST'])
@instructor_or_admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if current user is the instructor or an admin
    if not current_user.is_admin() and course.instructor_id != current_user.id:
        flash('You do not have permission to delete this course.', 'danger')
        return redirect(url_for('courses_index'))
    
    db.session.delete(course)
    db.session.commit()
    
    flash(f'Course {course.title} has been deleted!', 'success')
    return redirect(url_for('courses_index'))

# Enrollment routes
@app.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    if not current_user.is_student():
        flash('Only students can enroll in courses.', 'warning')
        return redirect(url_for('view_course', course_id=course_id))
    
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        course_id=course.id, 
        student_id=current_user.id
    ).first()
    
    if existing_enrollment:
        flash(f'You are already enrolled in {course.title}.', 'info')
        return redirect(url_for('view_course', course_id=course_id))
    
    # Check if course is full
    if course.is_full():
        flash(f'Sorry, {course.title} is already full.', 'warning')
        return redirect(url_for('view_course', course_id=course_id))
    
    # Create enrollment
    enrollment = Enrollment(
        course_id=course.id,
        student_id=current_user.id,
        status='active'
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'You have successfully enrolled in {course.title}!', 'success')
    return redirect(url_for('view_course', course_id=course_id))

@app.route('/courses/<int:course_id>/unenroll', methods=['POST'])
@login_required
def unenroll_course(course_id):
    enrollment = Enrollment.query.filter_by(
        course_id=course_id, 
        student_id=current_user.id
    ).first_or_404()
    
    course = Course.query.get_or_404(course_id)
    
    db.session.delete(enrollment)
    db.session.commit()
    
    flash(f'You have been unenrolled from {course.title}.', 'success')
    return redirect(url_for('dashboard'))

# Course video routes
@app.route('/courses/<int:course_id>/videos/add', methods=['GET', 'POST'])
@instructor_or_admin_required
def add_course_video(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if current user is the instructor or an admin
    if not current_user.is_admin() and course.instructor_id != current_user.id:
        flash('You do not have permission to add videos to this course.', 'danger')
        return redirect(url_for('view_course', course_id=course_id))
    
    form = CourseVideoForm()
    
    if form.validate_on_submit():
        video = CourseVideo(
            course_id=course.id,
            title=form.title.data,
            video_type=form.video_type.data,
            video_url=form.video_url.data,
            description=form.description.data,
            order=form.order.data
        )
        
        db.session.add(video)
        db.session.commit()
        
        flash(f'Video "{video.title}" has been added to the course!', 'success')
        return redirect(url_for('view_course', course_id=course_id))
    
    return render_template('courses/add_video.html', form=form, course=course)

@app.route('/courses/<int:course_id>/videos/<int:video_id>/delete', methods=['POST'])
@instructor_or_admin_required
def delete_course_video(course_id, video_id):
    video = CourseVideo.query.get_or_404(video_id)
    course = Course.query.get_or_404(course_id)
    
    # Check if current user is the instructor or an admin
    if not current_user.is_admin() and course.instructor_id != current_user.id:
        flash('You do not have permission to delete videos from this course.', 'danger')
        return redirect(url_for('view_course', course_id=course_id))
    
    db.session.delete(video)
    db.session.commit()
    
    flash(f'Video "{video.title}" has been deleted from the course.', 'success')
    return redirect(url_for('view_course', course_id=course_id))

# Serve uploaded files
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
