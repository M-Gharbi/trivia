import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

def get_paginated_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10

    questions = [question.format() for question in selection]
    formatted_questions = questions[start:end]

    return formatted_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')

    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def all_categories():
    try:
      categories = Category.query.all()
      formatted_categories = {}
      for category in categories:
        formatted_categories[category.id] = category.type
      return jsonify({
        'success': True,
        'categories': formatted_categories
      }), 200
    except Exception:
      abort(500)



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
  def questions_all():
    questions = Question.query.order_by(Question.id).all()
    all_questions = len(questions)
    categories = Category.query.order_by(Category.id).all()

    formatted_questions = get_paginated_questions(request, questions)

    if (len(formatted_questions) == 0):
      abort(404)

    formatted_categories = {}
    for category in categories:
      formatted_categories[category.id] = category.type

    return jsonify({
      'success': True,
      'total_questions': all_questions,
      'categories': formatted_categories,
      'questions': formatted_questions
    }), 200

  @app.route('/questions/<int:id>')
  def get_questions(id):

    question = Question.query.filter(Question.id==id).one_or_none()
    try:

      return jsonify({
        'success': True,
        'question': question.format()
      }), 200
    except Exception:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()
      return jsonify({
        'success': True,
        'message': "Question deleted"
      }), 200
    except Exception:
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
    question = body.get('question', '')
    answer = body.get('answer', '')
    difficulty = body.get('difficulty', '')
    category = body.get('category', '')

    if ((question == '') or (answer == '') or (difficulty == '') or (category == '')):
      abort(422)

    try:
      question = Question(
        question=question,
        answer=answer,
        difficulty=difficulty,
        category=category)
      question.insert()

      return jsonify({
        'success': True,
        'message': 'Question created!'
      }), 201

    except Exception:
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
  @app.route('/questions/search', methods=['POST'])
  def search():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term == '':
      abort(422)

    try:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      if len(questions) == 0:
        abort(404)

      paginated_questions = get_paginated_questions(request, questions)

      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': len(Question.query.all())
      }), 200

    except Exception:
      abort(404)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def questions_by_category(id):
    category = Category.query.filter_by(id=id).one_or_none()

    if (category is None):
      abort(422)

    #questions = Question.query.filter(Question.id==Category.id).all()

    questions = Question.query.filter_by(category=str(id)).all()
    paginated_questions = get_paginated_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(questions),
      'current_category': category.type
    })


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
  def play_quiz():
    body = request.get_json()
    quiz_category = body.get('quiz_category')
    previous_questions = body.get('previous_questions')

    if ((quiz_category is None) or (previous_questions is None)):
      abort(400)

    if (quiz_category['id'] == 0):
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=quiz_category['id']).all()

    def random_question():
        return questions[random.randint(0, len(questions)-1)]

    next_question = random_question()

    found = True

    while found:
      if next_question.id in previous_questions:
        next_question = random_question()
      else:
        found = False

    return jsonify({
      'success': True,
      'question': next_question.format(),
    }), 200


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  #(500)
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'An error has occured, please try again'
    }), 500

  #(400)
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request error'
    }), 400

  #(422)
  @app.errorhandler(422)
  def unprocesable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable entity'
    }), 422
  #(404)

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404



  return app

    