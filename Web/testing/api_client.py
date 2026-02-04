import requests
API = "http://localhost:8000"

def login(e,p):
    return requests.post(API+"/login",
        json={"email":e,"password":p}).json()

def reg1(e,p):
    return requests.post(API+"/register/step1",
        json={"email":e,"password":p}).json()

def reg2(e,c):
    return requests.post(API+"/register/step2",
        json={"email":e,"code":c}).json()

def reg3(e,h,w):
    return requests.post(API+"/register/step3",
        json={"email":e,"height":h,"weight":w}).json()
