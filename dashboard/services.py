# ainalyzit/dashboard/services.py

import datetime
from analysis.services import get_db_handle
from bson.son import SON
import pymongo

def get_user_stats(user_id):
    """
    Calculates a comprehensive set of statistics for a given user's dashboard.
    """
    db, client = get_db_handle()
    logs_collection = db['daily_logs']
    
    # --- 1. Basic Stats ---
    total_meals = logs_collection.count_documents({'userId': user_id})
    
    # --- 2. Average Score ---
    avg_pipeline = [
        {'$match': {'userId': user_id}},
        {'$group': {'_id': '$userId', 'averageScore': {'$avg': '$nutritionalScore'}}}
    ]
    avg_result = list(logs_collection.aggregate(avg_pipeline))
    average_score = round(avg_result[0]['averageScore']) if avg_result else 0
    
    # --- 3. Best Meal ---
    best_meal_cursor = logs_collection.find({'userId': user_id}).sort('nutritionalScore', pymongo.DESCENDING).limit(1)
    best_meal = next(best_meal_cursor, None)
    
    # --- 4. Recent Meals ---
    recent_meal_logs = list(logs_collection.find({'userId': user_id}).sort('timestamp', pymongo.DESCENDING).limit(5))
    
    # --- 5. Health Score Trend (Last 30 Days) ---
    thirty_days_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
    trend_pipeline = [
        {'$match': {
            'userId': user_id,
            'timestamp': {'$gte': thirty_days_ago}
        }},
        {'$project': {
            'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
            'score': '$nutritionalScore'
        }},
        {'$group': {
            '_id': '$date',
            'avgScore': {'$avg': '$score'}
        }},
        {'$sort': SON([('_id', 1)])}
    ]
    trend_data = list(logs_collection.aggregate(trend_pipeline))
    
    chart_labels = [entry['_id'] for entry in trend_data]
    chart_data = [round(entry['avgScore'], 1) for entry in trend_data]
    
    client.close()

    return {
        'average_score': average_score,
        'total_meals': total_meals,
        'best_meal': best_meal,
        'recent_meal_logs': recent_meal_logs,
        'chart_labels': chart_labels,
        'chart_data': chart_data
    }

def log_meal_to_db(user_id, food_name, score):
    """
    Manually logs a meal to the daily_logs collection.
    This is used for the manual "Log Meal" feature.
    """
    db, client = get_db_handle()
    logs_collection = db['daily_logs']
    
    log_entry = {
        "userId": user_id,
        "foodName": food_name,
        "nutritionalScore": score,
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
    }
    
    result = logs_collection.insert_one(log_entry)
    client.close()
    return result.inserted_id