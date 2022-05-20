from flask import Flask, render_template, redirect, url_for, request, make_response, session
import requests

app = Flask(__name__)
app.secret_key = "abc"

# base_url = 'https://thinkfotechapp.herokuapp.com'
base_url = 'http://127.0.0.1:8000'

@app.route('/')
def homePage():
	if 'client' in session:
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()

		response=requests.get(base_url + '/itemList/lightSound')
		lightSoundList = response.json()
		response=requests.get(base_url + '/itemList/food')
		foodList = response.json()
		response=requests.get(base_url + '/itemList/others')
		othersList = response.json()
  
		return render_template('client_home.html', clientDetails=clientDetails, lightSoundList=lightSoundList, foodList=foodList, othersList=othersList)
	else:
		return render_template('login.html', session='client')

@app.route('/admin')
def adminHomePage():
	if 'admin' in session:
		response = requests.get(base_url + '/eventList/new_request')
		new_request_list = response.json()
		response = requests.get(base_url + '/eventList/on_survey')
		on_survey_list = response.json()
		response = requests.get(base_url + '/eventList/for_verification')
		for_verification_list = response.json()
		response = requests.get(base_url + '/eventList/forwarded')
		forwarded_list = response.json()
		return render_template('admin_home.html', new_request_list=new_request_list, on_survey_list=on_survey_list, for_verification_list=for_verification_list, forwarded_list=forwarded_list)
	else:
		return render_template('login.html', session='admin')

@app.route('/manager')
def managerHomePage():
	if 'manager' in session:
		response = requests.get(base_url + '/eventList/new_request')
		new_request_list = response.json()
		response = requests.get(base_url + '/eventList/on_survey')
		on_survey_list = response.json()
		response = requests.get(base_url + '/eventList/for_verification')
		for_verification_list = response.json()
		response = requests.get(base_url + '/eventList/forwarded')
		forwarded_list = response.json()
		return render_template('manager_home.html', session='manager', new_request_list=new_request_list, on_survey_list=on_survey_list, for_verification_list=for_verification_list, forwarded_list=forwarded_list)
	else:
		return render_template('login.html', session='manager')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		clientImg = request.files['photo']
		if clientImg:
			files = {'photo' : (clientImg.filename, clientImg, clientImg.content_type)}	
			response = requests.post(base_url + '/client', data=userInput, files=files)
		else:
			response=requests.post(base_url + '/client', json=userInput)
		return redirect(url_for('homePage'))

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		if userInput['session'] == 'client':
			response = requests.post(base_url + '/clientLogin', json=userInput)
			if response.json() != '':
				clientID = response.json()
				session['client'] = clientID
			return redirect(url_for('homePage'))
		elif userInput['session'] == 'admin':
			response = requests.post(base_url + '/adminLogin', json=userInput)
			if response.json() == 'admin':
				session['admin'] = response.json()
			return redirect(url_for('adminHomePage'))
		elif userInput['session'] == 'manager':
			response = requests.post(base_url + '/managerLogin', json=userInput)
			if response.json() == 'manager':
				session['manager'] = response.json()
			return redirect(url_for('managerHomePage'))

@app.route('/logout')
def logout():
	if 'client' in session:
		session.pop('client', None)
	return redirect(url_for('homePage'))

@app.route('/adminLogout')
def adminLogout():
	if 'admin' in session:
		session.pop('admin', None)
	return redirect(url_for('adminHomePage'))

@app.route('/managerLogout')
def managerLogout():
	if 'manager' in session:
		session.pop('manager', None)
	return redirect(url_for('managerHomePage'))

@app.route('/adminClientList')
def adminClientList():
	if 'admin' in session:
		response=requests.get(base_url + '/client')
		clientList = response.json()
		return render_template('admin_manager_client_list.html', clientList=clientList, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerClientList')
def managerClientList():
	if 'manager' in session:
		response=requests.get(base_url + '/client')
		clientList = response.json()
		return render_template('admin_manager_client_list.html', clientList=clientList, session='manager')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/adminClientProfile/<clientID>')
def adminClientProfile(clientID):
	if 'admin' in session:
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		response = requests.get(base_url + '/clientEventList/' + clientID)
		eventList = response.json()
		return render_template('admin_client_profile.html', clientID=clientID, clientDetails=clientDetails, eventList=eventList)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerClientProfile/<clientID>')
def managerClientProfile(clientID):
	if 'manager' in session:
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		response = requests.get(base_url + '/clientEventList/' + clientID)
		eventList = response.json()
		return render_template('manager_client_profile.html', clientID=clientID, clientDetails=clientDetails, eventList=eventList)
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/adminChat/<recID>')
def adminChatPage(recID):
	if 'admin' in session:
		clientID = 'ADMIN'
		response = requests.get(base_url + '/client/' + recID)
		recDetails = response.json()
		response = requests.post(base_url + '/message', json={'sender' : clientID, 'receiver' : recID, 'action' : 'get'})
		msgList = response.json()
		return render_template('client_chat.html', recID=recID.upper(), recDetails=recDetails, msgList=msgList, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/clientChat/<recID>')
def clientChatPage(recID):
	if 'client' in session:
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		response = requests.post(base_url + '/message', json={'sender' : clientID, 'receiver' : recID, 'action' : 'get'})
		msgList = response.json()
		return render_template('client_chat.html', clientDetails=clientDetails, recID=recID.upper(), recDetails={}, msgList=msgList, session='client')

@app.route('/adminSendMessage', methods=['POST', 'GET'])
def adminSendMessage():
	if 'admin' in session:
		userID = 'ADMIN'
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['sender'] = userID
			requests.post(base_url + '/message', json=userInput)
			return redirect(url_for('adminChatPage', recID=userInput['receiver']))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/clientSendMessage', methods=['POST', 'GET'])
def clientSendMessage():
	if 'client' in session:
		clientID = session['client']
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['sender'] = clientID
			requests.post(base_url + '/message', json=userInput)
			return redirect(url_for('clientChatPage', recID=userInput['receiver']))
	else:
		return redirect(url_for('homePage'))

@app.route('/adminInbox')
def adminInbox():
	if 'admin' in session:
		clientID = 'ADMIN'
		response = requests.post(base_url + '/message/' + clientID)
		msgList = response.json()
		return render_template('inbox.html', msgList=msgList, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/profile')
def profile():
	if 'client' in session:
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		return render_template('client_profile.html', clientDetails=clientDetails)
	else:
		return redirect(url_for('homePage'))

@app.route('/editProfile')
def editProfile():
	if 'client' in session:
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		return render_template('client_edit_profile.html', clientDetails=clientDetails)
	else:
		return redirect(url_for('homePage'))

@app.route('/updateProfile', methods=['POST','GET'])
def updateProfile():
	if 'client' in session:
		if request.method == 'POST':
			clientID = session['client']
			userInput = request.form.to_dict()
			clientImg = request.files['photo']
			if clientImg:
				files = {'photo' : (clientImg.filename, clientImg, clientImg.content_type)}	
				response = requests.put(base_url + '/client/' + clientID, files=files)
			requests.put(base_url + '/client/' + clientID, json=userInput)
			return redirect(url_for('profile'))
	else:
		return redirect(url_for('homePage'))

@app.route('/addItems')
def addItems():
	if 'manager' in session:
		return render_template('manager_add_items.html')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/registerItems', methods=['POST', 'GET'])
def registerItems():
	if 'manager' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			itemImg = request.files['photo']
			if itemImg:
				files = {'photo' : (itemImg.filename, itemImg, itemImg.content_type)}
				response = requests.post(base_url + '/item', data=userInput, files=files)
			else:
				response=requests.post(base_url + '/item', json=userInput)
			return redirect(url_for('addItems'))

@app.route('/managerShowItems')
def managerShowItems():
	if 'manager' in session:
		response=requests.get(base_url + '/itemList/lightSound')
		lightSoundList = response.json()
		response=requests.get(base_url + '/itemList/food')
		foodList = response.json()
		response=requests.get(base_url + '/itemList/others')
		othersList = response.json()
		return render_template('admin_manager_show_items.html', session='manager', lightSoundList=lightSoundList, foodList=foodList, othersList=othersList)
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/adminShowItems')
def adminShowItems():
	if 'admin' in session:
		response=requests.get(base_url + '/itemList/lightSound')
		lightSoundList = response.json()
		response=requests.get(base_url + '/itemList/food')
		foodList = response.json()
		response=requests.get(base_url + '/itemList/others')
		othersList = response.json()
		return render_template('admin_manager_show_items.html', session='admin', lightSoundList=lightSoundList, foodList=foodList, othersList=othersList)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerItemDetails/<itemID>')
def managerItemDetails(itemID):
	if 'manager' in session:
		itemID = itemID.upper()
		response=requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		return render_template('admin_manager_item_profile.html', session='manager', itemID=itemID, itemDetails=itemDetails)
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerEditItem/<itemID>')
def managerEditItem(itemID):
	if 'manager' in session:
		itemID = itemID.upper()
		response=requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		return render_template('manager_item_edit.html', session='manager', itemID=itemID, itemDetails=itemDetails)
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerUpdateItem', methods=['POST', 'GET'])
def managerUpdateItem():
	if 'manager' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			itemID = userInput['itemID'].upper()
			itemImg = request.files['photo']
			if itemImg:
				files = {'photo' : (itemImg.filename, itemImg, itemImg.content_type)}
				requests.put(base_url + '/item/' + itemID, files=files)
			response = requests.put(base_url + '/item/' + itemID, json=userInput)
			return redirect(url_for('managerItemDetails', itemID=itemID))
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/adminItemDetails/<itemID>')
def adminItemDetails(itemID):
	if 'admin' in session:
		itemID = itemID.upper()
		response=requests.get(base_url + '/item/' + itemID)
		itemDetails = response.json()
		return render_template('admin_manager_item_profile.html', session='admin', itemID=itemID, itemDetails=itemDetails)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerItemDelete', methods=['POST', 'GET'])
def managerItemDelete():
	if 'manager' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			itemID = userInput['itemID'].upper()
			requests.delete(base_url + '/item/' + itemID)
			return redirect(url_for('managerShowItems'))
		else:
			return redirect(url_for('managerHomePage'))

@app.route('/adminItemDelete', methods=['POST', 'GET'])
def adminItemDelete():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			itemID = userInput['itemID'].upper()
			requests.delete(base_url + '/item/' + itemID)
			return redirect(url_for('adminShowItems'))
		else:
			return redirect(url_for('adminHomePage'))

@app.route('/eventRegistration', methods=['POST', 'GET'])
def eventRegistration():
	if 'client' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			userInput['clientID'] = session['client']
			requests.post(base_url + '/costEstReq', json=userInput)
	return redirect(url_for('homePage'))

@app.route('/clientEventList')
def clientEventList():
	if 'client' in session:
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		response = requests.get(base_url + '/clientEventList/' + clientID)
		eventList = response.json()
		return render_template('client_event_list.html', clientDetails=clientDetails, eventList=eventList)
	else:
		return redirect(url_for('homePage'))

@app.route('/clientEventDetails/<eventID>')
def clientEventDetails(eventID):
	if 'client' in session:
		eventID = eventID.upper()
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		if eventDetails['status'] == 'verified':
			response = requests.get(base_url + '/dayEstVer/' + eventID)
			dayEstimationReport = response.json()
			dayEstimate = dayEstimationReport['dayEstimate']
			grandTotal = dayEstimationReport['grandTotal']
			discountAmount = dayEstimationReport['discountAmount']
			discountedGrandTotal = dayEstimationReport['discountedGrandTotal']
		else:
			dayEstimate = {}
			grandTotal = 0
			discountAmount = 0
			discountedGrandTotal = 0
		return render_template('client_event_details.html', clientDetails=clientDetails, eventID=eventID, eventDetails=eventDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, discountAmount=discountAmount, discountedGrandTotal=discountedGrandTotal)
	else:
		return redirect(url_for('homePage'))

@app.route('/adminEventDetailsC/<eventID>')
def adminEventDetailsC(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		return render_template('admin_event_details.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, flag='clientlist')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminEventDetailsE/<eventID>')
def adminEventDetailsE(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		return render_template('admin_event_details.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, flag='eventlist')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminEventDetailsVerE/<eventID>')
def adminEventDetailsVerE(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		discountAmount = dayEstimationReport['discountAmount']
		discountedGrandTotal = dayEstimationReport['discountedGrandTotal']
		return render_template('event_details_verify.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, discountAmount=discountAmount, discountedGrandTotal=discountedGrandTotal, flag='eventlist')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminEventDetailsVerC/<eventID>')
def adminEventDetailsVerC(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		discountAmount = dayEstimationReport['discountAmount']
		discountedGrandTotal = dayEstimationReport['discountedGrandTotal']
		return render_template('event_details_verify.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, discountAmount=discountAmount, discountedGrandTotal=discountedGrandTotal, flag='clientlist')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminEventDetails/<eventID>')
def adminEventDetails(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEstVer/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		discountAmount = dayEstimationReport['discountAmount']
		discountedGrandTotal = dayEstimationReport['discountedGrandTotal']
		return render_template('admin_event_details_ver.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, discountAmount=discountAmount, discountedGrandTotal=discountedGrandTotal)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerEventDetailsC/<eventID>')
def managerEventDetailsC(eventID):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		return render_template('manager_event_details.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, flag='clientlist')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerEventDetailsE/<eventID>')
def managerEventDetailsE(eventID):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		return render_template('manager_event_details.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, flag='eventlist')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerEventDetails/<eventID>')
def managerEventDetails(eventID):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEst/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		return render_template('event_details.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal)
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerVerEventDetails/<eventID>')
def managerVerEventDetails(eventID):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/client/' + eventDetails['clientID'])
		clientDetails = response.json()
		response = requests.get(base_url + '/dayEstVer/' + eventID)
		dayEstimationReport = response.json()
		dayEstimate = dayEstimationReport['dayEstimate']
		grandTotal = dayEstimationReport['grandTotal']
		discountAmount = dayEstimationReport['discountAmount']
		discountedGrandTotal = dayEstimationReport['discountedGrandTotal']
		return render_template('event_details_ver.html', eventID=eventID, eventDetails=eventDetails, clientDetails=clientDetails, dayEstimate=dayEstimate, grandTotal=grandTotal, discountAmount=discountAmount, discountedGrandTotal=discountedGrandTotal)
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/clientEventEdit/<eventID>')
def clientEventEdit(eventID):
	if 'client' in session:
		eventID = eventID.upper()
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		return render_template('event_edit.html', clientDetails=clientDetails, eventID=eventID, eventDetails=eventDetails, session='client')
	else:
		return redirect(url_for('homePage'))

@app.route('/adminEventEditE/<eventID>')
def adminEventEditE(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		return render_template('event_edit.html', eventID=eventID, eventDetails=eventDetails, session='admin', flag='eventlist')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminEventEditC/<eventID>')
def adminEventEditC(eventID):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		return render_template('event_edit.html', eventID=eventID, eventDetails=eventDetails, session='admin', flag='clientlist')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerEventEditE/<eventID>')
def managerEventEditE(eventID):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		return render_template('event_edit.html', eventID=eventID, eventDetails=eventDetails, session='manager', flag='eventlist')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerEventEditC/<eventID>')
def managerEventEditC(eventID):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		return render_template('event_edit.html', eventID=eventID, eventDetails=eventDetails, session='manager', flag='clientlist')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/eventUpdate', methods=['POST', 'GET'])
def eventUpdate():
	if request.method == 'POST':
		userInput = request.form.to_dict()
		if userInput['session'] == 'client':
			if 'client' in session:
					eventID = userInput['eventID'].upper()
					response = requests.put(base_url + '/event/' + eventID, json=userInput)
					return redirect(url_for('clientEventList'))
			else:
				return redirect(url_for('homePage'))
		elif userInput['session'] == 'admin':
			if 'admin' in session:
					eventID = userInput['eventID'].upper()
					response = requests.put(base_url + '/event/' + eventID, json=userInput)
					eventDetails = response.json()
					if userInput['flag'] == 'clientlist':
						return redirect(url_for('adminClientProfile', clientID=eventDetails['clientID']))
			return redirect(url_for('adminHomePage'))
		elif userInput['session'] == 'manager':
			if 'manager' in session:
					eventID = userInput['eventID'].upper()
					response = requests.put(base_url + '/event/' + eventID, json=userInput)
					eventDetails = response.json()
					if userInput['flag'] == 'clientlist':
						return redirect(url_for('managerClientProfile', clientID=eventDetails['clientID']))
			return redirect(url_for('managerHomePage'))

@app.route('/estimateEntry/<eventID>/<day>/<item_cat>/<flag>')
def estimateEntry(eventID, day, item_cat, flag):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/estEntryDetails/' + eventID + '/' + day + '/' + item_cat)
		finalEstimateEntry = response.json()
		estimateEntry = finalEstimateEntry['estimateEntry']
		date = finalEstimateEntry['date']
		return render_template('estimate_entry.html', eventID=eventID, day=day, item_cat=item_cat, estimateEntry=estimateEntry, date=date, flag=flag, session='manager')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/adminEstimateEntry/<eventID>/<day>/<item_cat>/<flag>')
def adminEstimateEntry(eventID, day, item_cat, flag):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/estEntryDetails/' + eventID + '/' + day + '/' + item_cat)
		finalEstimateEntry = response.json()
		estimateEntry = finalEstimateEntry['estimateEntry']
		date = finalEstimateEntry['date']
		return render_template('estimate_entry.html', eventID=eventID, day=day, item_cat=item_cat, estimateEntry=estimateEntry, date=date, flag=flag, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/costEstimateCreate', methods=['POST', 'GET'])
def costEstimateCreate():
	if 'manager' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			costEst = {}
			costEst['eventID'] = userInput['eventID']
			del userInput['eventID']
			costEst['day'] = userInput['day']
			del userInput['day']
			costEst['date'] = userInput['date']
			del userInput['date']
			costEst['item_cat'] = userInput['item_cat']
			del userInput['item_cat']
			qty = {}
			for i in userInput:
				if userInput[i]:
					qty[i] = userInput[i]
				else:
					qty[i] = ''
			costEst['qty'] = str(qty)
			requests.post(base_url + '/costEstCreate', json=costEst)
			if userInput['flag'] == 'clientlist':
				return redirect(url_for('managerEventDetailsC', eventID=costEst['eventID']))
			elif userInput['flag'] == 'eventlist':
				return redirect(url_for('managerEventDetailsE', eventID=costEst['eventID']))
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/costEstimateEdit', methods=['POST', 'GET'])
def costEstimateEdit():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			costEst = {}
			costEst['eventID'] = userInput['eventID']
			del userInput['eventID']
			costEst['day'] = userInput['day']
			del userInput['day']
			costEst['date'] = userInput['date']
			del userInput['date']
			costEst['item_cat'] = userInput['item_cat']
			del userInput['item_cat']
			qty = {}
			for i in userInput:
				if userInput[i]:
					qty[i] = userInput[i]
				else:
					qty[i] = ''
			costEst['qty'] = str(qty)
			requests.post(base_url + '/costEstCreate', json=costEst)
			if userInput['flag'] == 'clientlist':
				return redirect(url_for('adminEventDetailsVerC', eventID=costEst['eventID']))
			elif userInput['flag'] == 'eventlist':
				return redirect(url_for('adminEventDetailsVerE', eventID=costEst['eventID']))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/managerDayWiseEstimate/<eventID>/<day>')
def managerDayWiseEstimate(eventID, day):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/costEst/' + eventID + '/' + day)
		estimationReport = response.json()
		return render_template('daywise_estimate.html', eventID=eventID, eventDetails=eventDetails, estimationReport=estimationReport, session='manager')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/managerDayWiseEstimateVer/<eventID>/<day>')
def managerDayWiseEstimateVer(eventID, day):
	if 'manager' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/costEstVer/' + eventID + '/' + day)
		estimationReport = response.json()
		return render_template('daywise_estimate.html', eventID=eventID, eventDetails=eventDetails, estimationReport=estimationReport, session='manager')
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/adminDayWiseEstimate/<eventID>/<day>')
def adminDayWiseEstimate(eventID, day):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/costEst/' + eventID + '/' + day)
		estimationReport = response.json()
		return render_template('daywise_estimate.html', eventID=eventID, eventDetails=eventDetails, estimationReport=estimationReport, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/adminDayWiseEstimateVer/<eventID>/<day>')
def adminDayWiseEstimateVer(eventID, day):
	if 'admin' in session:
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/costEstVer/' + eventID + '/' + day)
		estimationReport = response.json()
		return render_template('daywise_estimate.html', eventID=eventID, eventDetails=eventDetails, estimationReport=estimationReport, session='admin')
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/clientDayWiseEstimate/<eventID>/<day>')
def clientDayWiseEstimate(eventID, day):
	if 'client' in session:
		clientID = session['client']
		response = requests.get(base_url + '/client/' + clientID)
		clientDetails = response.json()
		eventID = eventID.upper()
		response = requests.get(base_url + '/event/' + eventID)
		eventDetails = response.json()
		response = requests.get(base_url + '/costEstVer/' + eventID + '/' + day)
		estimationReport = response.json()
		return render_template('user_daywise_estimate.html', clientDetails=clientDetails, eventID=eventID, eventDetails=eventDetails, estimationReport=estimationReport)
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/submitEstimate', methods=['POST', 'GET'])
def submitEstimate():
	if 'manager' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/submitEst', json=userInput)
			if userInput['flag'] == 'clientlist':
				return redirect(url_for('managerEventDetailsC', eventID=userInput['eventID']))
			elif userInput['flag'] == 'eventlist':
				return redirect(url_for('managerEventDetailsE', eventID=userInput['eventID']))
	else:
		return redirect(url_for('managerHomePage'))

@app.route('/grantDiscount', methods=['POST', 'GET'])
def grantDiscount():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/grantDiscount', json=userInput)
			if userInput['flag'] == 'clientlist':
				return redirect(url_for('adminEventDetailsVerC', eventID=userInput['eventID']))
			elif userInput['flag'] == 'eventlist':
				return redirect(url_for('adminEventDetailsVerE', eventID=userInput['eventID']))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/verifyEstimate', methods=['POST', 'GET'])
def verifyEstimate():
	if 'admin' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/verifyEstimate', json=userInput)
			eventDetails = response.json()
			if userInput['flag'] == 'clientlist':
				return redirect(url_for('adminClientProfile', clientID=eventDetails['clientID']))
			else:
				return redirect(url_for('adminHomePage'))
	else:
		return redirect(url_for('adminHomePage'))

@app.route('/reviewEstimate', methods=['POST', 'GET'])
def reviewEstimate():
	if 'client' in session:
		if request.method == 'POST':
			userInput = request.form.to_dict()
			response = requests.post(base_url + '/reviewEstimate', json=userInput)
			return redirect(url_for('clientEventDetails', eventID=userInput['eventID']))
	else:
		return redirect(url_for('homePage'))

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')