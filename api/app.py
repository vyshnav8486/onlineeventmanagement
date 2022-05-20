from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse
from flask_cors import CORS
from firebase import Firebase
import werkzeug
from datetime import datetime
from pytz import timezone
import ast

app = Flask(__name__)
api = Api(app)
CORS(app)

config = {
  "apiKey": "AIzaSyCjM4iy43XcmqJXXm1vLSXiVDKcIJazMCM",
  "authDomain": "thinkfotechinnovations.firebaseapp.com",
  "databaseURL": "https://thinkfotechinnovations.firebaseio.com",
  "storageBucket": "thinkfotechinnovations.appspot.com",
}

firebase = Firebase(config)
db = firebase.database()
storage = firebase.storage()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

adminLoginParser = reqparse.RequestParser()
adminLoginParser.add_argument('email', type=str, help='email required', required=True)
adminLoginParser.add_argument('password', type=str, help='password required', required=True)

managerLoginParser = reqparse.RequestParser()
managerLoginParser.add_argument('email', type=str, help='email required', required=True)
managerLoginParser.add_argument('password', type=str, help='password required', required=True)

clientRegParser = reqparse.RequestParser()
clientRegParser.add_argument('name', type=str, help='name of the client required', required=True)
clientRegParser.add_argument('mobileNumber', type=int, help='mobile number of client required', required=True)
clientRegParser.add_argument('address', type=str, help='address of client required', required=True)
clientRegParser.add_argument('city', type=str, help='city of client required', required=True)
clientRegParser.add_argument('email', type=str, help='email of client required', required=True)
clientRegParser.add_argument('password', type=str, help='password required', required=True)
clientRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, help='photo of client required', location='files')

clientUpdateParser = reqparse.RequestParser()
clientUpdateParser.add_argument('name', type=str)
clientUpdateParser.add_argument('mobileNumber', type=int)
clientUpdateParser.add_argument('address', type=str)
clientUpdateParser.add_argument('city', type=str)
clientUpdateParser.add_argument('email', type=str)
clientUpdateParser.add_argument('password', type=str)
clientUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

clientLoginParser = reqparse.RequestParser()
clientLoginParser.add_argument('email', type=str, help='email required', required=True)
clientLoginParser.add_argument('password', type=str, help='password required', required=True)

messageParser = reqparse.RequestParser()
messageParser.add_argument('sender', type=str, help='sender required', required=True)
messageParser.add_argument('receiver', type=str, help='receiver required', required=True)
messageParser.add_argument('action', type=str, help='action required', required=True)
messageParser.add_argument('message', type=str)
messageParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files', action='append')

itemRegParser = reqparse.RequestParser()
itemRegParser.add_argument('item_cat', type=str, help='category of the item required', required=True)
itemRegParser.add_argument('item_name', type=str, help='name of the item required', required=True)
itemRegParser.add_argument('item_unit', type=str, help='unit of the item required', required=True)
itemRegParser.add_argument('item_price', type=int, help='price of the item (per unit) required', required=True)
itemRegParser.add_argument('item_desc', type=str, help='item description required', required=True)
itemRegParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, help='photo of item required', location='files')

itemUpdateParser = reqparse.RequestParser()
itemUpdateParser.add_argument('item_cat', type=str)
itemUpdateParser.add_argument('item_name', type=str)
itemUpdateParser.add_argument('item_unit', type=str)
itemUpdateParser.add_argument('item_price', type=int)
itemUpdateParser.add_argument('item_desc', type=str)
itemUpdateParser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')

costEstimationReqParser = reqparse.RequestParser()

costEstimationReqParser.add_argument('clientID', type=str, help='client id required', required=True)
costEstimationReqParser.add_argument('event_name', type=str, help='name of event required', required=True)
costEstimationReqParser.add_argument('event_date', type=str, help='date of event required', required=True)
costEstimationReqParser.add_argument('event_duration', type=int, help='duration of event required', required=True)
costEstimationReqParser.add_argument('event_desc', type=str, help='description of event required')

eventUpdateParser = reqparse.RequestParser()
eventUpdateParser.add_argument('event_name', type=str)
eventUpdateParser.add_argument('event_date', type=str)
eventUpdateParser.add_argument('event_duration', type=int)
eventUpdateParser.add_argument('event_desc', type=str)

costEstimationCreateParser = reqparse.RequestParser()
costEstimationCreateParser.add_argument('eventID', type=str, help='event id required', required=True)
costEstimationCreateParser.add_argument('day', type=int, help='day required', required=True)
costEstimationCreateParser.add_argument('date', type=str, help='date required', required=True)
costEstimationCreateParser.add_argument('item_cat', type=str, help='category of item required', required=True)
costEstimationCreateParser.add_argument('qty', type=str, help='quantity required', required=True)

submitEstimateParser = reqparse.RequestParser()
submitEstimateParser.add_argument('eventID', type=str, help='event id required', required=True)

grantDiscountParser = reqparse.RequestParser()
grantDiscountParser.add_argument('eventID', type=str, help='event id required', required=True)
grantDiscountParser.add_argument('discountAmount', type=int, help='discount amount required', required=True)

verifyEstimateParser = reqparse.RequestParser()
verifyEstimateParser.add_argument('eventID', type=str, help='event id required', required=True)

reviewEstimateParser = reqparse.RequestParser()
reviewEstimateParser.add_argument('eventID', type=str, help='event id required', required=True)
reviewEstimateParser.add_argument('action', type=str, help='action required', required=True)

def eventStatus():
  eventList = db.child('EventManagementSystem').child('eventList').get().val()
  if eventList == None:
    eventList = {}
  costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
  if costEstList == None:
    costEstList = {}
  for i in eventList:
    if i in costEstList:
      eventList[i]['reportStatus'] = 'created'
    else:
      eventList[i]['reportStatus'] = 'not created'
  for i in eventList:
    if eventList[i]['status'] == 'created':
      eventList[i]['eventStatus'] = 'estimate on verification'
    elif eventList[i]['status'] == 'requested':
      if eventList[i]['reportStatus'] == 'created':
        eventList[i]['eventStatus'] = 'site surveying started'
      elif eventList[i]['reportStatus'] == 'not created':
        eventList[i]['eventStatus'] = 'requested for estimate'
    elif eventList[i]['status'] == 'verified':
      eventList[i]['eventStatus'] = 'estimate verified and forwarded to client'
  return eventList

class AdminLogin(Resource):
  def post(self):
    args = adminLoginParser.parse_args()
    adminPassword = db.child('EventManagementSystem').child('adminPassword').get().val()
    if adminPassword == None:
      adminPassword = 'admin123'
      db.child('EventManagementSystem').child('adminPassword').set(adminPassword)
    if 'admin@gmail.com' == args['email'] and adminPassword == args['password']:
      return 'admin'
    else:
      return ''

class ManagerLogin(Resource):
  def post(self):
    args = managerLoginParser.parse_args()
    managerPassword = db.child('EventManagementSystem').child('managerPassword').get().val()
    if managerPassword == None:
      managerPassword = 'manager123'
      db.child('EventManagementSystem').child('managerPassword').set(managerPassword)
    if 'manager@gmail.com' == args['email'] and managerPassword == args['password']:
      return 'manager'
    else:
      return ''

class ClientReg(Resource):
  def post(self):
    args = clientRegParser.parse_args()
    if args['photo']:
      if not allowed_file(args['photo'].filename):
        abort(400, message='unsupported file format')
    clientCnt = db.child('EventManagementSystem').child('clientCnt').get().val()
    if clientCnt == None:
      clientCnt = 0
    clientCnt += 1
    db.child('EventManagementSystem').child('clientCnt').set(clientCnt)
    clientID = 'CLI' + str(100 + clientCnt)
    if args['photo']:
      f = args['photo']
      del args['photo']
      storage.child('EventManagementSystem').child('clientImage').child(clientID).child('pic.jpg').put(f)    
    else:
      del args['photo']
      storage.child('EventManagementSystem').child('clientImage').child(clientID).child('pic.jpg').put('static/user.png')
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    args['imgUrl'] = storage.child('EventManagementSystem').child('clientImage').child(clientID).child('pic.jpg').get_url(None)
    clientList[clientID] = args
    db.child('EventManagementSystem').child('clientList').set(clientList)
    return args

  def get(self):
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    return clientList

class ClientUpdate(Resource):
  def get(self, clientID):
    clientID = clientID.upper()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    if clientID in clientList:
      clientDetails = clientList[clientID]
    else:
      abort(400, message='client not found')
    return clientDetails

  def put(self, clientID):
    clientID = clientID.upper()
    args = clientUpdateParser.parse_args()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    if clientID in clientList:
        if args['name']:
          clientList[clientID]['name'] = args['name']
        if args['mobileNumber']:
          clientList[clientID]['mobileNumber'] = args['mobileNumber']
        if args['address']:
          clientList[clientID]['address'] = args['address']
        if args['city']:
          clientList[clientID]['city'] = args['city']
        if args['email']:
          clientList[clientID]['email'] = args['email']
        if args['password']:
          clientList[clientID]['password'] = args['password']
        if args['photo']:
          storage.child('EventManagementSystem').child('clientImage').child(clientID).child('pic.jpg').put(args['photo'])
          clientList[clientID]['imgUrl'] = storage.child('EventManagementSystem').child('clientImage').child(clientID).child('pic.jpg').get_url(None)
        db.child('EventManagementSystem').child('clientList').set(clientList)
        clientDetails= clientList[clientID]
    else:
      abort(400, message='client not found')
    return clientDetails

  def delete(self, clientID):
    clientID = clientID.upper()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    if clientID in clientList:
        del clientList[clientID]
        db.child('EventManagementSystem').child('clientList').set(clientList)
    else:
      abort(400, message='client not found')
    return clientList

class ClientLogin(Resource):
  def post(self):
    args = clientLoginParser.parse_args()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    clientID = ''
    for i in clientList:
      if clientList[i]['email'] == args['email'] and clientList[i]['password'] == args['password']:
          clientID = i
    return clientID

class Message(Resource):
  def post(self):
    args = messageParser.parse_args()
    sender = args['sender'].upper()
    receiver = args['receiver'].upper()
    args['sender'] = sender
    args['receiver'] = receiver
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    if sender == receiver:
      abort(400, message='sender and receiver cannot be same') 
    if sender != 'ADMIN':
      if not sender in clientList:
        abort(400, message='invalid sender')
    if receiver != 'ADMIN':
      if not receiver in clientList:
        abort(400, message='invalid receiver')
    if args['action'] == 'send':
      if args['message'] or args['photo']:
        if args['photo']:
          images = args['photo']
          for img in images:
            if not allowed_file(img.filename):
              abort(400, message='unsupported file format')
          for img in images:
            imgCnt = db.child('EventManagementSystem').child('imgCnt').get().val()
            if imgCnt == None:
              imgCnt = 0
            imgCnt += 1
            db.child('EventManagementSystem').child('imgCnt').set(imgCnt)
            imgName = 'IMG' + str(100 + imgCnt)
            msgCnt = db.child('EventManagementSystem').child('msgCnt').get().val()
            if msgCnt == None:
              msgCnt = 0
            msgCnt += 1
            db.child('EventManagementSystem').child('msgCnt').set(msgCnt)
            msgID = 'MSG' + str(100 + msgCnt)
            storage.child('EventManagementSystem').child('msgImage').child(msgID).child(imgName).put(img)
            imgUrl = storage.child('EventManagementSystem').child('msgImage').child(msgID).child(imgName).get_url(None)
            msgList = db.child('EventManagementSystem').child('msgList').get().val()
            if msgList == None:
              msgList = {}
            msgList[msgID] = {
              'sender'   : sender,
              'receiver' : receiver,
              'type'     : 'img',
              'imgUrl'   : imgUrl
              }
            x = datetime.now(timezone("Asia/Kolkata"))
            msgList[msgID]['date'] = x.strftime('%d/%m/%Y')
            msgList[msgID]['time'] = x.strftime('%X')
            db.child('EventManagementSystem').child('msgList').set(msgList)
        if args['message']:
          msgCnt = db.child('EventManagementSystem').child('msgCnt').get().val()
          if msgCnt == None:
            msgCnt = 0
          msgCnt += 1
          db.child('EventManagementSystem').child('msgCnt').set(msgCnt)
          msgID = 'MSG' + str(100 + msgCnt)
          msgList = db.child('EventManagementSystem').child('msgList').get().val()
          if msgList == None:
            msgList = {}              
          msgList[msgID]= {
            'sender'   : sender,
            'receiver' : receiver,
            'type'     : 'text',
            'message'  : args['message']
            }
          x = datetime.now()
          x = datetime.now(timezone("Asia/Kolkata"))
          msgList[msgID]['date'] = x.strftime('%d/%m/%Y')
          msgList[msgID]['time'] = x.strftime('%X')
          db.child('EventManagementSystem').child('msgList').set(msgList)      
        return msgList
      else:
        abort(400, message='content required')
    elif args['action'] == 'get':
      msgList = db.child('EventManagementSystem').child('msgList').get().val()
      if msgList == None:
        msgList = {}
      tempMsgList = {}
      msgIDList = list(msgList.keys())
      msgIDList.reverse()
      for msgID in msgIDList:
        if msgList[msgID]['sender'] == sender or msgList[msgID]['receiver'] == sender:
          if msgList[msgID]['sender'] == receiver or msgList[msgID]['receiver'] == receiver:
            tempMsgList[msgID] = msgList[msgID]
      return tempMsgList
    else:
      abort(400, message='invalid action')

class MessageInbox(Resource):
  def post(self,clientID):
    clientID = clientID.upper()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    msgList = db.child('EventManagementSystem').child('msgList').get().val()
    if msgList == None:
      msgList = {}
    if clientID != 'ADMIN':
      if not clientID in clientList:
        abort(400, message='client not found')
    msgIDList = list(msgList.keys())
    msgIDList.reverse()
    tempMsgList = {}
    for msg in msgIDList:
      if msgList[msg]['sender'] == clientID or msgList[msg]['receiver'] == clientID:
        if msgList[msg]['sender'] != clientID:
          othClientID = msgList[msg]['sender']
        elif msgList[msg]['receiver'] != clientID:
          othClientID = msgList[msg]['receiver']
        flag = 0
        for i in tempMsgList:
          if tempMsgList[i]['sender'] == othClientID or tempMsgList[i]['receiver'] == othClientID:
            flag = 1
            break
        if flag == 0:
          tempMsgList[msg] = msgList[msg]
          tempMsgList[msg]['othClientID'] = othClientID
          if othClientID != 'ADMIN':
            tempMsgList[msg]['clientDetails'] = clientList[othClientID]
    return tempMsgList

class ItemReg(Resource):
  def post(self):
    args = itemRegParser.parse_args()
    if not (args['item_cat'] == 'lightSound' or args['item_cat'] == 'food' or args['item_cat'] == 'others'):
      abort(400, message='invalid category')
    if args['photo']:
      if not allowed_file(args['photo'].filename):
        abort(400, message='unsupported file format')
    itemCnt = db.child('EventManagementSystem').child('itemCnt').get().val()
    if itemCnt == None:
      itemCnt = 0
    itemCnt += 1
    db.child('EventManagementSystem').child('itemCnt').set(itemCnt)
    itemID = 'ITEM' + str(100 + itemCnt)
    if args['photo']:
      f = args['photo']
      del args['photo']
      storage.child('EventManagementSystem').child('itemImage').child(itemID).child('pic.jpg').put(f)    
    else:
      del args['photo']
      storage.child('EventManagementSystem').child('itemImage').child(itemID).child('pic.jpg').put('static/no_image.jpg')
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    args['imgUrl'] = storage.child('EventManagementSystem').child('itemImage').child(itemID).child('pic.jpg').get_url(None)
    itemList[itemID] = args
    db.child('EventManagementSystem').child('itemList').set(itemList)
    return args

  def get(self):
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    return itemList

class ItemList(Resource):
  def get(self, cat):
    catList = ['lightSound', 'food', 'others']
    if not cat in catList:
      abort(400, message='invalid category')
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    tempItemList = {}
    for i in itemList:
      if itemList[i]['item_cat'] == cat:
        tempItemList[i] = itemList[i]
    return tempItemList

class ItemUpdate(Resource):
  def get(self, itemID):
    itemID = itemID.upper()
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    if itemID in itemList:
      itemDetails = itemList[itemID]
    else:
      abort(400, message='item not found')
    return itemDetails

  def put(self, itemID):
    itemID = itemID.upper()
    args = itemUpdateParser.parse_args()
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    if itemID in itemList:
        if args['item_name']:
          itemList[itemID]['item_name'] = args['item_name']
        if args['item_unit']:
          itemList[itemID]['item_unit'] = args['item_unit']
        if args['item_price']:
          itemList[itemID]['item_price'] = args['item_price']
        if args['item_desc']:
          itemList[itemID]['item_desc'] = args['item_desc']
        if args['item_cat']:
          if not (args['item_cat'] == 'lightSound' or args['item_cat'] == 'food' or args['item_cat'] == 'others'):
            abort(400, message='invalid category')
          itemList[itemID]['item_cat'] = args['item_cat']
        if args['photo']:
          storage.child('EventManagementSystem').child('itemImage').child(itemID).child('pic.jpg').put(args['photo'])
          itemList[itemID]['imgUrl'] = storage.child('EventManagementSystem').child('itemImage').child(itemID).child('pic.jpg').get_url(None)
        db.child('EventManagementSystem').child('itemList').set(itemList)
        itemDetails= itemList[itemID]
    else:
      abort(400, message='item not found')
    return itemDetails

  def delete(self, itemID):
    itemID = itemID.upper()
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    if itemID in itemList:
      flag = 0
      for eventid in costEstList:
        for day in costEstList[eventid]:
          for itemid in costEstList[eventid][day]:
            if itemid == itemID:
              flag = 1
              break
    else:
      abort(400, message='item not found')
    if flag == 0:
      del itemList[itemID]
      db.child('EventManagementSystem').child('itemList').set(itemList)
    elif flag == 1:
      abort(400, message='item cant delete')
    return itemList

class CostEstimationRequest(Resource):
  def post(self):
    args = costEstimationReqParser.parse_args()
    clientID = args['clientID'].upper()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    if not clientID in clientList:
      abort(400, message='client not found')
    eventCnt = db.child('EventManagementSystem').child('eventCnt').get().val()
    if eventCnt == None:
      eventCnt = 0
    eventCnt += 1
    db.child('EventManagementSystem').child('eventCnt').set(eventCnt)
    eventID = 'EVNT' + str(100 + eventCnt)
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    eventList[eventID] = args
    eventList[eventID]['clientID'] = clientID
    eventList[eventID]['status'] = 'requested'
    db.child('EventManagementSystem').child('eventList').set(eventList)
    return args

class EventList(Resource):
  def get(self, cat):
    catList = ['all', 'new_request', 'on_survey', 'for_verification', 'forwarded']
    if not cat in catList:
      abort(400, message='invalid category')
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    eventList = eventStatus()
    tempEventList = {}
    if cat == 'all':
      tempEventList = eventList
    elif cat == 'new_request':
      for i in eventList:
        if eventList[i]['eventStatus'] == 'requested for estimate':
          tempEventList[i] = eventList[i]
    elif cat == 'on_survey':
      for i in eventList:
        if eventList[i]['eventStatus'] == 'site surveying started':
          tempEventList[i] = eventList[i]
    elif cat == 'for_verification':
      for i in eventList:
        if eventList[i]['eventStatus'] == 'estimate on verification':
          tempEventList[i] = eventList[i]
    elif cat == 'forwarded':
      for i in eventList:
        if eventList[i]['eventStatus'] == 'estimate verified and forwarded to client':
          tempEventList[i] = eventList[i]
    for i in tempEventList:
      tempEventList[i]['clientDetails'] = clientList[tempEventList[i]['clientID']]
    return tempEventList

class ClientEventList(Resource):
  def get(self, clientID):
    clientID = clientID.upper()
    clientList = db.child('EventManagementSystem').child('clientList').get().val()
    if clientList == None:
      clientList = {}
    if not clientID in clientList:
      abort(400, message='client not found')
    eventList = eventStatus()
    tempEventList = {}
    for i in eventList:
      if eventList[i]['clientID'] == clientID:
        tempEventList[i] = eventList[i]
    return tempEventList

class EventUpdate(Resource):
  def get(self, eventID):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    if eventID in eventList:
      eventDetails = eventList[eventID]
    else:
      abort(400, message='event not found')
    if eventID in costEstList:
      eventDetails['reportStatus'] = 'created'
    else:
      eventDetails['reportStatus'] = 'not created'
    if eventDetails['status'] == 'created':
      eventDetails['eventStatus'] = 'estimate on verification'
    elif eventDetails['status'] == 'requested':
      if eventDetails['reportStatus'] == 'created':
        eventDetails['eventStatus'] = 'site surveying strated'
      elif eventDetails['reportStatus'] == 'not created':
        eventDetails['eventStatus'] = 'requested for estimate'
    elif eventDetails['status'] == 'verified':
      eventDetails['eventStatus'] = 'estimate verified and forwarded to client'
    return eventDetails

  def put(self, eventID):
    eventID = eventID.upper()
    args = eventUpdateParser.parse_args()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if eventID in eventList:
        if args['event_name']:
          eventList[eventID]['event_name'] = args['event_name']
        if args['event_date']:
          eventList[eventID]['event_date'] = args['event_date']
        if args['event_duration']:
          eventList[eventID]['event_duration'] = args['event_duration']
        if args['event_desc']:
          eventList[eventID]['event_desc'] = args['event_desc']
        db.child('EventManagementSystem').child('eventList').set(eventList)
        eventDetails= eventList[eventID]
    else:
      abort(400, message='event not found')
    return eventDetails

  def delete(self, eventID):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    if eventID in eventList:
      if not eventID in costEstList:
        del eventList[eventID]
        db.child('EventManagementSystem').child('eventList').set(eventList)
      else:
        abort(400, message='event cant delete')
    else:
      abort(400, message='event not found')
    return eventList

class CostEstimationCreate(Resource):
  def post(self):
    args = costEstimationCreateParser.parse_args()
    eventID = args['eventID'].upper()
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    catList = ['lightSound', 'food', 'others']
    if not args['item_cat'] in catList:
      abort(400, message='invalid category')
    if not eventDetails['event_duration'] >= args['day']:
      abort(400, message='invalid day')
    qty = ast.literal_eval(args['qty'])
    nameDay = 'DAY_' + str(args['day'])
    for i in qty:
      costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
      if costEstList == None:
        costEstList = {}
      if qty[i]:
        if i.upper() in itemList:
          if itemList[i.upper()]['item_cat'] == args['item_cat']:
            if not eventID in costEstList:
              costEstList[eventID] = {
                nameDay : {
                  i.upper() : int(qty[i])
                }
              }
            else:
              if not nameDay in costEstList[eventID]:
                costEstList[eventID][nameDay] = {
                  i.upper() : int(qty[i])
                }
              else:
                costEstList[eventID][nameDay][i.upper()] = int(qty[i])
      else:
        if eventID in costEstList:
          if nameDay in costEstList[eventID]:
            if i.upper() in costEstList[eventID][nameDay]:
              if itemList[i.upper()]['item_cat'] == args['item_cat']:
                del costEstList[eventID][nameDay][i.upper()]
      db.child('EventManagementSystem').child('costEstimationList').set(costEstList)
      eventList[eventID][nameDay + '_date'] = args['date']
      db.child('EventManagementSystem').child('eventList').set(eventList)
      if eventID in costEstList:
        costEst = costEstList[eventID]
      else:
        costEst = {}
    return costEst

class DayEstimationReport(Resource):
  def get(self, eventID):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    dayEstimate = {}
    if not eventID in costEstList:
      for i in range(1, eventDetails['event_duration']+1):
        keyName = 'DAY_' + str(i)
        dayEstimate[keyName] = {
          'dayName'   : 'Day ' + str(i),
          'totalCost' : 0
        }
      grandTotal = 0
      dayEstimationReport = {
        'dayEstimate'          : dayEstimate,
        'grandTotal'           : grandTotal,
        'discountAmount'       : 0,
        'discountedGrandTotal' : grandTotal
      }
    else:
      grandTotal = 0
      for i in range(1, eventDetails['event_duration']+1):
        keyName = 'DAY_' + str(i)
        if keyName in costEstList[eventID]:
          totalCost = 0
          for j in costEstList[eventID][keyName]:
            totalCost = totalCost + (int(itemList[j]['item_price']) * int(costEstList[eventID][keyName][j]))
          dayEstimate[keyName] = {
            'dayName'   : 'Day ' + str(i),
            'totalCost' : totalCost
          }
          grandTotal = grandTotal + totalCost
        else:
          dayEstimate[keyName] = {
            'dayName'   : 'Day ' + str(i),
            'totalCost' : 0
          }
          grandTotal = grandTotal + 0
      if 'discountAmount' in eventDetails:
        discountAmount = eventDetails['discountAmount']
      else:
        discountAmount = 0
      discountedGrandTotal = grandTotal - discountAmount
      dayEstimationReport = {
        'dayEstimate'          : dayEstimate,
        'grandTotal'           : grandTotal,
        'discountAmount'       : discountAmount,
        'discountedGrandTotal' : discountedGrandTotal
      }
    return dayEstimationReport

class DayEstimationReportVer(Resource):
  def get(self, eventID):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    verifiedCostEst = db.child('EventManagementSystem').child('verifiiedCostEst').get().val()
    if verifiedCostEst == None:
      verifiedCostEst = {}
    dayEstimate = {}
    if not eventID in verifiedCostEst:
      for i in range(1, eventDetails['event_duration']+1):
        keyName = 'DAY_' + str(i)
        dayEstimate[keyName] = {
          'dayName'   : 'Day ' + str(i),
          'totalCost' : 0
        }
      grandTotal = 0
      dayEstimationReport = {
        'dayEstimate'          : dayEstimate,
        'grandTotal'           : grandTotal,
        'discountAmount'       : 0,
        'discountedGrandTotal' : grandTotal
      }
    else:
      grandTotal = 0
      for i in range(1, eventDetails['event_duration']+1):
        keyName = 'DAY_' + str(i)
        if keyName in verifiedCostEst[eventID]:
          totalCost = 0
          for j in verifiedCostEst[eventID][keyName]:
            totalCost = totalCost + int(verifiedCostEst[eventID][keyName][j]['totalCost'])
          dayEstimate[keyName] = {
            'dayName'   : 'Day ' + str(i),
            'totalCost' : totalCost
          }
          grandTotal = grandTotal + totalCost
        else:
          dayEstimate[keyName] = {
            'dayName'   : 'Day ' + str(i),
            'totalCost' : 0
          }
          grandTotal = grandTotal + 0
      if 'discountAmount' in eventDetails:
        discountAmount = eventDetails['discountAmount']
      else:
        discountAmount = 0
      discountedGrandTotal = grandTotal - discountAmount
      dayEstimationReport = {
        'dayEstimate'          : dayEstimate,
        'grandTotal'           : grandTotal,
        'discountAmount'       : discountAmount,
        'discountedGrandTotal' : discountedGrandTotal
      }
    return dayEstimationReport

class EstimationReport(Resource):
  def get(self, eventID, day):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    if not (int(day.split('_')[1]) <= eventDetails['event_duration']):
      abort(400, message='invalid day')
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    flag = 0
    if eventID in costEstList:
      if day in costEstList[eventID]:
        flag = 1
        lightSound = {}
        lightSoundTotal = 0
        for i in costEstList[eventID][day]:
          if itemList[i]['item_cat'] == 'lightSound':
            lightSound[i] = {
              'itemDetails' : itemList[i],
              'qty'         : costEstList[eventID][day][i],
              'totalCost'   : int(costEstList[eventID][day][i]) * int(itemList[i]['item_price'])
            }
            lightSoundTotal = lightSoundTotal + (int(costEstList[eventID][day][i]) * int(itemList[i]['item_price']))
        food = {}
        foodTotal = 0
        for i in costEstList[eventID][day]:
          if itemList[i]['item_cat'] == 'food':
            food[i] = {
              'itemDetails' : itemList[i],
              'qty'         : costEstList[eventID][day][i],
              'totalCost'   : int(costEstList[eventID][day][i]) * int(itemList[i]['item_price'])
            }
            foodTotal = foodTotal + (int(costEstList[eventID][day][i]) * int(itemList[i]['item_price']))
        others = {}
        othersTotal = 0
        for i in costEstList[eventID][day]:
          if itemList[i]['item_cat'] == 'others':
            others[i] = {
              'itemDetails' : itemList[i],
              'qty'         : costEstList[eventID][day][i],
              'totalCost'   : int(costEstList[eventID][day][i]) * int(itemList[i]['item_price'])
            }
            othersTotal = othersTotal + (int(costEstList[eventID][day][i]) * int(itemList[i]['item_price']))
        grandTotal = lightSoundTotal + foodTotal + othersTotal
        date = eventDetails[day + '_date']
    if flag == 0:
      lightSound = {}
      food = {}
      others = {}
      lightSoundTotal = 0
      foodTotal = 0
      othersTotal = 0
      grandTotal = 0
      date = ''
    estimationReport = {
      'dayName'         : 'DAY ' + (day.split('_')[1]),
      'lightSound'      : lightSound,
      'food'            : food,
      'others'          : others,
      'date'            : date,
      'lightSoundTotal' : lightSoundTotal,
      'foodTotal'       : foodTotal,
      'othersTotal'     : othersTotal,
      'grandTotal'      : grandTotal
    }
    return estimationReport

class EstimationReportVer(Resource):
  def get(self, eventID, day):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    if not (int(day.split('_')[1]) <= eventDetails['event_duration']):
      abort(400, message='invalid day')
    verifiedCostEst = db.child('EventManagementSystem').child('verifiiedCostEst').get().val()
    if verifiedCostEst == None:
      verifiedCostEst = {}
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    flag = 0
    if eventID in verifiedCostEst:
      if day in verifiedCostEst[eventID]:
        flag = 1
        lightSound = {}
        lightSoundTotal = 0
        for i in verifiedCostEst[eventID][day]:
          if itemList[i]['item_cat'] == 'lightSound':
            lightSound[i] = {
              'itemDetails' : itemList[i],
              'qty'         : verifiedCostEst[eventID][day][i]['qty'],
              'totalCost'   : int(verifiedCostEst[eventID][day][i]['qty']) * int(verifiedCostEst[eventID][day][i]['price'])
            }
            lightSoundTotal = lightSoundTotal + (int(verifiedCostEst[eventID][day][i]['qty']) * int(verifiedCostEst[eventID][day][i]['price']))
        food = {}
        foodTotal = 0
        for i in verifiedCostEst[eventID][day]:
          if itemList[i]['item_cat'] == 'food':
            food[i] = {
              'itemDetails' : itemList[i],
              'qty'         : verifiedCostEst[eventID][day][i]['qty'],
              'totalCost'   : int(verifiedCostEst[eventID][day][i]['qty']) * int(verifiedCostEst[eventID][day][i]['price'])
            }
            foodTotal = foodTotal + (int(verifiedCostEst[eventID][day][i]['qty']) * int(verifiedCostEst[eventID][day][i]['price']))
        others = {}
        othersTotal = 0
        for i in verifiedCostEst[eventID][day]:
          if itemList[i]['item_cat'] == 'others':
            others[i] = {
              'itemDetails' : itemList[i],
              'qty'         : verifiedCostEst[eventID][day][i]['qty'],
              'totalCost'   : int(verifiedCostEst[eventID][day][i]['qty']) * int(verifiedCostEst[eventID][day][i]['price'])
            }
            othersTotal = othersTotal + (int(verifiedCostEst[eventID][day][i]['qty']) * int(verifiedCostEst[eventID][day][i]['price']))
        grandTotal = lightSoundTotal + foodTotal + othersTotal
        date = eventDetails[day + '_date']
    if flag == 0:
      lightSound = {}
      food = {}
      others = {}
      lightSoundTotal = 0
      foodTotal = 0
      othersTotal = 0
      grandTotal = 0
      date = ''
    estimationReport = {
      'dayName'         : 'DAY ' + (day.split('_')[1]),
      'lightSound'      : lightSound,
      'food'            : food,
      'others'          : others,
      'date'            : date,
      'lightSoundTotal' : lightSoundTotal,
      'foodTotal'       : foodTotal,
      'othersTotal'     : othersTotal,
      'grandTotal'      : grandTotal
    }
    return estimationReport

class EstimateEntryDetails(Resource):
  def get(self, eventID, day, item_cat):
    eventID = eventID.upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    if not int(eventDetails['event_duration']) >= int(day):
      abort(400, message='invalid day')
    else:
      dayName = 'DAY_' + str(day) + '_date'
      day = 'DAY_' + str(day)
    catList = ['lightSound', 'food', 'others']
    if not item_cat in catList:
      abort(400, message='item cat not found')
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    estimateEntry = {}
    for i in itemList:
      if itemList[i]['item_cat'] == item_cat:
        flag = 0
        if eventID in costEstList:
          if day in costEstList[eventID]:
            if i in costEstList[eventID][day]:
              flag = 1
              estimateEntry[i] = itemList[i]
              estimateEntry[i]['qty'] = costEstList[eventID][day][i]
        if flag == 0:
          estimateEntry[i] = itemList[i]
          estimateEntry[i]['qty'] = ''
    if dayName in eventDetails:
      date = eventDetails[dayName]
    else:
      date = ''
    finalEstimateEntry = { 'estimateEntry' : estimateEntry, 'date' : date}
    return finalEstimateEntry

class SubmitEstimate(Resource):
  def post(self):
    args = submitEstimateParser.parse_args()
    eventID = args['eventID'].upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    if not eventID in costEstList:
      abort(400, message='estimate not prepared')
    else:
      costEst = costEstList[eventID]
    flag = 0
    for i in range(1, int(eventDetails['event_duration']) + 1):
      if not ('DAY_' + str(i)) in costEst:
        flag = 1
        break
    if flag == 1:
      abort(400, message='event not completed')
    elif flag == 0:
      eventList[eventID]['status'] = 'created'
      db.child('EventManagementSystem').child('eventList').set(eventList)
    return eventList[eventID]

class GrantDiscount(Resource):
  def post(self):
    args = grantDiscountParser.parse_args()
    eventID = args['eventID'].upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    if not eventID in costEstList:
      abort(400, message='estimate not prepared')
    else:
      if not eventList[eventID]['status'] == 'requested':
        eventList[eventID]['discountAmount'] = args['discountAmount']
        db.child('EventManagementSystem').child('eventList').set(eventList)
      else:
        abort(400, message='estimate not created')
    return eventList[eventID]

class VerifyCostEstimate(Resource):
  def post(self):
    args = verifyEstimateParser.parse_args()
    eventID = args['eventID'].upper()
    verifiedEstimate = {}
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
      if eventDetails['status'] != 'created':
        abort(400, message='estimate not forwarded')
    costEstList = db.child('EventManagementSystem').child('costEstimationList').get().val()
    if costEstList == None:
      costEstList = {}
    itemList = db.child('EventManagementSystem').child('itemList').get().val()
    if itemList == None:
      itemList = {}
    if not eventID in costEstList:
      abort(400, message='estimate not prepared')
    else:
      costEst = costEstList[eventID]
    flag = 0
    for i in range(1, int(eventDetails['event_duration']) + 1):
      if not ('DAY_' + str(i)) in costEst:
        flag = 1
        break
    if flag == 1:
      abort(400, message='event not completed')
    elif flag == 0:
      for i in costEst:
        for j in costEst[i]:
          if not i in verifiedEstimate:
            verifiedEstimate[i] = { j : {'qty' : costEst[i][j], 'price' : itemList[j]['item_price'], 'totalCost' : (int(costEst[i][j]) * int(itemList[j]['item_price'])) } }
          else:
            verifiedEstimate[i][j] = { 'qty' : costEst[i][j], 'price' : itemList[j]['item_price'], 'totalCost' : (int(costEst[i][j]) * int(itemList[j]['item_price'])) }
      verifiedCostEst = db.child('EventManagementSystem').child('verifiiedCostEst').get().val()
      if verifiedCostEst == None:
        verifiedCostEst = {}
      verifiedCostEst[eventID] = verifiedEstimate
      db.child('EventManagementSystem').child('verifiiedCostEst').set(verifiedCostEst)
      eventList[eventID]['status'] = 'verified'
      eventList[eventID]['acceptFlag'] = 2
      db.child('EventManagementSystem').child('eventList').set(eventList)
    return eventList[eventID]

class ReviewEstimate(Resource):
  def post(self):
    args = reviewEstimateParser.parse_args()
    eventID = args['eventID'].upper()
    eventList = db.child('EventManagementSystem').child('eventList').get().val()
    if eventList == None:
      eventList = {}
    if not eventID in eventList:
      abort(400, message='event not found')
    else:
      eventDetails = eventList[eventID]
      if eventDetails['status'] != 'verified':
        abort(400, message='estimate not verified')
    if args['action'] == 'accept':
      eventList[eventID]['acceptFlag'] = 1
    elif args['action'] == 'reject':
      eventList[eventID]['acceptFlag'] = 0
    db.child('EventManagementSystem').child('eventList').set(eventList)
    return eventList[eventID]
     
api.add_resource(AdminLogin, '/adminLogin')
api.add_resource(ManagerLogin, '/managerLogin')
api.add_resource(ClientReg, '/client')
api.add_resource(ClientUpdate, '/client/<clientID>')
api.add_resource(ClientLogin, '/clientLogin')
api.add_resource(Message, '/message')
api.add_resource(MessageInbox, '/message/<clientID>')
api.add_resource(ItemReg, '/item')
api.add_resource(ItemList, '/itemList/<cat>')
api.add_resource(ItemUpdate, '/item/<itemID>')
api.add_resource(CostEstimationRequest, '/costEstReq')
api.add_resource(EventList, '/eventList/<cat>')
api.add_resource(ClientEventList, '/clientEventList/<clientID>')
api.add_resource(EventUpdate, '/event/<eventID>')
api.add_resource(CostEstimationCreate, '/costEstCreate')
api.add_resource(DayEstimationReport, '/dayEst/<eventID>')
api.add_resource(DayEstimationReportVer, '/dayEstVer/<eventID>')
api.add_resource(EstimationReport, '/costEst/<eventID>/<day>')
api.add_resource(EstimationReportVer, '/costEstVer/<eventID>/<day>')
api.add_resource(EstimateEntryDetails, '/estEntryDetails/<eventID>/<day>/<item_cat>')
api.add_resource(SubmitEstimate, '/submitEst')
api.add_resource(GrantDiscount, '/grantDiscount')
api.add_resource(VerifyCostEstimate, '/verifyEstimate')
api.add_resource(ReviewEstimate, '/reviewEstimate')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port='8000')