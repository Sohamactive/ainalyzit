import datetime
from analysis.services import get_db_handle # We can reuse the DB connection function

def log_meal_to_db(user_id, food_name, nutritional_score):
    """
    Saves a user's meal choice to the 'daily_logs' collection in MongoDB.
    """
    db, client = get_db_handle()
    logs_collection = db['daily_logs']

    log_document = {
        "userId": user_id,
        "logDate": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        "foodName": food_name,
        "nutritionalScore": nutritional_score
    }
    
    result = logs_collection.insert_one(log_document)
    client.close()
    return result.inserted_id

from analysis.services import get_db_handle

# ... (keep your existing log_meal_to_db function) ...

def get_user_stats(user_id):
    """
    Calculates the daily score and streak for a given user.
    """
    db, client = get_db_handle()
    logs_collection = db['daily_logs']
    
    today_str = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    # --- 1. Calculate Today's Average Score ---
    pipeline = [
        {'$match': {'userId': user_id, 'logDate': today_str}},
        {'$group': {'_id': '$userId', 'averageScore': {'$avg': '$nutritionalScore'}}}
    ]
    daily_avg_result = list(logs_collection.aggregate(pipeline))
    
    daily_score = 0
    if daily_avg_result:
        daily_score = round(daily_avg_result[0]['averageScore'])

    # --- 2. Calculate Streak ---
    streak = 0
    current_date = datetime.datetime.now(datetime.timezone.utc).date()
    
    # Find all unique dates the user has logged a meal on, in descending order
    distinct_dates_cursor = logs_collection.distinct(
        'logDate',
        {'userId': user_id}
    )
    logged_dates = sorted([datetime.date.fromisoformat(d) for d in distinct_dates_cursor], reverse=True)

    for i, log_date in enumerate(logged_dates):
        # Check if the log date is today or a consecutive day before today
        if log_date == (current_date - datetime.timedelta(days=i)):
            streak += 1
        else:
            # The streak is broken
            break
            
    client.close()

    return {
        'daily_score': daily_score,
        'streak': streak
    }