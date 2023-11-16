from flask import render_template, request, url_for
from werkzeug.utils import redirect, secure_filename
from bs4 import BeautifulSoup
import requests
from app.__init__ import app, db
from app.models import User, Post
import uuid as uuid
import os

@app.route('/')
def welcome():
    return render_template("welcome.html")

# webscrape information from osu off campus housing website and store them into the database
@app.route('/load')
def load():
    url = "https://offcampus.osu.edu/search-housing.aspx?page=0&pricefrom=0&sort=1&alllandlords=0"
    r = requests.get(url)
    s = BeautifulSoup(r.content, 'html.parser')
    pages = s.find(class_="c-paging")
    page = pages.find_all('li')
    max_page = page[len(page) - 2].get_text()
    max_page = int(max_page)

    for page_number in range(max_page): # please change the range if the data takes too long to scrape due to the amount
        url = "https://offcampus.osu.edu/search-housing.aspx?page=" + str(
                page_number) + "&pricefrom=0&sort=1&alllandlords=0"
        r = requests.get(url)
        s = BeautifulSoup(r.content, 'html.parser')
        result = s.find(class_="o-row o-row--flex o-row--gutter u-margin-top-sm")
        houses = result.find_all(class_="o-row__col o-row__col--6of12@md o-row__col--4of12@xl")
        for i in range(len(houses)):
            house = houses[i].find(class_="c-propertycard__info")
            house_address = house.find('h2').get_text().strip()
            content = house.find_all('dd')
            rent = content[0].get_text().strip()
            bedroom = content[1].get_text().strip()
            bathroom = content[2].get_text().strip()
            amenities = content[3].get_text().strip()
            a_tags = house.find_all('a')
            detail = a_tags[1]['href']
            detail_url = "https://offcampus.osu.edu" + detail
            # add new house post in the database
            if (Post.query.filter_by(address=house_address).first()) is None:
                post=Post(
                    address=house_address,
                    rent=rent,
                    bedroom=bedroom,
                    bathroom=bathroom,
                    detail_url=detail_url,
                    amenities=amenities,
                    liked="",
                    type="housing post")
                db.session.add(post)
    db.session.commit()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['name']
        password = request.form['password']
        #check if the password is correct
        if User.query.filter_by(name=username).first():
            user=User.query.filter_by(name=username).first()
            if user.password==password:
                return redirect(url_for('main', name=username, index="0", type="housing post", bedroom="0", bathroom="0", upper="0", lower="0"))
            else:
                return render_template('login.html')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        pic = request.files['img']
        filename = secure_filename(pic.filename)
        # construct pic name
        picname = str(uuid.uuid1()) + "_" + filename
        # save pic name to the directory
        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], picname))
        # add new users to the database
        user = User(
            name=request.form['name'],
            fullname=request.form['fullname'],
            password=request.form['password'],
            email=request.form['email'],
            bio=request.form['bio'],
            liked="",
            pic_address=picname,
            post_address=""
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route('/edit_profile/<name>', methods=['POST', 'GET'])
def edit_profile(name):
    if request.method == 'POST':
        user=User.query.filter_by(name=name).first()
        name=request.form['name']
        if name != 'no change':
            user.name=name
        fullname = request.form['fullname']
        if fullname != 'no change':
            user.fullname = fullname
        password = request.form['password']
        if password != 'no change':
            user.password = password
        email = request.form['email']
        if email != 'no change':
            user.email = email
        bio = request.form['bio']
        if bio != 'no change':
            user.bio = bio
        name=user.name
        db.session.commit()
        return redirect(url_for('profile', name=name))
    else:
        return render_template('edit_profile.html')


@app.route('/main/<name>/<index>/<type>/<bedroom>/<bathroom>/<upper>/<lower>', methods=["GET", "POST"])
def main(name, index, type, bedroom, bathroom, upper, lower):
    if request.method == 'POST':
        type=request.form['type']
        bedroom=request.form['bedrooms']
        bathroom=request.form['bathrooms']
        upper = request.form['upper_rent']
        lower = request.form['lower_rent']
        return redirect(url_for('main', name=name, index=index, type=type, bedroom=bedroom, bathroom=bathroom, upper=upper, lower=lower))
    else:
        if type=="sublease":
            post = Post.query.filter_by(type="sublease").all()
        else:
            post = Post.query.filter_by(type="housing post").all()
        rent=[]
        bedrooms=[]
        bathrooms=[]
        address=[]
        amenities=[]
        detail_url=[]
        #to know where to start
        index=int(index)
        #track the amount, only 12 for one page
        amount=0
        #filter
        for house in post[index:]:
            if amount <12:
                num_bathroom=get_number(house.bathroom)
                num_bedroom=get_number(house.bedroom)
                price=get_price(house.rent)
                if num_bathroom==int(bathroom) or int(bathroom)==0 :
                    if num_bedroom==int(bedroom) or int(bedroom)==0 :
                        if len(price) ==1 and int(lower)<=int(price[0]) and (int(upper)>=int(price[0]) or int(upper)==0):
                            rent.append(house.rent)
                            bedrooms.append(house.bedroom)
                            bathrooms.append(house.bathroom)
                            address.append(house.address)
                            amenities.append(house.amenities)
                            detail_url.append(house.detail_url)
                            amount+=1
                            index+=1
                        elif (int(upper)>=int(price[1]) or int(upper)==0) and (int(lower)>=int(price[0]) or int(lower)==0):
                            rent.append(house.rent)
                            bedrooms.append(house.bedroom)
                            bathrooms.append(house.bathroom)
                            address.append(house.address)
                            amenities.append(house.amenities)
                            detail_url.append(house.detail_url)
                            amount += 1
                            index += 1
            else:
                break
        return render_template('main.html', rent=rent, bedrooms=bedrooms, bathrooms=bathrooms, address=address, amenities=amenities, detail_url=detail_url, name=name, amount=amount, bathroom=bathroom, bedroom=bedroom, type=type, index=index, upper=upper, lower=lower)

@app.route('/profile/<name>')
def profile(name):
    rent = []
    bedroom = []
    bathroom = []
    amenities = []
    detail_url = []
    addresses=[]

    # get own posts
    user=User.query.filter_by(name=name).first()
    own_post=user.post_address
    own_post=own_post.split(";;")
    own_post=own_post[1:]
    length1=len(own_post)
    if length1 >0:
        for address in own_post:
            if Post.query.filter_by(address=address).first():
                addresses.append(address)
                liked_post=Post.query.filter_by(address=address).first()
                rent.append(liked_post.rent)
                bedroom.append(liked_post.bedroom)
                bathroom.append(liked_post.bathroom)
                amenities.append(liked_post.amenities)
                detail_url.append(liked_post.detail_url)

    # get liked posts
    liked_addresses = user.liked
    liked_addresses = liked_addresses[:-2].split(";;")
    # delete duplicates
    liked_addresses=set(liked_addresses)
    length2 = len(liked_addresses)
    if length2 >0:
        for address in liked_addresses:
            if Post.query.filter_by(address=address).first():
                addresses.append(address)
                liked_post=Post.query.filter_by(address=address).first()
                rent.append(liked_post.rent)
                bedroom.append(liked_post.bedroom)
                bathroom.append(liked_post.bathroom)
                amenities.append(liked_post.amenities)
                detail_url.append(liked_post.detail_url)

    # get user's profile pic
    url="images/"+user.pic_address

    return render_template('profile.html', user=user, post=post, rent=rent, bedroom=bedroom, bathroom=bathroom, addresses=addresses, amenities=amenities, detail_url=detail_url, length2=length2, url=url, length1=length1)

@app.route("/delete_post/<name>/<address>", methods=['POST'])
def delete_post(name,address):
    post = Post.query.filter_by(address=address).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("profile", name=name))

@app.route("/delete_liked/<name>/<address>", methods=['POST'])
def delete_liked(name,address):
    # delete liked username in post database
    post = Post.query.filter_by(address=address).first()
    liked_users=post.liked
    liked_users=liked_users.replace(name+";;","")
    post.liked=liked_users
    db.session.commit()

    # delete liked address in user database
    user = User.query.filter_by(name=name).first()
    liked_addresses=user.liked
    liked_addresses=liked_addresses.replace(address+";;","")
    user.liked=liked_addresses
    db.session.commit()
    return redirect(url_for("profile", name=name))

@app.route('/post/<name>', methods=["GET", "POST"])
def post(name):
    if request.method=="POST":
        # first pic
        pic = request.files['img']
        filename = secure_filename(pic.filename)
        # construct pic name
        picname = str(uuid.uuid1()) + "_" + filename
        # save pic name to the directory
        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], picname))
        # second pic
        pic2 = request.files['img2']
        filename = secure_filename(pic2.filename)
        picname2 = str(uuid.uuid1()) + "_" + filename
        pic2.save(os.path.join(app.config['UPLOAD_FOLDER'], picname2))
        # third pic
        pic3 = request.files['img3']
        filename = secure_filename(pic3.filename)
        picname3 = str(uuid.uuid1()) + "_" + filename
        pic3.save(os.path.join(app.config['UPLOAD_FOLDER'], picname3))
        # fourth pic
        pic4 = request.files['img4']
        filename = secure_filename(pic4.filename)
        picname4 = str(uuid.uuid1()) + "_" + filename
        pic4.save(os.path.join(app.config['UPLOAD_FOLDER'], picname4))
        # fifth pic
        pic5 = request.files['img5']
        filename = secure_filename(pic5.filename)
        picname5 = str(uuid.uuid1()) + "_" + filename
        pic5.save(os.path.join(app.config['UPLOAD_FOLDER'], picname5))

        upper = request.form['upper_rent']
        lower = request.form['lower_rent']
        new_address=request.form['address']
        
        # add new posts to the database
        post=Post(
            type=request.form['post_type'],
            address=new_address,
            rent="$"+lower+".00"+" - "+"$"+upper+".00",
            amenities=request.form['amenities'],
            bedroom=request.form['bedrooms'],
            bathroom=request.form['bathrooms'],
            info=request.form['info'],
            detail_url="/newPost/"+request.form['address'],
            pic_address=picname+";;"+picname2+";;"+picname3+";;"+picname4+";;"+picname5
        )
        db.session.add(post)
        db.session.commit()

        user=User.query.filter_by(name=name).first()
        address=user.post_address
        address=address+";;"+new_address
        user.post_address=address
        db.session.commit()
        return redirect(url_for('newPost', address=new_address))
    else:
        return render_template('post.html')
@app.route('/edit_post/<address>', methods=['POST', 'GET'])
def edit_post(address):
    if request.method == 'POST':
        post = Post.query.filter_by(address=address).first()
        post.type=request.form['post_type']
        address=request.form['address']
        if address != 'no change':
            post.address=address
            post.detail_url = "/newPost/" + address
        amenities = request.form['amenities']
        if amenities != 'no change':
            post.amenities = amenities
        bedroom = request.form['bedrooms']
        if bedroom != 'no change':
            post.bedroom = bedroom
        bathroom = request.form['bathrooms']
        if bathroom != 'no change':
            post.bathroom = bathroom
        info = request.form['info']
        if info != 'no change':
            post.info = info
        upper = request.form['upper_rent']
        if upper != 'no change':
            past_rent = get_price(post.rent)
            post.rent = "$" + past_rent[0] + ".00" + " - " + "$" + upper + ".00"
        lower = request.form['lower_rent']
        if lower != 'no change':
            past_rent = get_price(post.rent)
            post.rent = "$" + lower + ".00" + " - " + "$" + past_rent[1] + ".00"
        address=post.address
        db.session.commit()
        return redirect(url_for('newPost', address=address))
    else:
        return render_template('edit_post.html', address=address)

@app.route('/newPost/<address>')
def newPost(address):
    post = Post.query.filter_by(address=address).first()
    addresses=post.pic_address
    addresses=addresses.split(";;")
    pic1 = "images/"+addresses[0]
    pic2 = "images/"+addresses[1]
    pic3 = "images/"+addresses[2]
    pic4 = "images/"+addresses[3]
    pic5 = "images/"+addresses[4]
    return render_template('newPost.html', post=post, pic1=pic1, pic2=pic2, pic3=pic3, pic4=pic4, pic5=pic5)

@app.route("/like/<address>/<name>", methods=["POST"])
def like(address, name):
    #add new address to the user's liked address list
    user=User.query.filter_by(name=name).first()
    like_list=user.liked
    like_list=like_list+address+";;"
    user.liked=like_list
    db.session.commit()
    #add new username to the address's liked user list
    post = Post.query.filter_by(address=address).first()
    like_list = post.liked
    like_list = like_list + name + ";;"
    post.liked = like_list
    db.session.commit()
    return redirect(url_for("view_like", address=post.address))

@app.route("/view_like/<address>")
def view_like(address):
    post = Post.query.filter_by(address=address).first()
    like_users=post.liked
    like_users=like_users[:-2].split(";;")
    like_users=set(like_users)
    return render_template("like.html", post=post, like_users=like_users)

def get_number(string):
    total=0
    for word in string.split():
        if word.isdigit():
            total=total+int(word)
    return total

def get_price(string):
    num=[]
    for word in string.split():
        word=word.replace(",", "")
        word=word[1:-3]
        if word.isdigit():
            num.append(word)
    return num

with app.app_context():
    db.create_all()
