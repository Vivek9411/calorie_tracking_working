import requests
import datetime
import pytz
API_ID = "127b9e9d"
API_KEY = "d3f14705514a09f28cf0669fc0315c99"
url = "https://trackapi.nutritionix.com/v2/natural/exercise"
headers = {
        "x-app-id": API_ID,
        "x-app-key": API_KEY
    }
def findx(user_input, gender, weight, height, age, headers=headers):
    tz_ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.datetime.now(tz_ist)
    date, time = str(now_ist.strftime("%Y-%m-%d %H:%M:%S")).split(" ")
    query = {
     "query": user_input,
     "gender": gender,
     "weight_kg": weight,
     "height_cm": height,
     "age": age
    }
    response = requests.post(url=url, json=query, headers=headers)
    print(response.raise_for_status())
    print(response.json())
    data = response.json()['exercises']
    print(data)
    new=[]
    for each_exercise in data:
        exercise = {
            'exercise': each_exercise['user_input'],
            'duration': each_exercise['duration_min'],
            'calories': each_exercise['nf_calories'],
            'date': date,
            'time': time,
            'description': user_input,
        }
        new.append(exercise)
    # print(new)
    return  new


api_food = '3db00a91'
api_key_food = '8dc67612535c89a55858b8ab37364320'

url_food  ='https://trackapi.nutritionix.com/v2/natural/nutrients'
headers_food = {
    "x-app-id": api_food,
    "x-app-key": api_key_food
}
def find_food(user_input, headers_food=headers_food):
    tz_ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.datetime.now(tz_ist)
    date, time = str(now_ist.strftime("%Y-%m-%d %H:%M:%S")).split(" ")
    query = {
        "query": user_input,
    }
    response = requests.post(url=url_food, json=query, headers=headers_food)
    print(response.text)

    data = response.json()['foods']
    food = []
    for each_food in data:
        foods ={
            'food': each_food['food_name'],
            'calories': each_food['nf_calories'],
            'date': date,
            'time': time,
            'serving_unit': each_food['serving_unit'],
            'amount': each_food['serving_weight_grams'],
            'serving_quantity': each_food['serving_qty'],
            'description': user_input
        }
        # print(each_food)
        food.append(foods)
    return food



# print(find_food('eat 2 apples', headers_food=headers_food))
