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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'answer': 'Anansi Boys',
            'question': 'Name Neil Gaiman most popular book',
            'difficulty': 4,
            'category' : 4

        }

        self.searchTerm = {
           
              'searchTerm': 'Neil Gaiman'

        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    def test_list_categories(self):
        """ Test get list of categories """
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])

    def test_list_questions(self):
        """ Test get list of questions paginated """
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        
    def test_questions_by_category_id(self):
        """ Test get list of questions by id  """
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])

    def test_add_question(self):
        """ Add questions by id  """
        res = self.client().post('/questions',json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['new_question_id'])
        
    def test_search_question(self):
        """ search questions by search term  """
        res = self.client().post('/questions',json=self.searchTerm)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])


    def test_questions_by_non_existing_id(self):
        """ Delete questions by non_existing id  """
        res = self.client().get('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)


    def test_play_quiz(self):
        """ Play quiz by choosing category  """
        res = self.client().post('/quizzes',json= {'quiz_category': {'id': '4'},'previous_questions' : [5,] } )
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_play_all_quiz(self):
        """ Play quiz by choosing ALL category  """
        res = self.client().post('/quizzes',json= {'quiz_category': {'id': 0 },'previous_questions' : [5,] } )
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()