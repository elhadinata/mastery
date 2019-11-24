# mastery

Flask deploy doc


put git file in a new dirc

open terminal to that new dirc

make sure you are using python3.7（apt-get install python3.7）

run: pipenv shell     [go to vir-mode]
run:  pipenv install  [auto install dependency -same as my pc]

you may need to run [pipenv install pyjwt] if the flask raise some error about jwt

run: export FLASK_APP=start.py

run: flask run


test step:
open your chrome to 127.0.0.1:5000   you can see swagger doc

then you need to open your [Advanced REST client] -- Download from google 

do  ->  [POST] localhost:5000/login
    ->  add header name = Authorization  ->header value: [click right side pencil icon] then put username: ricky  password: 12345  click accept
    -> then click to send, it will return you a token [only for 1 hour]

once you got token, you can goto swagger page, put the token string for search,
that function will actually return whatever you send to server with an unique user_id

if the token is wrong, you will get an error from that response

++++++++++++++++
I also write a simple page for graph test, which not need token for now, 
you can directly go to page:  127.0.0.1:5000/search    to see the result
++++++++++++++++

for other function, I am not sure it's necessary, if your are interest, you can use 
[Advanced REST client] try yourself. Don't forget add the [header name: api-token  header value: token string you get from previous step] to pass the authorization



=============================
following step for first create sqlite db
if there is a file called 9321.db then following step is not necessary
python3 from app import db
>>>db.create_all()



+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# mastery-frontend
1. Clone repo
2. Go inside the repo
3. Run: npm install
4. Run: live-server
5. install this chrome plugin https://mybrowseraddon.com/access-control-allow-origin.html
6. Activate the plugin to allow CORS
7. Ready