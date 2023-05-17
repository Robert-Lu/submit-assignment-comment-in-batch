import csv, json, requests, sys, time
from collections import defaultdict

# read CSV
grades = defaultdict(dict)
fields = []
with open('S23 CS174A Exam Grading - Raw.csv') as file:
    csv_reader = csv.reader(file, delimiter=',')
    line_count = 0
    # read first row as fields
    fields = next(csv_reader)
    # second row: possible points
    possible_points = next(csv_reader)
    possible_points = {fields[i]: possible_points[i] for i in range(len(fields)) if possible_points[i].isdecimal()}
    # following rows: grades
    for row in csv_reader:
        if row[0] != '':
            grades[row[0]] = dict(zip(fields, row))

# Change the index to be ID
grades = {grades[key]['ID']: grades[key] for key in grades}

# Extract the comments
comments = dict()
for key in grades:
    comment = f"Total: {grades[key]['Total']}/{possible_points['Total']}\n"
    for field in fields:
        if field in possible_points and field != 'Total':
            comment += f" - {field}: {grades[key][field]}/{possible_points[field]}\n"
    comments[key] = comment

# Submit the comments:

# Read API key from file
with open('API_KEY.txt') as file:
    API_KEY = file.read().strip()

# Set the headers
headers = {
    "Authorization": "Bearer " + API_KEY,
}

# Extract the IDs from the assignment URL, e.g. https://bruinlearn.ucla.edu/courses/160791/assignments/1421413
institute_id = "14809"  # for UCLA BruinLearn, same for the first field of your API key
course_id = institute_id + "~" + "160791"
assignment_id = institute_id + "~" + "1421413"

for user_id in comments:
    submission_id = institute_id + "~" + user_id
    comment_text = comments[user_id]

    # Set the API endpoint URL
    base_url = "https://canvas.instructure.com/api/v1"
    url = f"{base_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{submission_id}"

    # Set the request payload
    data = {
        "comment": {
            "text_comment": comment_text
        }
    }

    try:
        # Send the request
        response = requests.put(url, headers=headers, json=data)

        # if sucessful, print the response
        if response.status_code < 300:
            print("Request successful.")
            print(f"ID:{user_id}, Comment:{comment_text}")
        else:
            print("Request failed.", response.status_code)
            print("Response:", response.json())
    except Exception as e:
        print(f"Error: {e} for ID:{user_id}, Comment:{comment_text}")
