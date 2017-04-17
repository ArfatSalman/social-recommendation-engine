from flask import Flask, render_template, request, abort, flash
from flask import url_for, redirect, jsonify
from models import User, graph
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from forms import RegistrationForm, LoginForm, PostForm, LikePostForm, FollowForm, UnfollowForm

app = Flask(__name__)
app.secret_key = 'Arfat'
login_manager = LoginManager(app)

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
        #tags = category + ',' + tags


        if not current_user.add_post(title, tags, category, text):
            flash('Post was unsuccessful', 'danger')
            return redirect(url_for('.post'))

        flash('The post was successful.','success')
        return redirect(url_for('index'))
    return render_template('post.html', post_form=post_form)



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
            abort(400)

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
            return abort('404')

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