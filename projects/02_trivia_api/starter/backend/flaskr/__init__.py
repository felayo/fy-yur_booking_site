import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()

            if len(categories) == 0:
                abort(404)

            # formatted_categories = {category.format() for category in categories}

            formatted_categories = {
                category.id: category.type for category in categories}

            return jsonify({
                "success": True,
                "categories": formatted_categories,
                "total_categories": len(formatted_categories)
            })

        except:
            abort(422)
    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions')
    def get_questions():

        questions = Question.query.order_by(Question.id).all()

        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.type).all()

        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(questions),
            "categories": formatted_categories,
            'current_category': None
        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            question.delete()

            questions = Question.query.order_by(Question.id).all()

            current_questions = paginate_questions(request, questions)

            return jsonify({
                "success": True,
                "deleted": question_id,
                "questions": current_questions,
                "remaining_questions": len(questions),
            })

        except:
            abort(422)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if body is None:
            abort(422)

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)

            question.insert()

            # questions = Question.query.order_by(Question.id).all()

            # current_questions = paginate_questions(request, questions)

            created_question = question.format()

            return jsonify({
                'success': True,
                'created': question.id,
                'question': created_question
            })

        except:
            abort(422)

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/search', methods=['POST'])
    def search_terms():

        body = request.get_json()

        search_term = body.get('searchTerm', None)

        try:
            if search_term:
                results = Question.query.filter(
                    Question.question.ilike("%{}%".format(search_term))).all()

                formatted_results = [result.format() for result in results]

                return jsonify({
                    "success": True,
                    "questions": formatted_results,
                    "total_questions": len(formatted_results)
                })

            abort(404)

        except:
            abort(405)

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_by_category(category_id):
        try:
            questions_by_category = Question.query.filter(
                Question.category == category_id).all()

            f_questions_by_category = [question.format()
                                       for question in questions_by_category]
            if len(f_questions_by_category) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "questions": f_questions_by_category,
                "current_category": category_id,
                "total_questions": len(f_questions_by_category)
            })

        except:
            abort(404)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_and_play_quizzes():

        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')
            categoryId = quiz_category.get('id')


            if categoryId == 0:
                questions = Question.query.order_by(func.random())

            else:
                questions = Question.query.filter(
                    Question.category == categoryId).order_by(func.random())

            if len(questions.all()) == 0:
                abort(404)
            else:
                question = questions.filter(
                    Question.id.notin_(previous_questions)).first()

            if question is None:
                return jsonify({
                    'success': True,
                    'question': None
                })

            return jsonify({
                'success': True,
                'question': question.format()
            })

        except:
            abort(422)

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                    "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(405)
    def unallowed_method(error):
        return (
            jsonify({"success": False, "error": 405,
                    "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400,
                    "message": "Bad Request"}),
            400,
        )

    @app.errorhandler(500)
    def internal_serverError(error):
        return (
            jsonify({"success": False, "error": 500,
                    "message": "Internal Server Error"}),
            500,
        )

    return app
