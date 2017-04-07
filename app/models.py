from py2neo import Graph, Node, Relationship, watch
from py2neo.ogm import GraphObject, Property
from uuid import uuid4
from datetime import datetime
from passlib.hash import bcrypt
from flask_login import UserMixin, current_user

URL = 'http://localhost:7474'

username = 'neo4j'
password = 'arfat78692'

graph = Graph(URL + '/db/data/', username=username, password=password)

# OGM of User Label
class User(GraphObject, UserMixin):
    __primarykey__ = 'email'

    email = Property()
    username = Property()
    password = Property()

    def __init__(self, email=''):
        return User.select(graph, email).first()

    def get_id(self):
        return self.email

    def add_post(self, title, tags, text):
        post = Node("Post",
                    id=str(uuid4()),
                    title=title,
                    text=text,
                    timestamp=timestamp(),
                    date=date()
                    )

        rel = Relationship(current_user.__ogm__.node, 
                           "PUBLISHED", 
                            post)
        graph.create(rel)

        tags = [tag.strip() for tag in tags.lower().split(',')]

        # Make all the tags and TAGGED rels
        for tag in tags:
            t = Node('Tag', name=tag)
            graph.merge(t)

            rel = Relationship(t, "TAGGED", post)
            graph.create(rel)

            # Make all the DEFINES rels
            self.make_define_relationships(tag)

        # update weights
        for tag in tags:
            if self.count_property_exists(tag):
                # update the relationship's count and weight 
                self.update_count_weight(tag)
            else:
                self.initial_weight_count(tag)

        return True

    def count_property_exists(self, tag_name):
        query = """
            MATCH (t:Tag {name: {tag_name}})-[rel:DEFINES]->(u:User {email: {user_email}})
            RETURN exists(rel.count) AS output
        """
        res = graph.run(query, user_email=self.email, tag_name=tag_name)
        return list(res)[0]['output']

    def update_count_weight(self, tagname):
        query = """
            MATCH (t:Tag)-[:DEFINES]->(u:User {email: {user_email}})
            WITH count(t) as total_tags, u

            MATCH (t:Tag {name: {tagname}})-[rel:DEFINES]->(u)
            SET rel.count = rel.count + 1
            RETURN rel
        """
        return graph.run(query, user_email=self.email, tagname=tagname)
        
    def make_define_relationships(self, tag):
        query="""
            MATCH (t:Tag {name: {tagname}}), (u:User {email: {user_email}})
            MERGE (t)-[rel:DEFINES]->(u)
            RETURN rel
        """
        return graph.run(query, user_email=self.email, tagname=tag)

    def initial_weight_count(self, tagname):
        query = """
            MATCH (t:Tag)-[:DEFINES]->(u:User {email: {user_email}})
            WITH count(t) as total_tags, u

            MATCH (t:Tag {name: {tagname}})-[rel:DEFINES]->(u)
            SET rel.count = 1
            RETURN rel
        """

        return graph.run(query, user_email=self.email, tagname=tagname)

    def get_todays_recent_posts(self):
        query="""
            MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
            WHERE post.date = {today}
            RETURN user.username as username, post, COLLECT(tag.name) AS tags
            ORDER BY post.timestamp DESC
            LIMIT 5
        """
        return graph.run(query, today=date())

    def get_recent_post(self):
        query="""
            MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
            WHERE user.email = {email}
            RETURN post, COLLECT(tag.name) AS tags
            ORDER BY post.timestamp DESC 
            LIMIT 5
        """

        return graph.run(query, email=self.email)

    def get_post_tags(self, post_id):
        query="""
            MATCH (post:Post {id: {post_id}})<-[:TAGGED]-(tag:Tag)
            RETURN COLLECT(DISTINCT tag.name) AS tags
        """
        for row in graph.run(query, post_id=post_id):
            return row['tags']

    def like_post(self, post_id):
        """
        MATCH (u:User {email: "arfat.salman@outlook.com"}),(p:Post{id: "2b12563c-c03d-4211-ae9d-043d150cefc6"})<-[:TAGGED]-(t:Tag)
        WITH collect(t) as tags, u
        FOREACH (tag in tags | MERGE (tag)-[d:DEFINES]-(u))
        RETURN p
        """

        query="""
            MATCH (post:Post {id: {post_id}}), (user:User {email: {email}})
            MERGE (user)-[r:LIKES]->(post)
            RETURN r
        """
        return graph.run(query, post_id=post_id, email=self.email)

    def has_liked_post(self, post_id):
        query = """
            MATCH (u:User {email: {email}}), (p:Post {id: {post_id}}) 
            RETURN exists((u)-[:LIKES]->(p)) AS likes"""

        res = graph.run(query, email=self.email, post_id=post_id)
        return list(res)[0]['likes']

    def follows(self, other_email):
        query="""
            MATCH (me:User {email: {email}}), (other:User {email: {other_email}})
            MERGE (me)-[r:FOLLOWS]->(other)
            RETURN r
        """

        return graph.run(query, email=self.email, other_email=other_email)


    def follow_feed(self):
        query="""
            MATCH (me:User {email: {my_email}})-[FOLLOWS]->(others:User)-[:PUBLISHED]->(posts:Post)
            RETURN posts, others AS user
        """

        return graph.run(query, my_email=self.email)

    def similarity_scores(self, limit=5):
        query="""
            MATCH (u:User {email: {user_email}})<-[first:DEFINES]-(t:Tag)-[second:DEFINES]->(they:User)
            WHERE NOT((u)-[:FOLLOWS]->(they))
            RETURN they, 
                   toFloat(sum(first.count*second.count))/ (sqrt(sum(first.count*first.count))*sqrt(sum(second.count*second.count))) AS sim,
                   COLLECT (distinct t.name) AS tags
            ORDER BY sim DESC
            LIMIT {limit}
        """

        return graph.run(query, user_email=self.email, limit=limit)

    def get_similar_posts(self):
        query="""
            MATCH (you:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
                  (they:User)-[:PUBLISHED]->(posts:Post)<-[:TAGGED]-(tag)
            WHERE you.email = {email} AND you <> they
            WITH they, 
                 COLLECT(DISTINCT tag.name) AS tags, 
                 posts, 
                 they AS user
            ORDER BY SIZE(tags) DESC 
            RETURN user, posts, tags
        """

        return graph.run(query, email=self.email)

    def get_commonality_of_user(self, email):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:User {email: {they} })
        MATCH (you:User {email: {you} })
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
                       (you)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        RETURN SIZE((they)-[:LIKES]->(:Post)<-[:PUBLISHED]-(you)) AS likes,
               COLLECT(DISTINCT tag.name) AS tags
        """

        return graph.run(query, they=email, you=self.email)

    def follows_users(self):
        query="""
            MATCH (me:User {email: {my_email}})-[:FOLLOWS]->(user:User)
            RETURN user
        """
        return graph.run(query, my_email=self.email)

    def following_users(self):
        query="""
            MATCH (me:User {email: {my_email}})<-[:FOLLOWS]-(user:User)
            RETURN user
        """
        return graph.run(query, my_email=self.email)

    def unfollow(self, email):
        query="""
            MATCH (me:User {email: {my_email}})-[rel:FOLLOWS]->(user:User {email: {other_email}})
            DELETE rel
            RETURN rel
        """

        return graph.run(query, my_email=self.email, other_email=email)

    @staticmethod
    def find_user_node(email):
        return graph.find_one('User', 'email', email)

    @staticmethod
    def register_user(email, username, password):
        if not User.find_user_node(email):
            user = User()
            user.email = email
            user.username = username
            user.password = bcrypt.encrypt(password)

            graph.push(user)
            return True
        return False

    @staticmethod
    def verify_user_password(email, password):
        user = User.find_user_node(email)
        if user:
            return bcrypt.verify(password, user['password'])
        return False


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%Y-%m-%d')