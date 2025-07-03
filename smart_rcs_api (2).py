import requests

def get_investimento_rcs():
    url = "https://developer.smartrcs.com.br/api/"  
    headers = {
        "X-Api-Key": "Bearer 2B82DAAF-DA5D-438C-A986-5B4C607F6127"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["investimento"]  

if __name__ == "__main__":
    print(get_investimento_rcs())  