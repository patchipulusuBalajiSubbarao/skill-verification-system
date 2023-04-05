from flask import Flask,render_template,redirect,request,session
from web3 import Web3,HTTPProvider
import json
import os
from werkzeug.utils import secure_filename
import hashlib

def hash_file(filename):
    h=hashlib.sha1()
    with open(filename,'rb') as file:
        chunk=0
        while chunk!=b'':
            chunk=file.read(1024)
            h.update(chunk)
    return h.hexdigest()

def connect_with_register(acc): # is used to connect with register contract
    blockchain='HTTP://127.0.0.1:7545' # blockchain server
    web3=Web3(HTTPProvider(blockchain)) # connect with blockchain
    
    if acc==0:
        acc=web3.eth.accounts[0] # loading primary account for making transactions if acc is 0
    
    web3.eth.defaultAccount=acc # selecting the default account to be the account which is called from function call
    artifact_path='../build/contracts/register.json' # loading the register artifact
    
    with open(artifact_path) as f: # opening a file
        artifact_json=json.load(f) # string value is converted into json document
        contract_abi=artifact_json['abi'] # Application Binary Interface is used to connect with blockchain
        contract_address=artifact_json['networks']['5777']['address'] # contract address
    
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # connect with contract
    return (contract,web3) # return contract connection and web3 object

def connect_with_questions(acc): # is used to connect with questions contract
    blockchain='HTTP://127.0.0.1:7545' # blockchain server
    web3=Web3(HTTPProvider(blockchain)) # connect with blockchain
    
    if acc==0:
        acc=web3.eth.accounts[0] # loading primary account for making transactions if acc is 0
    
    web3.eth.defaultAccount=acc # selecting the default account to be the account which is called from function call
    artifact_path='../build/contracts/questions.json' # loading the questions artifact
    
    with open(artifact_path) as f: # opening a file
        artifact_json=json.load(f) # string value is converted into json document
        contract_abi=artifact_json['abi'] # Application Binary Interface is used to connect with blockchain
        contract_address=artifact_json['networks']['5777']['address'] # contract address
    
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # connect with contract
    return (contract,web3) # return contract connection and web3 object

def connect_with_exams(acc): # is used to connect with questions contract
    blockchain='HTTP://127.0.0.1:7545' # blockchain server
    web3=Web3(HTTPProvider(blockchain)) # connect with blockchain
    
    if acc==0:
        acc=web3.eth.accounts[0] # loading primary account for making transactions if acc is 0
    
    web3.eth.defaultAccount=acc # selecting the default account to be the account which is called from function call
    artifact_path='../build/contracts/exams.json' # loading the exams artifact
    
    with open(artifact_path) as f: # opening a file
        artifact_json=json.load(f) # string value is converted into json document
        contract_abi=artifact_json['abi'] # Application Binary Interface is used to connect with blockchain
        contract_address=artifact_json['networks']['5777']['address'] # contract address
    
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # connect with contract
    return (contract,web3) # return contract connection and web3 object

api=Flask(__name__) # crete an api to connect with the platform
api.secret_key='sacetc3'
api.config['uploads']='static/uploads'

@api.route('/') # rendering home page to user when they open the server address
def homePage():
    return render_template('index.html')

@api.route('/registerForm',methods=['post']) # inserting data into the blockchain using smart contract
def registerForm():
    walletaddr=request.form['walletaddr'] # collecting all the details from HTML Form
    name=request.form['name']
    email=request.form['email']
    mobile=request.form['mobile']
    password=request.form['password']
    role=request.form['role']
    print(walletaddr,name,email,mobile,password,role)

    try: 
        contract,web3=connect_with_register(0) # connecting with blockchain server using register contract
        tx_hash=contract.functions.registerUser(walletaddr,name,email,mobile,int(password),int(role)).transact() # inserting data into the block
        web3.eth.waitForTransactionReceipt(tx_hash) # wait until block appends to the chain
        return render_template('index.html',res='Registered Successfully') # display the result as success
    except:
        return render_template('index.html',err="Already Registered") # display the result as failure - already registered

@api.route('/loginForm',methods=['post']) # this api is used to login the user account
def loginForm():
    walletaddr=request.form['walletaddr'] # collecting details from html form
    password=request.form['password']

    try:
        contract,web3=connect_with_register(0) # connecting with blockchain using register contract
        state=contract.functions.loginUser(walletaddr,int(password)).call() # invoking loginuser function to check login
        if state==True:
            session['username']=walletaddr
            
            contract,web3=connect_with_register(0)
            _usernames,_names,_emails,_mobiles,_passwords,_roles=contract.functions.viewUsers().call()
            userIndex=_usernames.index(walletaddr)
            role=_roles[userIndex]
            session['role']=role
            if role==0:
                return redirect('/instructordashboard')
            elif role==1:
                return redirect('/evaluatordashboard')
            elif role==2:
                return redirect('/candidatedashboard')
            elif role==3:
                return redirect('/recruiterdashboard')
        else:
            return render_template('index.html',err1='invalid details') # return the failure message
    except:
        return render_template('index.html',err1='First Create Account') # return the failure message

@api.route('/instructordashboard')
def instructordashboard():
    return render_template('instructordashboard.html')

@api.route('/candidatedashboard')
def candidatesdashboard():
    contract,web3=connect_with_exams(0)
    _usernames1,_examowners1,_examids1,_marks1,_statuses1,_examhash1=contract.functions.viewExams().call()

    contract,web3=connect_with_register(0)
    _usernames2,_names2,_emails2,_mobiles2,_passwords2,_roles2=contract.functions.viewUsers().call()

    contract,web3=connect_with_questions(0)
    _usernames3,_questions3,_marks3,_examids3,_examnames3=contract.functions.viewExams().call()
    
    data=[]
    for i in range(len(_usernames1)):
        if(_usernames1[i]==session['username'] and _statuses1[i]==0):
            dummy=[]
            ownerIndex=_usernames2.index(_examowners1[i])
            dummy.append(_names2[ownerIndex])
            dummy.append(_examowners1[i])
            dummy.append(_examids1[i])
            examindex=_examids3.index(_examids1[i])
            dummy.append(_examnames3[examindex])
            data.append(dummy)
    return render_template('candidatesdashboard.html',dashboard_data=data,l=len(data))

@api.route('/exam/<id>')
def attemptExam(id):
    examId=int(id)
    session['examId']=examId
    contract,web3=connect_with_questions(0)
    _usernames1,_questions1,_marks1,_examids1,_examnames1=contract.functions.viewExams().call()
    print(_usernames1,_questions1,_marks1,_examids1,_examnames1)
    data=[]
    for i in range(len(_usernames1)):
        if(_examids1[i]==examId):
            for j in range(len(_questions1[i])):
                dummy=[]
                dummy.append(_questions1[i][j])
                dummy.append(_marks1[i][j])
                data.append(dummy)
    print(data)
    return render_template('attemptexam.html',dashboard_data=data,l=len(data))

@api.route('/uploadExamSheet',methods=['post'])
def uploadExamSheet():
    examId1=str(session['examId'])
    doc=request.files['chooseFile']
    if session['username'] not in os.listdir(api.config['uploads']):
        os.mkdir(os.path.join(api.config['uploads'],session['username']))
    if examId1 not in os.listdir(os.path.join(api.config['uploads'],session['username'])):
        os.chdir(api.config['uploads']+'/'+session['username'])
        os.mkdir(examId1)
        os.chdir('..')
    doc1=secure_filename(doc.filename)
    doc.save(api.config['uploads']+'/'+session['username']+'/'+examId1+'/'+doc1)
    hashcode=hash_file(api.config['uploads']+'/'+session['username']+'/'+examId1+'/'+doc1)
    contract,web3=connect_with_exams(0)
    tx_hash=contract.functions.attemptExam(session['username'],int(examId1),hashcode).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    
    contract,web3=connect_with_questions(0)
    _usernames1,_questions1,_marks1,_examids1,_examnames1=contract.functions.viewExams().call()
    print(_usernames1,_questions1,_marks1,_examids1,_examnames1)
    data=[]
    for i in range(len(_usernames1)):
        if(_examids1[i]==int(examId1)):
            for j in range(len(_questions1[i])):
                dummy=[]
                dummy.append(_questions1[i][j])
                dummy.append(_marks1[i][j])
                data.append(dummy)
    print(data)
    return redirect('/candidatedashboard')


@api.route('/addstudents')
def addstudents():
    contract,web3=connect_with_register(0)
    _usernames,_names,_emails,_mobiles,_passwords,_roles=contract.functions.viewUsers().call()
    data=[]
    for i in range(len(_usernames)):
        if (_roles[i]==2):
            dummy=[]
            dummy.append(_usernames[i])
            data.append(dummy)
    
    contract,web3=connect_with_questions(0)
    _usernames1,_questions,_marks,_examids,_examnames=contract.functions.viewExams().call()
    print(_usernames1,_questions,_marks,_examids,_examnames);
    data1=[]
    for i in range(len(_usernames1)):
        if(session['username']==_usernames1[i]):
            dummy=[]
            dummy.append(_examids[i])
            dummy.append(_examnames[i])            
            data1.append(dummy)
        
    return render_template('addstudents.html',dashboard_data=data,l=len(data),dashboard_data1=data1,l1=len(data1))

@api.route('/addStudentsForm',methods=['post'])
def addStudentsForm():
    userId=request.form['userId']
    examId=int(request.form['examId'])
    flag=0

    contract,web3=connect_with_exams(0)
    _usernames3,_examowners3,_examids3,_marks3,_statuses3,_examhash3=contract.functions.viewExams().call()
    for i in range(len(_usernames3)):
        if(_usernames3[i]==userId and _examids3[i]==examId):
            flag=1
    
    contract,web3=connect_with_register(0)
    _usernames,_names,_emails,_mobiles,_passwords,_roles=contract.functions.viewUsers().call()
    data=[]
    for i in range(len(_usernames)):
        if (_roles[i]==2):
            dummy=[]
            dummy.append(_usernames[i])
            data.append(dummy)
    
    contract,web3=connect_with_questions(0)
    _usernames1,_questions,_marks,_examids,_examnames=contract.functions.viewExams().call()
    print(_usernames1,_questions,_marks,_examids,_examnames);
    data1=[]
    for i in range(len(_usernames1)):
        if(session['username']==_usernames1[i]):
            dummy=[]
            dummy.append(_examids[i])
            data1.append(dummy)

    if(flag==0):
        contract,web3=connect_with_exams(0)
        tx_hash=contract.functions.allocateExam(userId,session['username'],examId).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('addstudents.html',dashboard_data=data,l=len(data),dashboard_data1=data1,l1=len(data1),res='Exam Added to Student')
    else:
        return render_template('addstudents.html',dashboard_data=data,l=len(data),dashboard_data1=data1,l1=len(data1),err='This exam is already added')

@api.route('/createExam',methods=['post'])
def createExam():
    keys=[]
    questions=[]
    marks=[]
    
    for i in request.form:
        keys.append(i)
    print(keys)
    examname=request.form['examname']
    keys=keys[1:]
    for i in range(len(keys)):
        if i%2==0:
            questions.append(request.form[keys[i]])
        else:
            marks.append(int(request.form[keys[i]]))
    print(examname,questions,marks)

    contract,web3=connect_with_questions(0)
    tx_hash=contract.functions.addExam(session['username'],examname,questions,marks).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)

    # print(request.form)
    return render_template('instructordashboard.html',res="Exam Added to Blockchain")

@api.route('/evaluatordashboard')
def evaluatordashboard():
    contract,web3=connect_with_exams(0)
    _usernames,_examowners,_examids,_marks,_statuses,_examhash=contract.functions.viewExams().call()
    data=[]
    for i in range(len(_usernames)):
        if(_statuses[i]==1):
            dummy=[]
            dummy.append(_usernames[i])
            # dummy.append(_examowners[i])
            dummy.append(_examids[i])
            dummy.append(_examhash[i])
            data.append(dummy)
    return render_template('evaluatordashboard.html',dashboard_data=data,len=len(data))

@api.route('/answer/<id1>/<id2>')
def answerPage(id1,id2):
    session['sheetid1']=id1
    session['sheetid2']=id2
    print(id1,id2)
    k=os.listdir(api.config['uploads']+'/'+session['sheetid1']+'/'+session['sheetid2'])
    print(k)
    return render_template('allocatemarks.html',anssheet=api.config['uploads']+'/'+session['sheetid1']+'/'+session['sheetid2']+'/'+k[0])

@api.route('/allocateMarks',methods=['post'])
def allocateMarks():
    marks=int(request.form['marks'])
    contract,web3=connect_with_exams(0)
    tx_hash=contract.functions.allocateMarks(session['sheetid1'],int(session['sheetid2']),marks).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/evaluatorresults')

@api.route('/evaluatorresults')
def evaluatorresults():
    contract,web3=connect_with_exams(0)
    _usernames,_examowners,_examids,_marks,_statuses,_examhash=contract.functions.viewExams().call()
    data=[]
    for i in range(len(_usernames)):
        if(_statuses[i]==2):
            dummy=[]
            dummy.append(_usernames[i])
            dummy.append(_examids[i])
            dummy.append(_marks[i])
            data.append(dummy)
    return render_template('evaluatorresults.html',dashboard_data=data,len=len(data))

@api.route('/myresults')
def myresults():
    contract,web3=connect_with_exams(0)
    _usernames,_examowners,_examids,_marks,_statuses,_examhash=contract.functions.viewExams().call()
    data=[]
    for i in range(len(_usernames)):
        if(_statuses[i]==2 and _usernames[i]==session['username']):
            dummy=[]
            dummy.append(_examowners[i])
            dummy.append(_examids[i])
            dummy.append(_marks[i])
            data.append(dummy)
    return render_template('myresults.html',dashboard_data=data,len=len(data))

@api.route('/recruiterdashboard')
def recruiterdashboard():
    return render_template('recruiterdashboard.html')

@api.route('/verifyskill',methods=['post'])
def verifyskill():
    studentwallet=request.form['studentwallet']
    examid=int(request.form['examid'])
    contract,web3=connect_with_questions(0)
    _usernames1,_questions1,_marks1,_examids1,_examnames1=contract.functions.viewExams().call()

    contract,web3=connect_with_exams(0)
    _usernames,_examowners,_examids,_marks,_statuses,_examhash=contract.functions.viewExams().call()
    for i in range(len(_usernames)):
        if(_examids[i]==examid and _usernames[i]==studentwallet):
            examindex=_examids1.index(examid)
            _marks11=_marks1[examindex]
            totalmarks=0
            for j in _marks11:
                totalmarks+=j
            if (_marks[i]/totalmarks)*100>=60:
                return render_template('recruiterdashboard.html',res='The student has cleared the exam')
            else:
                return render_template('recruiterdashboard.html',err='The student has failed the exam')
            
    return render_template('recruiterdashboard.html',err='The student has not attempted the exam')

@api.route('/logout')
def logout():
    session['username']=None
    session['role']=None
    return redirect('/')

if (__name__=="__main__"): # running the web server - front end server
    api.run(port=5001,debug=True)