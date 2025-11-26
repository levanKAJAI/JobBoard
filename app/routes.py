import os
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from app import db, login_manager
from app.models import User, Job
from app.forms import RegisterForm, LoginForm, JobForm, ProfileForm, AdminUserForm

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
@main.route('/jobs')
def index():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    query = Job.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title.ilike(like), Job.short_desc.ilike(like), Job.full_desc.ilike(like), Job.company.ilike(like)))
    if category:
        query = query.filter(Job.category == category)
    jobs = query.order_by(Job.date_posted.desc()).all()
    return render_template('index.html', jobs=jobs, q=q, category=category)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('ეს ელფოსტა უკვე რეგისტრირებულია.', 'danger')
            return render_template('register.html', form=form)
        hashed_pw = generate_password_hash(form.password.data)
        user = User(name=form.name.data, email=form.email.data.lower(), password=hashed_pw, role='user')
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"Registration success: {user.email}")
        flash('რეგისტრაცია წარმატებით დასრულდა!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            current_app.logger.info(f"Login success: {user.email}")
            flash('ავტორიზაცია წარმატებული!', 'success')
            return redirect(url_for('main.index'))
        else:
            current_app.logger.warning(f"Login failed: {form.email.data}")
            flash('არასწორი ელფოსტა ან პაროლი.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('გასვლა წარმატებით შესრულდა', 'info')
    return redirect(url_for('main.index'))

@main.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(title=form.title.data, short_desc=form.short_desc.data,
                  full_desc=form.full_desc.data, company=form.company.data,
                  salary=form.salary.data, location=form.location.data,
                  category=form.category.data, author=current_user)
        db.session.add(job)
        db.session.commit()
        current_app.logger.info(f"Job added: {job.title} by {current_user.email}")
        flash('ვაკანსია დაემატა!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_job.html', form=form)

@main.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@main.route('/author/<int:user_id>')
def author_jobs(user_id):
    user = User.query.get_or_404(user_id)
    jobs = Job.query.filter_by(user_id=user.id).order_by(Job.date_posted.desc()).all()
    return render_template('author_jobs.html', user=user, jobs=jobs)

@main.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.author != current_user:
        flash('თქვენ არ შეგიძლიათ ამ ვაკანსიის რედაქტირება!', 'danger')
        return redirect(url_for('main.index'))
    form = JobForm(obj=job)
    if form.validate_on_submit():
        job.title = form.title.data
        job.short_desc = form.short_desc.data
        job.full_desc = form.full_desc.data
        job.company = form.company.data
        job.salary = form.salary.data
        job.location = form.location.data
        job.category = form.category.data
        db.session.commit()
        current_app.logger.info(f"Job edited: {job.title} by {current_user.email}")
        flash('ვაკანსია განახლდა!', 'success')
        return redirect(url_for('main.job_detail', job_id=job.id))
    return render_template('add_job.html', form=form, edit=True)

@main.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.author != current_user:
        flash('თქვენ არ შეგიძლიათ ამ ვაკანსიის წაშლა!', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(job)
    db.session.commit()
    current_app.logger.info(f"Job deleted: {job.title} by {current_user.email}")
    flash('ვაკანსია წაიშალა!', 'info')
    return redirect(url_for('main.index'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data.lower()
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                flash('სურათის ფორმატი უნდა იყოს JPG/PNG.', 'danger')
                return render_template('profile.html', form=form, user=current_user)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(save_path)
            current_user.image = filename
        db.session.commit()
        flash('პროფილი განახლდა!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', form=form, user=current_user)

# Admin: მომხმარებლების სია + როლის ცვლილება inline
@main.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('ამ გვერდზე წვდომა შეზღუდულია (მხოლოდ ადმინი).', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('role')
        user = User.query.get_or_404(int(user_id))
        user.role = new_role
        db.session.commit()
        flash('როლი განახლდა!', 'success')
        return redirect(url_for('main.admin_users'))
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin_users.html', users=users)

@main.route('/admin/users/add', methods=['GET','POST'])
@login_required
def admin_add_user():
    if current_user.role != 'admin':
        flash('ამ ოპერაციის შესრულება შეზღუდულია (მხოლოდ ადმინი).', 'danger')
        return redirect(url_for('main.index'))
    form = AdminUserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('ეს ელფოსტა უკვე არსებობს.', 'danger')
            return render_template('admin_add_user.html', form=form)
        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            password=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"Admin added user: {user.email} ({user.role})")
        flash('მომხმარებელი დამატებულია!', 'success')
        return redirect(url_for('main.admin_users'))
    return render_template('admin_add_user.html', form=form)

# External API Integration
@main.route('/api_data')
def api_data():
    try:
        resp = requests.get('https://api.exchangerate.host/latest?base=USD', timeout=8)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get('rates', {})
        show = {k: rates.get(k) for k in ['EUR', 'GBP', 'GEL', 'JPY', 'TRY'] if k in rates}
        return render_template('api_data.html', rates=show, date=data.get('date'))
    except Exception as e:
        current_app.logger.error(f"API request error: {e}")
        flash('გარე API მონაცემების ჩატვირთვა ვერ მოხერხდა.', 'danger')
        return redirect(url_for('main.index'))

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html'), 404

@main.app_errorhandler(500)
def internal_error(e):
    return render_template('error_500.html'), 500
