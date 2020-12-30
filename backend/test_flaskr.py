import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Mm@0559372667','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.question = {
            'question': "best plyer?",
            'answer': "Mohammed Alshammari",
            'difficulty': "1",
            'category': 6
        }

    
    def tearDown(self):
        """Executed after reach test"""
        print("Done!")
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_404_get_categories(self):
        res = self.client().get('/categorie')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_404_paginated_questions(self):
        res = self.client().get('/questions?page=30000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question_by_ID(self):
        # create a new question to delete
        new_question = Question(
            question=self.question['question'],
            answer=self.question['answer'],
            category=self.question['category'],
            difficulty=self.question['difficulty']
        )
        new_question.insert()
        res = self.client().delete('/questions/{}'.format(new_question.id))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_delete_question(self):
        res = self.client().delete('/question/300000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_422_get_questions_in_category(self):
        res = self.client().get('/categories/87798/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_get_questions_in_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])


    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': "ho"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_search_not_found(self):
        res = self.client().post('/questions/search', json={'searchTerm': ""})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_notfound_quiz_question(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_get_quiz_question(self):
        res = self.client().post('/quizzes', json={'quiz_category': {'type': 'Science', 'id': '1'},'previous_questions': []})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()