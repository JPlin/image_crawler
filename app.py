from flask import Flask, request, render_template
import DB
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    db = DB.DB()
    db.start()
    count = db.query_count('url')
    db.commit()
    return render_template('index.html' , count = count)

if __name__ == '__main__':
    app.run()