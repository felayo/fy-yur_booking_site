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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "ayorinde", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

            self.new_question = {
                'question': 'Who is the former Governor of ogun state?',
                'answer': 'Ibikunle Amosun',
                'difficulty': 4,
                'category': 4
            }
            
            self.new_quiz = {
                'previous_questions': [],
                'quiz_category': {'type': 'History', 'id': '4'}
            }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # success - Get Categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))
        
    #Error -  Get categories  
    def test_404_for_non_existing_categories(self):
        res = self.client().get("/categories/500")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    # success - Get Paginated Questions    
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    # Error - Get Paginated Questions
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=500")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
     
    # Success - Delete questions   
    def test_delete_question(self):
        res = self.client().delete("/questions/9")
        data = json.loads(res.data)
        
        question = Question.query.filter(
            Question.id == 9).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 9)
        self.assertTrue(data["remaining_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)
    
    # Error - Unprocessable Deletion   
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/500")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    # Success - Create new question  
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["question"]))
        
    # Error -   Question creation not allowed
    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/90", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
        
    # Success - search terms
    def test_search_question(self):
        res = self.client().post("/search", json={'searchTerm': 'soccer'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
    
    #Error - Search term method not allowed   
    def test_405_if_search_term_method_not_allowed(self):
        res = self.client().post("/search", json={'search_term': 'soccer'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
    
    # Success - Get Questions based on category    
    def test_get_questions_based_on_category(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(len(data["questions"]))
        
    #Error -  Missing categories
    def test_404_if_missing_category(self):
        res = self.client().get("/categories/90/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    #success - play quizzes
    def test_play_quiz(self):
        res = self.client().post("/quizzes", json=self.new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["question"]))
    
    # Error - Failed Quiz    
    def test_422_if_play_quiz_unprocessed(self):
        res = self.client().post("/quizzes", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
