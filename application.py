from flask import Flask, render_template, request, redirect, url_for, flash, \
    Response, session
from flask_bootstrap import Bootstrap
from filters import datetimeformat, file_type
from resources import get_bucket, get_buckets_list, get_url, get_queue_elem, write_to_dynamodb

application = Flask(__name__)
Bootstrap(application)
application.secret_key = 'secret'
application.jinja_env.filters['datetimeformat'] = datetimeformat
application.jinja_env.filters['file_type'] = file_type

msg = None
key = None

@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_buckets_list()
        return render_template("index.html", buckets=buckets)


@application.route('/files')
def files():
    my_bucket = get_bucket()
    files = my_bucket.objects.all()
    summaries = [f for f in files]
    for f in summaries:
        f.url = get_url(f)
    return render_template('files.html', my_bucket=my_bucket, files=summaries)


@application.route('/victor')
def victor():
    global msg
    global key
    
    my_bucket = get_bucket()

    msg = get_queue_elem()
    img_name = "Queue_empty.png" if msg is None else msg.body
    key = img_name
    img_file = my_bucket.Object(img_name)
    img_file.url = get_url(img_file)
    return render_template('victor.html', img_file=img_file)

@application.route('/clicked_coords')
def clicked_coords():
    global key
    
    # return redirect(url_for('victor'))
    coords = [k for k in request.args.keys()]
    coords = coords[0]
    write_to_dynamodb(key, coords)
    msg.delete()
    # return render_template('clicked_coords.html', coords=coords)
    return redirect(url_for('victor'))
    



@application.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('files'))


@application.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))


@application.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

if __name__ == "__main__":
    application.run()
