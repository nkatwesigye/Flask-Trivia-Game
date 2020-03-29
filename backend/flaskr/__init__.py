import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r'/*': {'origins': '*'}})
  
  

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  
  # setup pagination feature
  def setup_pagination():
    global start 
    global end
    page = request.args.get('page',1,type=int)
    start = ( page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return start,end

           
  # list all categories
  @app.route('/categories')
  def get_catageries():
      categories = {}
      all_categories = Category.query.all()
      if len(all_categories) == 0 :
            abort(404)
      for category in all_categories: 
       categories[category.id] = category.type
      return jsonify( {
          'success' : True,
          'categories' : categories
        })

  
  # List all questions
  @app.route('/questions')
  def list_questions():
       formated_questions = []
       setup_pagination()
       categories = {}
       all_questions = Question.query.all()
       all_categories = Category.query.all()
       if len(all_questions) is None :
            abort(422)

       for question in all_questions:
         formated_questions.append(question.format()) 

       for category in all_categories:
           categories[category.id] = category.type
       return jsonify( {
          'questions' : formated_questions[start:end],
          'total_questions' : len(formated_questions),
          'categories': categories,
          'success' : True 
        })

    
  # Get question based on question id 
  @app.route('/questions/<int:question_id>',methods=['GET','DELETE'])
  def delete_question(question_id):
      questions_to_delete = Question.query.filter_by(id=question_id).first()
      if questions_to_delete == None:
        abort(422)
      questions_to_delete.delete()
      return jsonify({
          'question_id' : question_id,
          'success' : True
      })

  # list questions and search
  @app.route('/questions',methods=['GET','POST'])
  def add_question_add_search():
      search_results = []
      setup_pagination()
      newQuestion_params = request.json
      if newQuestion_params.get('searchTerm'):
         search_term = newQuestion_params['searchTerm']
         search_questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
         if search_questions is None:
            abort(404)
         for question in search_questions: 
             search_results.append(question.format())  
         return jsonify({
          'success' : True,
          'questions' : search_results[start:end],
          'total_questions': len(search_results)

         })
      else:
        answer = newQuestion_params['answer']
        question = newQuestion_params['question']
        difficulty = newQuestion_params['difficulty']
        category = newQuestion_params['category']
        newQuestion = Question(question,answer,difficulty,category)
        newQuestion.insert()
        new_question_id = Question.query.filter_by(question = newQuestion.question).first()
        return jsonify({
          'new_question_id' : new_question_id.id,
          'success': True
      })
 
  # filter questions based on category
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_for_category(category_id):
      setup_pagination()
      formated_questions = []
      category_questions = Question.query.filter_by(category=category_id).all()
      if category_questions is None:
        abort(404)
      for questions in category_questions:
          formated_questions.append(questions.format())
      return jsonify({
        'questions' : formated_questions[start:end],
        'success' : True
      })

  # Play Route with radom questions for all or specific category
  @app.route('/quizzes',methods=['POST'])
  def play_quizze():
      final_question = []
      play_questions = request.json
      previous_questions = play_questions['previous_questions']
      category = play_questions['quiz_category']
      if previous_questions is not None  and category['id'] != 0:
         to_be_played =  Question.query.filter(~Question.id.in_(previous_questions),Category.id == category['id'])
         for question in to_be_played:
             final_question.append(question.format())
         random_question = random.choice(final_question)
         return jsonify ({
             'success' : True,
              'question': random_question
         })
      elif category['id'] == 0 :
           to_be_played =  Question.query.filter(~Question.id.in_(previous_questions))
           for question in to_be_played:
             final_question.append(question.format())
           random_question = random.choice(final_question)
           return jsonify ({
             'success' : True,
              'question': random_question
         })
      else:    
        abort(404)



  # Error Handler
  @app.errorhandler(400)
  def bad_request(error):
        """
        :error handler for error 400 
        :param error: Bad request
        :return: error: HTTP status code, message: Error description
        """
        return jsonify({
            'success': False,
            'error': 400,
            'message': ' Bad request ' + str(error)
        }), 400

  @app.errorhandler(500)
  def bad_request(error):
        """
        :error handler for error 500 
        :param error: Internal Server Error
        :return: error: HTTP status code, message: Error description
        """
        return jsonify({
            'success': False,
            'error': 500,
            'message': ' Internal Server Error ' + str(error)
        }), 500

  @app.errorhandler(404)
  def not_found(error):
        """
        :error handler for error 404 
        :param error: Page not found
        :return: error: HTTP status code, message: Error description
        """
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page not found ' + str(error)
        }), 404

  @app.errorhandler(422)
  def not_processable(error):
        """
        Generic error handler for unprocessable failure 
        """
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Request can not be processed ' + str(error)
        }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
        """
        Generic error handler for method_not_allowed failure 
        """
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed ' + str(error)
        }), 405

  return app

    
