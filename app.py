from flask import (
    Flask, url_for, render_template, send_from_directory, request, redirect, abort)
from flask_bootstrap import Bootstrap
from sqlalchemy import desc
from flask_wtf import CSRFProtect
from models.Models import Images, db
from forms.Forms import ImageSearch
import time

app = Flask(__name__)
CSRFProtect(app)
app.config.from_pyfile('config.py')
bootstrap = Bootstrap(app=app)
db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/image/', methods=['GET', 'POST'])
@app.route('/image/show', methods=['GET', 'POST'])
def image():
    search_form = ImageSearch()  # 图片搜索表单
    page = request.args.get('page', 1, type=int)  # 得到url参数中的page和count(每页展示的数量), 如果没有参数则默认为1,9
    count = request.args.get('count', 9, type=int)
    if search_form.validate_on_submit():
        image_date = search_form.imagedate.data
        return redirect(url_for('image_search', date=image_date))  # 将得到的日期查询数据发送给相应的查询路由
    pagination = db.session.query(Images.image_name, Images.image_date, Images.image_copyright).order_by(
        desc(Images.image_date)).paginate(page, per_page=count, error_out=True)  # 数据库查询并进行分页
    image_name_date_list = pagination.items  # 返回的查询结果
    return render_template('image_show.html', image_lists=image_name_date_list, search_form=search_form,
                           pagination=pagination)  # 模板渲染


@app.route('/image/search', methods=['GET', 'POST'])
def image_search():
    search_form = ImageSearch()
    image_date = request.args.get('date', time.strftime('%Y-%m-%d'), type=str)
    if image_date.count('-') == 2 and len(image_date) == 10:  # like '2018-09-09'
        image_date = image_date
    elif image_date.count('-') == 0 and len(image_date) == 8:  # like '20180909' -> '2018-09-09'
        image_date = time.strptime(image_date, '%Y%m%d')
        image_date = time.strftime('%Y-%m-%d', image_date)
    image_date = request.args.get('date', '2018-03-28', type=str)
    image_list = db.session.query(Images.image_name, Images.image_date, Images.image_copyright).filter(
        Images.image_date == image_date).all()  # 根据日期查询到的结果
    if image_list:  # 如果查到就进行渲染，否则就抛出404，然后由错误处理函数接收并进行处理
        return render_template('image_show.html', image_lists=image_list, search_form=search_form)
    else:
        abort(404)


@app.route('/download/<image_name>')
def download(image_name):
    file_type = 'jpeg'
    return send_from_directory('static/images', image_name + '.jpg', as_attachment=True)  # 下载函数，参数为图片的名字


@app.route('/about/')
def about():
    return render_template('about.html')  # about页面，网站相关信息


@app.errorhandler(404)
def handle_404(e):
    search_form = ImageSearch()
    return render_template('404.html', search_form=search_form), 404  # 404处理函数


if __name__ == '__main__':
    app.run(debug=True)
