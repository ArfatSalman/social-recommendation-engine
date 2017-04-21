import os
from time import time
from werkzeug import secure_filename
from flask import Flask, render_template, request, abort, flash
from flask import url_for, redirect, jsonify, current_app
from models import User, graph
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from forms import RegistrationForm, LoginForm, PostForm, LikePostForm, FollowForm, UnfollowForm

app = Flask(__name__)
app.secret_key = 'Arfat'
login_manager = LoginManager(app)


with app.app_context():
    current_app.config['ALLOWED_EXTENSIONS'] = ['jpg', 'jpeg','png']
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER = os.path.join(os.path.abspath('app'), 'static')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_upload_file_url(image):
    if image:
        unique = str(int(time())) # added for uniqueness
        if not allowed_file(image.filename):
            return abort(406)

        filename = ('%s_' % unique + secure_filename(image.filename)).lower()

        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename.lower()))

        return url_for('static', filename=filename, _external=True)

    return None

@login_manager.user_loader
def user_loader(username):
    return User.select(graph, username).first()


@app.route('/')
def index():
    category = request.args.get('type', None)
    if category not in ['movies', 'songs', 'books']:
        category = None

    like_form = LikePostForm()
    return render_template('index.html', like=like_form, category=category)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    post_form = PostForm(request.form)

    if post_form.validate_on_submit():
        title = post_form.title.data
        tags = post_form.tags.data
        text = post_form.text.data
        category = post_form.category.data
        link = post_form.link.data
        image = request.files['image']

        image_url = get_upload_file_url(image)
        if image_url is None:
            flash('File uplaod unsuccessful', 'danger')
            return redirect(url_for('.post'))


        if not current_user.add_post(title, link, tags, category, text, image_url):
            flash('Post was unsuccessful', 'danger')
            return redirect(url_for('.post'))

        flash('The post was successful.','success')
        return redirect(url_for('index'))
    return render_template('post.html', post_form=post_form)


@app.route('/remove-tag')
@login_required
def remove_tag():
    tagname = request.args.get('tag', None)
    
    if tagname:
        current_user.remove_tag(tagname)

    return redirect(url_for('.profile', email=current_user.email))


@app.route('/like-post', methods=['POST'])
@login_required
def like_post():
    form = LikePostForm()
    if form.validate_on_submit():
        post_id = form.post_id.data
        current_user.like_post(post_id)

        flash('Post like successful.','success')
    return redirect(url_for('.index'))


@app.route('/get-tags')
@login_required
def get_tags():
    partial_tag = request.args.get('q', "")
    record_list = User.get_tags(partial_tag)
    return jsonify(tags=record_list.evaluate())

@app.route('/follow', methods=['POST'])
@login_required
def follow():
    form = FollowForm()
    if form.validate_on_submit():
        email = form.email.data
        if email == current_user.email:
            return abort(404)
        current_user.follows(email)

        flash("You've followed %s" % email, 'success')
    
    return redirect(url_for('.profile', email=current_user.email))


@app.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    unfollow_form = UnfollowForm()
    if unfollow_form.validate_on_submit():
        email = unfollow_form.email.data

        current_user.unfollow(email)

        flash('You have unfollowed %s ' % email, 'warning')

    return redirect(url_for('.profile', email=current_user.email))


@app.route('/profile/<email>', methods=['GET', 'POST'])
@login_required
def profile(email):
    form = FollowForm()
    unfollow = UnfollowForm()
    return render_template('profile.html', user_node=User.get_user(email), 
        form=form, unfollow=unfollow)


@app.route('/followings')
@login_required
def feed():
    form = LikePostForm()
    return render_template('followings.html', like=form)

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()
    
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        is_registered = User.register_user(email, username, password)

        if not is_registered:
            flash('The email is already registered.', 'danger')
            return redirect(url_for('.register'))

        return redirect(url_for('.index'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.select(graph, email).first()

        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('.login'))

        if User.verify_user_password(user.email, password):
            login_user(user)
        else:
            flash('Wrong username/password', 'danger')
            return redirect(url_for('.login'))

        return redirect(url_for('.index'))

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


if __name__ == '__main__':
    app.run(debug=True)                         