
import json
import os
from flask import Flask
from flask import request
from aog import conv
from flask import make_response



# Flask app should start in global layout
app = Flask(__name__)



@app.route('/', methods=['POST'])
def fullfillment():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeFullfillment(req)
    res = json.dumps(res, indent=4)
    #print(res)
    final = make_response(res)
    final.headers['Content-Type'] = 'application/json'
    return final

def makeFullfillment(req):
  
  #isfrom function is used to check from which dialogflow intent request came from.
  if conv.isfrom(req,'ask_intent'): 
    # ask method expect a reply from user. after the message mic will be open for user to reply.
    res=conv.ask("You made me ask this","You made me print this")
    return res

  
  # F I N A L  R E S P O N S E
  if conv.isfrom(req,'final response'):
    
    # Close is for terminating the conversation with a message.
    res=conv.close('Closing')
    return res

  # Getting parameter (Entity) from the intent 
  if conv.isfrom(req,'entities'):
    entity=conv.get_parameters(req,'color') # Color is the value of the entity as seen in the dialogflow. 
    res=conv.ask("Your favourite colour is {}".format(entity))
    return res



  # B A S I C  C A R D  
  if conv.isfrom(req,'basic card'):

    # parameters=(speech,title,formatted_text,subtitle,card_image,image_scale,image_text,link_title,link_url,response)
    # Required parameters = speech and either formatted_text or card_image  
    # Button requires both link_url and link_title
    url="https://developers.google.com/actions/assistant.png"
    if conv.has_capability(req,'actions.capability.SCREEN_OUTPUT'): # Checking device has screen or not 
      res=conv.basic_card(formatted_text="Content in the basic card",speech="You made me say this",\
                        title="Title of the Card",subtitle="subtitle",card_image=url,link_title="Link Title",link_url=url,image_scale="CROPPED")
    else:
      res=conv.ask("You dont have screen capability")
    return res



  # L I S T  
  if conv.isfrom(req,'list'):
    
    # parameters (speech,title,items) *items is a list of dictionaries 
    # parameters in each item : title,description,image_url,image_text,key,synonyms
    # when user click on a list item, an other intent with the event 'actions_intent_OPTION' will be invoked.
    # it won't be created automatically.
    # from this intent you can check which item is user selected.  
    url="https://developers.google.com/actions/assistant.png"
    res=conv.list(speech="this is a list",title="List title",items=[{'title':"item title",'description':'item description','image_url':url,\
    'image_text':'image here','key':'your_key','synonyms':['one1','two1']},\
    {'title':"item title1",'description':'item description1','image_url':url,\
    'image_text':'image here1','key':'your_key1','synonyms':['one2','two2']},\
    {'title':"item title2",'description':'item description1','image_url':url,\
    'image_text':'image here1','key':'your_key2','synonyms':['one3','two3']}])
    return res

  # TO GET SELECTED ITEM'S KEY IN LIST
  if conv.isfrom(req,'option reciever'):
    #When user clicks on an list item, this intent will be invoked
    key=conv.list_item_selectd(req) # Function for getting key of the seelcted item
    res=conv.ask("An item with key {} selected".format(key))
    return res


  # P E R M I S S I O N S 
  if conv.isfrom(req,'permissions'):
    # Choose one or more supported permissions to request:
    # NAME, DEVICE_PRECISE_LOCATION, DEVICE_COARSE_LOCATION
    # Parameters : permissions(it's a list so you can request one or all three of these permissions at a time)
    # context(optional explaination for the permission) 
    # After getting use response, permission intent will invoke the intent with event 'actions_intent_PERMISSION'
    # it won't be created automatically.
    res=conv.ask_permission(['NAME','DEVICE_PRECISE_LOCATION','DEVICE_COARSE_LOCATION'],context="To get you know better")
    return res


  # PERMISSION FOLLOWUP
  if conv.isfrom(req,'permission followup'):
    if conv.permission_granted(req):
      name=conv.get_username(req) # return type is a dictionary contains {displayName,givenName,familyName}
      location=conv.get_userlocation(req) # return type is a dictionary contains {latitude,longitude}
      res=conv.ask(speech="Hi, {}".format(name['displayName']),displayText="Your location is {},\
        {}".format(location['latitude'],location['longitude']))
      return res

    return res


  # ASKING DATE AND TIME
  if conv.isfrom(req,'date time'):
    # These optional dialogues for dates and time will be used if user didnt specify date and time.
    # After user provide date and time intent with event actions_intent_DATETIME will be invoked
    # you have to create that event manually.
    res=conv.ask_datetime(\
      initial="When do you want to come in?",\
      date="What day was that?",\
      time="What time"
      )
    return res


  # GETTING RESULTS OF ASKING DATE TIME 
  if conv.isfrom(req,'date time followup'):
    date,time=conv.get_datetime(req) #date dictionary= {'year','date','month'} ,time dictionary ={hours and time}
    res=conv.ask(speech="Date and time is ",displayText='Year : {} Month : {} Day {}, Hours ; {} Time : {}'.format\
      (date.get('year','0'),date.get('month','0'),date.get('day','0'),time.get('hours','0'),time.get('minutes','0')))
    return res


  if conv.isfrom(req,'carousels'):
    url="https://developers.google.com/actions/assistant.png"
    res=conv.carousels(speech="Carousels",title="List title",items=[{'title':"item title",'description':'item description','image_url':url,\
    'image_text':'image here','key':'your_key','synonyms':['one1','two1']},\
    {'title':"item title1",'description':'item description1','image_url':url,\
    'image_text':'image here1','key':'your_key1','synonyms':['one2','two2']},\
    {'title':"item title2",'description':'item description1','image_url':url,\
    'image_text':'image here1','key':'your_key2','synonyms':['one3','two3']}])
    return res


  # SUGGESTION CHIPS
  if conv.isfrom(req,'suggestion chips'):
    res=conv.suggestion_chips(speech="Here are some suggestions for you.",suggestions=['suggestion1','suggestion2','suggestion3'])
    return res

  # CONFIRMATION
  if conv.isfrom(req,'confirmation'):
    # Ask a generic confirmation from the user (yes/no question) 
    # Users reply to this confirmation will invoke intent with event actiont
    res=conv.ask_confirmation("Do you like python ?")
    return res

  if conv.isfrom(req,'confirmation followup'):
    # Function to get users reply to the confirmation (Boolean value) 
    data=conv.get_confirmation(req) 
    if data:
      res=conv.ask("You like python")
    else:
      res=conv.ask("You dont like python")
    return res
  
  if conv.isfrom(req,'user last seen'):
    # Function to get user's last seen on this app.
    last_seen=conv.get_lastseen(req) 
    if last_seen is None: # User is using app for the first time.
      res=conv.ask("Welcome to python demo app")
    else:
      res=conv.ask(speech="Welcome back user, your last seen is ",displayText="last seen :{}".format(last_seen))
    return res
    
  if conv.isfrom(req,'get user id'):
    # Function to get user id. You can use it for identifying user.
    user_id=conv.get_userid(req) 
    res=conv.ask(speech="User id is,",displayText=("User ID :{}".format(user_id)))
    return res


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    app.run(debug=True, port=port, host='0.0.0.0')