
from app.models import User
import forgery_py as feed
from app.views import app
from app.models import graph
from random import choice, sample, randint

GMAIL = '@gmail.com'

USERS = ['arfat', 'Nga', 'Wen', 'Armanda', 'Wendolyn', 
         'Alane', 'Clarinda', 'Dorthey', 'Michelle', 
         'Wanita', 'Brigida', 'Gwendolyn', 'Shawnna', 
         'Kym', 'Florine', 'Nilsa', 'Clifford', 'Myrtie', 
         'Elodia', 'Mason', 'Ardell', 'Pennie', 'Maryln', 
         'Idell', 'Mee', 'Callie', 'Theda', 'Alfonzo', 
         'Louanne', 'Tempie', 'Agnus', 'Samatha', 'Marceline', 
         'Alesia', 'Deane', 'Elizbeth', 'Debby', 'Marilynn', 
         'Salome', 'Mariel', 'Demarcus', 'Dusti', 'Jackeline', 
         'Patti', 'Ebonie', 'Angelia', 'Chae', 'Beatrice', 
         'Gilberto', 'Blanch', 'Wai', 'Robert', 'Ela', 'Jone', 
         'Joni', 'Catrina', 'Luvenia', 'Deidre', 'Amberly', 
         'Ozella', 'Sharice', 'Temika', 'Zonia', 'Corrin', 
         'Elouise', 'Michel', 'Ramiro', 'Shea', 'Caleb', 
         'Mignon', 'Hubert', 'Eliz', 'Daisey', 'Jose', 
         'Dong', 'Mittie', 'Rochell', 'Nyla', 'Lavonda', 
         'Kaila', 'Candyce', 'Hermina', 'Devon', 'Alisha', 
         'Mindy', 'Alma', 'Lenny', 'Cathi', 'Audie', 'Nathalie', 
         'Ingrid', 'Curtis', 'Isa', 'Janette', 'Jacques', 
         'Annamarie', 'Ashanti', 'Joyce', 'Gertha', 'Monroe']

CAT = ['articles', 'songs', 'movies']

TAGS = ['pedal', 'four', 'smile', 'honorable', 'raspy', 
        'uncovered', 'pig', 'rule', 'drag', 'neck', 
        'plant', 'torpid', 'tax', 'accidental', 
        'false', 'waggish', 'soggy', 'note', 'necessary', 
        'screw', 'changeable', 'ad hoc', 'arithmetic', 
        'animal', 'giants', 'mate', 'tender', 'unable', 
        'homely', 'actor', 'angle', 'swim', 'overconfident', 
        'ultra', 'billowy', 'colossal', 'consist', 'land', 
        'exuberant', 'kitty', 'party', 'meddle', 'ants', 
        'weather', 'gaping', 'letter', 'friends', 'harmonious', 
        'command', 'rice', 'calculate', 'oval', 'hop', 'wacky', 
        'damaging', 'temporary', 'grip', 'sail', 'political', 
        'frightening', 'superficial', 'advise', 
        'unequaled', 'long', 'soap', 'start', 'mixed', 
        'scarce', 'guide', 'things', 'verse', 'early', 
        'sharp', 'teeny', 'discover', 'hair', 'humorous', 
        'tall', 'boundary', 'synonymous', 'flowers', 'receive', 
        'efficient', 'special', 'condemned', 'blood', 'stingy', 
        'downtown', 'shape', 'mint', 'diligent', 'big', 
        'spray', 'brown', 'tour', 'stretch', 'pass', 
        'depressed', 'trouble', 'clap']

app.config['WTF_CSRF_ENABLED'] = False

PASS = '12345'
test_client = app.test_client()


def get_all_post_id():
    query="""
        MATCH (p:Post)
        RETURN COLLECT(p.id)
    """
    return graph.run(query).evaluate()

def like_post(post_id):
    return test_client.post('/like-post',data=dict(post_id=post_id), 
        follow_redirects=True)


def register_all_users():
    for user in USERS:
        register(user, PASS)

def choose_user():
    return choice(USERS)

def get_tags():
    limit = randint(1, len(TAGS)-1) % 5
    return ",".join(sample(TAGS, limit))


def login(email, password):
    print ('Logged in as: '+email)
    email = email  + GMAIL
    return test_client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def register(username, password):
    email = username + GMAIL
    return test_client.post('/register', data=dict(
        email=email,
        username=username,
        password=password), follow_redirects=True)

def logout():
    return test_client.get('/logout', follow_redirects=True)


def add_post():
    return test_client.post('/post', data=dict(
        title=feed.lorem_ipsum.title(),
        tags=get_tags(),
        category=choice(CAT),
        text=feed.lorem_ipsum.paragraphs(5)), follow_redirects=True)

def follow():
    email = choose_user() + GMAIL
    return test_client.post('/follow', 
            data=dict(
                email=email), follow_redirects=True)

def like_random_posts(limit):
    post_ids = get_all_post_id()
    for i in range(limit):
        login(choose_user(), PASS)
        like_post(choice(post_ids))
        logout()

def random_data():
    login(choose_user(), PASS)
    
    if randint(0, 100) < 25:
        add_post()
    else:
        print 'Skipping add_post()'
    
    if randint(0, 100) < 50:
        follow()
    else:
        print 'Skipping follow()'
    
    logout()


if __name__ == "__main__":
    for i in range(1, 100):
        random_data()

    like_random_posts(100)
