from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask import Response, json, request, jsonify, Flask


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request,selection):
    page=request.args.get('page',1,type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE

    questions =[question.format() for question in selection]
    current_questions=questions[start:end]
    
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*":{"origins":"*"}})

    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def available_categories():
        categories=Category.query.order_by(Category.id).all()
        current_category=paginate(request,categories)

        if len(current_category)==0:
            abort(400)

        return jsonify({
            'success':True,
            'categories': current_category
        })
        

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        questions=Question.query.all()
        total_questions = len(questions)
        current_question=paginate(request,questions)
        # all_categories = Category.query.all()

        

        # current_categories_id = []
        # current_categories = []
        # for question in questions: 
        #     if question.category not in current_categories_id:
        #         current_categories_id.append(question.category)
        #         current_categories.append(Category.query.filter_by(id=question.category).first())
        
        if len(current_question)==0:
            abort(400)

        return jsonify({
            'success':True,
            'current_questions': current_question,
            'total_questions':total_questions, 
            # 'categories': all_categories,
            # 'current_categories' : current_categories
            })
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def delete(question_id):
        try:
            question=Question.query.filter(Question.id==question_id).one_or_none()

            if question is None:
                abort(400)
            question.delete()
            selection=Question.query.order_by(Question.id).all()
            current_question = paginate(request,selection)

            return jsonify({
                'success':True,
                'deleted':question_id,
                'questions':current_question,
                'total_questions':len(Question.query.all())
            })
        except:
            abort(432)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions',methods=['POST'])
    def create_question():
      
        body = request.form
        db = SQLAlchemy()
        new_question=body.get('question',None)
        new_answer=body.get('answer',None)
        new_category=body.get('category',None)
        new_difficulty=body.get('difficulty',None)
        try:
            new_question_=Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=int(new_difficulty)
            )
            db.session.add(new_question_)
            selection=Question.query.order_by(Question.id).all()
            current_questions=paginate(request,selection)
            return jsonify({
                'success':True,
                'new_question':new_question_.id,
                'questions':current_questions,
                'total_questions':len(Question.query.all())
            })
        
        except:
            abort(422)
        

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search(search_term):
        body=request.get_json(search_term)

        search_result=Question.query.filter(Question.question.contains('search_term').all())
        if search_result in Question.question:
            return jsonify({
                'success':True
                
            })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<string:category_id>/questions')
    def get_question_by_category(category_id):
        selection = (Question.query.filter(Question.category == str(category_id)).order_by(Question.id).all())
        
        return jsonify({
        'success': True,
        'total_questions': len(selection),
        'current_category' : category_id
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/play',methods=['POST'])
    def play_quiz():
        body = request.get_json()
    
    
        
        return jsonify({
            'success': True
        })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "resource not found"}),404,

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({"success": False, "error": 422, "message": "unprocessable"}),422,

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({"success": False, "error": 405, "message": "method not allowed"}),405
        
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"success": False, "error": 500,"message": "internal server error"}), 500
    return app

