from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_pymongo import PyMongo
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
# from PIL import Image
from bson import ObjectId
# from bson.binary import Binary
#import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkeythisis'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/pymogo_user'
mongo = PyMongo(app)

user_collection = mongo.db.users

class GetImageForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstName =StringField('FirstName',validators=[DataRequired()])
    lastName =StringField('LastName',validators=[DataRequired()])
    image = FileField('Image', validators=[])

class ShowImageForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])

class UpdateImageForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    image = FileField('Image', validators=[])

@app.route('/', methods=['GET', 'POST'])
def get_image():
    form = GetImageForm()
    if form.validate_on_submit():
        image = form.image.data
        mongo.save_file(image.filename, image)

        # ====================================================================================================
        # I WAS TRYING TO RESIZE USER'S IMAGE AS IT MAY CONSUME SO MUCH SPAVE IN THE DB. IT DIDN'T GO SO WELL
        # i = Image.open(image)
        # fn, fe = os.path.splitext(image.filename)
        # size_i = (300, 300)
        # i.thumbnail(size_i)
        # i.save('300/{}_300{}'.format(fn, fe))

        # with open(f'F:/MINDFUL/FLASK/Imaging Image/300/{fn}_300{fe}', 'rb') as file:
        #     encoded = Binary(file.read())

        # file_id = mongo.db.fs.files.find_one_or_404({'filename': image.filename}).get('_id')
        # mongo.db.fs.chunks.update_one({'files_id': ObjectId(file_id)}, {
        #     '$set': {
        #         'data': encoded
        #     }
        # })
        # ====================================================================================================

        user_collection.insert_one({
            'username': form.username.data,
            'firstName': form.firstName.data,
            'lastName':form.lastName.data,
            'image': image.filename
        })
        return redirect(url_for('show_image_form'))
    return render_template('get_image.html', form = form)

@app.route('/image/<img>')
def image(img):
    return mongo.send_file(img)

@app.route('/show-image-form', methods=['GET', 'POST'])
def show_image_form():
    form = ShowImageForm()
    if form.validate_on_submit():
        user_id = user_collection.find_one_or_404({'username': form.username.data}).get('_id')
        return redirect(url_for('show_image', user_id = user_id))
    return render_template('show_image_form.html', form = form)

@app.route('/update-image-form', methods=['GET', 'POST'])
def update_image():
    form = UpdateImageForm()
    if form.validate_on_submit():
        user = user_collection.find_one_or_404({'username': form.username.data})
        image_file = form.image.data
        user_id = user.get('_id')
        user_image = user.get('image') #THIS GIVES THE NAME OF USER'S IMAGE

        # I COULDN'T FIGURE OUT HOW TO UPDATE THE BINARY DATA
        # SO EVERYTIME A USER UPDATES HIS/HER IMAGE I'D DELETE THE PREVIOUS IMAGE AND STORE THE NEW ONE
        image_id = mongo.db.fs.files.find_one_or_404({'filename': user_image}).get('_id')
        mongo.db.fs.chunks.delete_one({'files_id': ObjectId(image_id)})
        mongo.db.fs.files.delete_one({'filename': user_image})
        mongo.save_file(image_file.filename, image_file)

        user_collection.find_one_and_update({'_id': ObjectId(user.get('_id'))}, {
            '$set': {
                'image': image_file.filename
            }
        })

        return redirect(url_for('show_image', user_id = user_id))
    return render_template('update_image_form.html', form = form)

@app.route('/show-image/<user_id>', methods=['GET','POST'])
def show_image(user_id):
    user = user_collection.find_one_or_404({'_id': ObjectId(user_id)})

    pic = url_for('image', img = user['image'])
    user['image'] = pic

    return render_template('show_image.html', user = user)

if __name__ == '__main__':
    app.run(debug=True)
    

