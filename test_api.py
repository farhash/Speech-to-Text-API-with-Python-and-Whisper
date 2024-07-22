import requests


url = 'https://stt.lexemeai.com/stt/upload/'

file_path = '/home/farhat/Desktop/nevisa_api/Test4.wav'

with open(file_path, 'rb') as file:
    files = {'audio': file}
    try:
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            response_data = response.json()
            print("Response JSON:", response_data)
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            print("Response text:", response)
    except requests.exceptions.RequestException as e:
        print("error communicating with api: ", e)


url2 = 'https://stt.lexemeai.com/stt/result/'

result_key = response_data.get("stt_result_key")
url2 += result_key + "/"

try:
    response2 = requests.post(url2)
    response_data2 = response2.json()
    while response_data2.get("stt_result_status") == "pending":
        response2 = requests.post(url2)
        response_data2 = response2.json()
   
    if response_data2.get("stt_result_status") == "success":
        print(response_data2.get("stt_result_script"))
    else:
        print(f"The convert is failed. Status code: {response2.status_code}")
        print("Response text:", response2)
except requests.exceptions.RequestException as e:
    print("error communicating with api: ", e)
