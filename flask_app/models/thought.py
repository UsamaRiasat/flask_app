from unittest import result
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

class Thought:

    def __init__(self, data):
        self.id = data['id']
        self.thought_content = data['thought_content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users_who_liked=data['users_who_liked']
        self.likes = data['likes']
        self.first_name = data['first_name']
        self.user_id = data['user_id']

    @classmethod
    def get_all(cls):
        query = "SELECT thoughts.*, users.first_name from thoughts inner Join users on users.id=thoughts.user_id ORDER BY thoughts.likes DESC;"
        results = connectToMySQL('thoughts_of_user').query_db(query)
        thoughts = []
        for row in results:
            # get the users who liked the thought
            query = "SELECT users.first_name FROM users INNER JOIN thought_was_like_from_users ON users.id=thought_was_like_from_users.users_id WHERE thought_was_like_from_users.thought_id = %(thought_id)s;"
            data = {
                'thought_id': row['id']
            }
            results2 = connectToMySQL('thoughts_of_user').query_db(query,data)
            row['users_who_liked'] = results2
            thoughts.append( cls(row))
        return thoughts


    @classmethod
    def get_user_thoughts(cls, u_id):
        query = "SELECT thoughts.*, users.first_name from thoughts inner Join users on users.id=thoughts.user_id and thoughts.user_id ="+str(u_id)+";"
        results = connectToMySQL('thoughts_of_user').query_db(query)
        thoughts = []
        for row in results:
            # get the users who liked the thought
            query = "SELECT users.first_name FROM users INNER JOIN thought_was_like_from_users ON users.id=thought_was_like_from_users.users_id WHERE thought_was_like_from_users.thought_id = %(thought_id)s;"
            data = {
                'thought_id': row['id']
            }
            results2 = connectToMySQL('thoughts_of_user').query_db(query,data)
            row['users_who_liked'] = results2
            thoughts.append( cls(row))
        return thoughts

    @classmethod
    def get_one(cls,data):
        query = "SELECT thoughts.*, users.first_name FROM thoughts INNER JOIN users ON users.id=thoughts.user_id WHERE thoughts.id = %(thought_id)s;"
        results = connectToMySQL('thoughts_of_user').query_db(query,data)
        query = "SELECT DISTINCT users.first_name, users.id FROM users INNER JOIN thought_was_like_from_users ON users.id=thought_was_like_from_users.users_id WHERE thought_was_like_from_users.thought_id = %(thought_id)s;"
        results2 = connectToMySQL('thoughts_of_user').query_db(query,data)
        results[0]['users_who_liked'] = results2
        return cls( results[0] )


    @classmethod
    def save(cls, data):
        query = 'INSERT INTO thoughts (thought_content, user_id) VALUES ( %(thought_content)s, %(user_id)s);' #rregulloje
        return connectToMySQL('thoughts_of_user').query_db(query, data)

    @classmethod
    def update(cls, data):
        query = 'UPDATE thoughts SET likes = %(likes)s WHERE id=%(thought_id)s;'
        return connectToMySQL('thoughts_of_user').query_db(query, data)

    @classmethod
    def addLike(cls, data):
        query = "INSERT INTO thought_was_like_from_users (thought_id,users_id) VALUES (%(thought_id)s,%(user_id)s);"
        res = connectToMySQL('thoughts_of_user').query_db(query,data)
        query = 'UPDATE thoughts SET likes = (thoughts.likes + 1) WHERE id=%(thought_id)s;'
        res = connectToMySQL('thoughts_of_user').query_db(query,data)
        if(res):
            return connectToMySQL('thoughts_of_user').query_db(query,data)

    @classmethod
    def removeLike(cls, data):
        query = "DELETE FROM thought_was_like_from_users WHERE thought_id=%(thought_id)s AND users_id=%(user_id)s;"
        res = connectToMySQL('thoughts_of_user').query_db(query,data)
        query = 'UPDATE thoughts SET likes = (thoughts.likes - 1) WHERE id=%(thought_id)s;'
        return connectToMySQL('thoughts_of_user').query_db(query,data)

    @classmethod
    def destroy(cls,data):
        query = "DELETE FROM thoughts WHERE id = %(id)s;"
        return connectToMySQL('thoughts_of_user').query_db(query,data)

    @classmethod
    def getUsersWhoLiked(cls, data):
        query = "SELECT thought_was_like_from_users.* FROM thought_was_like_from_users LEFT JOIN thoughts.* ON thought_was_like_from_users.thought_id = thoughts.id LEFT JOIN users ON thought_was_like_from_users.users_id = users.id WHERE thoughts.id = %(thought_id)s;"
        results = connectToMySQL('thoughts_of_user').query_db(query)
        myThought = Thought.get_one(data)
        for row in results:
            myThought.users_who_liked.append(row['email'])
        myThought.likes=len(myThought.users_who_liked)
        print(myThought.users_who_liked)
        return myThought

    @staticmethod
    def validate_thought(thought):
        is_valid = True
        if len(thought['thought_content']) == 0:
            flash("Thought is required","addThoughts")
            is_valid= False
        if len(thought['thought_content']) < 5:
            flash("Thought content must be at least 5 characters","addThought")
            is_valid= False
        return is_valid
