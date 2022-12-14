from flask import Flask, request, render_template, redirect, session,flash
import json
from db import init_app, query_db

app = Flask(__name__)
app.debug = True
app.secret_key = 'av6sv7wwrnwr26f8a8g8g28742y4f'

init_app(app)

whiltelist = ["/static", "/api", "/login", "/user/registry", "/car/registry"]

@app.before_request#웹이 실행되고 의도한 화면이 나오기전에 처리해야할 요청들
def require_authorization():
    if any(filter(lambda x:request.path.startswith(x), whiltelist)) or ('username' in session):
        print("PASS")
        pass
    else:
        print("REDIRECT", request.path, whiltelist)
        return redirect('/login')#첫 웹사이트 입장시 보여줄 화면을 결정

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/login', methods=["POST"])
def api_login():
    uid = request.form['id']
    pw = request.form['password']

    data = query_db("SELECT guard.id, guard.name, guard.aid, apartment.name as aname FROM guard, apartment WHERE guard.aid=apartment.id AND guard.id=? AND guard.password=?",
                    args=(uid, pw), one=True,
                    commit=True)
    print(data)
    return f"{data['id']},{data['name']},{data['aid']},{data['aname']}"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login?logout')

@app.route('/login.do', methods=["POST"])
def login_do():

    uid = request.form['id']
    pw = request.form['password']
    print(uid, pw)
    if(uid=='admin'and pw=='1234'):
        session['username'] = uid
        return redirect('/users')
    elif(uid!='admin'):
        flash("올바르지 않은 아이디 입니다.")
        return redirect('/login?fail')
    else:
        flash("올바르지 않은 비밀번호 입니다.")
        return redirect('/login?fail')


@app.route('/car/registry')
def car_registry():
    data = query_db("""SELECT * FROM apartment""")
    data2=query_db("""SELECT * FROM user """)
    return render_template('car_registry.html', apartments=data,user=data2)

###pop up or page 

###pop up or page 

###pop up or page 

###pop up or page 

###pop up or page 

@app.route('/car/registry.do', methods=["POST"])
def car_registry_do():
    name = request.form['name']
    phone = request.form['phone']
    aid = request.form['aid']
    plate = request.form['plate']
    data = query_db("INSERT INTO car (plate, uid) select ?, id FROM user WHERE name=? AND phone=? AND aid=?",
                    args=(plate, name, phone, aid),
                    commit=True)
    #namelist=query_db(f"SELECT id from user where name=?",args=(name))
    
    #if ({namelist['id']}==None):
        #flash("일치하는 입주자명이 존재하지 않습니다.")
        #return redirect('/car/registry')

    return redirect('/cars')

@app.route('/api/car/<plate>')
def get_car(plate):
    data = query_db(f"SELECT apartment.name as aname, user.address, plate, user.name, car.permit, car.updated FROM car, user, apartment WHERE car.uid=user.id AND apartment.id=user.aid AND plate=?",
                    args=(plate.strip().replace(" ", ""),), one=True)
    if(data==None):
        return "notfound"
    out = f"{data['name']},{data['aname']},{data['address']},{data['plate']},{data['permit']},{data['updated']}"
    return out

@app.route('/car/<plate>/permit')
def car_permit(plate):
    data = query_db("UPDATE car SET permit='Y' WHERE plate=?",
                    args=(plate,), one=True, commit=True)
    return redirect("/cars")

@app.route('/car/<plate>/deny')
def car_deny(plate):
    data = query_db("DELETE FROM car WHERE plate=?",
                    args=(plate,), one=True, commit=True)#tuple을 제거
    return redirect("/cars")

@app.route('/car/<plate>/revert')
def car_revert(plate):
    data = query_db("UPDATE car SET permit='N' WHERE plate=?",
                    args=(plate,), one=True, commit=True)
    return redirect("/cars")

@app.route('/')
@app.route('/users')
def get_all_user():
    data = query_db("""SELECT apartment.name as apartment, user.*, COUNT(car.plate) as count_car
                       FROM apartment, user LEFT OUTER JOIN car 
                       ON car.uid=user.id
                       WHERE apartment.id = user.aid
                       GROUP BY user.id""")
    return render_template('users.html', users=data)

@app.route('/user/registry.do', methods=['POST'])
def user_registry_do():
    name = request.form['name']
    aid = request.form['aid']
    address = request.form['address']
    phone = request.form['phone']
    data = query_db("insert into user (name, aid, address, phone) values (?,?,?,?)",
                    args=(name, aid, address, phone),
                    commit=True)
    return redirect('/users')

@app.route('/user/registry')
def user_registry():
    apts = query_db("SELECT * FROM apartment")
    return render_template('user_registry.html', apartments=apts)

@app.route('/user/<uid>')
def user_info(uid):
    data = query_db("""SELECT apartment.name as apartment, user.*, COUNT(car.plate) as count_car
                       FROM apartment, user LEFT OUTER JOIN car 
                       ON car.uid=user.id
                       WHERE apartment.id = user.aid
                       AND user.id=?
                       GROUP BY user.id""", args=(uid,), one=True)
    apts = query_db("SELECT * FROM apartment")
    return render_template('user_info.html', user=data, apartments=apts)

@app.route('/user/<uid>/permit')
def user_permit(uid):
    data = query_db("UPDATE user SET permit='Y' WHERE id=?",
                    args=(uid,), one=True, commit=True)
    return redirect("/users")

@app.route('/user/<uid>/deny')
def user_deny(uid):
    data = query_db("DELETE FROM user WHERE id=?",
                    args=(uid,), one=True, commit=True)
    return redirect("/users")

@app.route('/user/<uid>/revert')
def user_revert(uid):
    data = query_db("UPDATE user set permit='N' WHERE id=?",
                    args=(uid,), one=True, commit=True)
    return redirect("/users")


@app.route('/user/<uid>/update', methods=['POST'])
def user_update(uid):
    name = request.form['name']
    aid = request.form['aid']
    address = request.form['address']
    phone = request.form['phone']
    permit = request.form['permit']
    data = query_db("UPDATE user SET name=?, aid=?, address=?, phone=?, permit=? WHERE id=?",
                    args=(name, aid, address, phone, permit, uid),
                    commit=True)
    return redirect('/users')

@app.route('/guards')
def get_all_gurad():
    data = query_db("""SELECT apartment.name as apartment, guard.*
                       FROM apartment, guard
                       WHERE apartment.id = guard.aid""")
    return render_template('guards.html', guards=data)

@app.route('/guard/<gid>')
def guard_info(gid):
    data = query_db("""SELECT apartment.name as apartment, guard.*
                       FROM apartment, guard
                       WHERE apartment.id = guard.aid
                       AND guard.id=?""", args=(gid,), one=True)
    apts = query_db("SELECT * FROM apartment")
    return render_template('guard_info.html', guard=data, apartments=apts)

@app.route('/guard/registry')
def guard_registry():
    data = query_db("""SELECT * FROM apartment""")
    return render_template('guard_registry.html', apartments=data)



@app.route('/guard/registry.do', methods=['POST'])
def guard_registry_do():
    gid = request.form['id']
    password = request.form['password']
    name = request.form['name']
    aid = request.form['aid']
    phone = request.form['phone']
    data = query_db("INSERT INTO guard (id,name, password, aid, phone) values (?,?,?,?,?)",
                    args=(gid, name, password, aid, phone),
                    commit=True)
    return redirect('/guards')

@app.route('/guard/<gid>/update', methods=['POST'])
def guard_update(gid):
    password = request.form['password']
    name = request.form['name']
    aid = request.form['aid']
    phone = request.form['phone']
    data = query_db("UPDATE guard SET name=?, password=?, aid=?, phone=? WHERE id=?",
                    args=(name, password, aid, phone, gid),
                    commit=True)
    return redirect('/guards')


@app.route('/cars')
def get_all_car():
    data = query_db("""SELECT apartment.name as aname, car.*, user.name
                       FROM apartment, user, car
                       WHERE apartment.id = user.aid
                       AND car.uid = user.id""")
    data2 = query_db("""SELECT * FROM user""")
    return render_template('cars.html', cars=data, users=data2)


@app.route('/user_car/registry')
def user_car_registry():
    apts = query_db("SELECT * FROM apartment")
    return render_template('user_car_registry.html', apartments=apts)


@app.route('/user_car/registry.do', methods=['POST'])
def user_car_registry_do():
    name = request.form['name']
    aid = request.form['aid']
    address = request.form['address']
    phone = request.form['phone']
    plate = request.form['plate']
    
    data2 = query_db("insert into user (name, aid, address, phone) values (?,?,?,?)",args=(name, aid, address, phone),commit=True)

    data = query_db("INSERT INTO car (plate, uid) select ?, id FROM user WHERE name=? AND phone=? AND aid=?",
                    args=(plate, name, phone, aid),
                    commit=True)
    return redirect('/cars')



@app.route('/selectone')
def selectone():

    return render_template('selectone.html')






@app.route('/apartment/add')
def add_apt():
    #TODO
    pass

@app.route('/car/add')
def add_car():
    #TODO
    pass

@app.route('/apartments')
def get_all_apt():
    data = query_db('SELECT * FROM apartment')
    out = ""
    for d in data:
        out += str(d) +"<br/>"
    return out

if __name__ == '__main__':
    app.run()
