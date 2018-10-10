# coding=utf-8
from pymysql import MySQLError
import logging
import pymysql
import requests
import time
import re
import os


class AutoGetBingDailyPg:
    def __init__(self):
        self.image_msg = dict()  # 储存图片相关信息的字典
        self.base_url = ' https://cn.bing.com'
        self.log = self.log_func()

    def get_image_msg(self):
        compile_dict = {
            'image_date': re.compile('data-date="(.*?)"'),  # 图片日期正则
            'image_urlbase': re.compile('g_img={url: "(.*?)",d'),  # 图片urlbase正则
            'image_copyright': re.compile('class="sc_light" title="(.*?)" aria-label'),  # 图片copyright正则
            'id_com': re.compile('target="_blank" href="javascript:void\(0\)" h="ID=(.*?)"'),  # js参数
            'ig_com': re.compile('IG:"(.*?)",EventID:')  # js参数
        }
        html = requests.get(self.base_url).text
        for key in compile_dict.keys():
            if key.startswith('image'):
                self.image_msg[key] = compile_dict[key].findall(html, re.S)[0]
                print(self.image_msg[key])
        image_name = self.image_msg['image_urlbase'].split('/')[-1].replace('_1920x1080.jpg', '') if self.image_msg[
            'image_urlbase'].endswith('1920x1080.jpg') else self.image_msg['image_urlbase']  # 从urlbase中得到图片名字
        t_str = time.strptime(self.image_msg['image_date'], '%Y%m%d')  # 将日期从%Y%m%d -> %Y-%m-%d
        self.image_msg['image_date'] = time.strftime('%Y-%m-%d', t_str)
        id = compile_dict['id_com'].findall(html, re.S)[0]
        ig = compile_dict['ig_com'].findall(html, re.S)[0]
        print(id, ig, image_name)
        image_position, image_description = self.get_detail(id, ig)  # 图片拍摄地及图片描述
        self.image_msg['image_position'] = image_position
        self.image_msg['image_description'] = image_description
        self.image_msg['image_name'] = image_name
        self.log.info(f'图片名字为: {self.image_msg["image_name"]}')
        self.log.info(f'得到图片url为: {self.image_msg["image_urlbase"]}')

    def get_detail(self, id, ig):
        url = f'https://cn.bing.com/cnhp/life?ensearch=0&IID={id}&IG={ig}'
        self.log.info(f'开始在 {url} 查找图片相关信息。。。')
        print(f'开始在 {url} 查找图片相关信息。。。')
        html = requests.get(url)
        if html.status_code == 200 and html.text is not None:
            name_com = re.compile('<span class="hplaAttr">(.*?)</span></div>')
            desc_com = re.compile('<div id="hplaSnippet">(.*?)</div><div class="hplaPvd">')
            html = html.text
            name = name_com.findall(html, re.S)[0]
            description = desc_com.findall(html, re.S)[0]
            self.log.info('相关信息记录查找结束。。。')
            return name, description
        else:
            self.log.error(f'请求 {url} 出错，结果为空')
            exit(0)

    def save2mysql(self):
        try:
            self.log.info('开始保存到数据库。。。')
            keys = ','.join(self.image_msg.keys())
            values = ','.join(['%s'] * len(self.image_msg))
            sql_str = 'select image_date from images where image_date = "{}"'.format(self.image_msg['image_date'])
            result = cursor.execute(sql_str)
            if result != 0:
                print(self.image_msg['image_name'], '已存在')
                self.log.warning('图片已存在\n')
                exit(0)
            else:
                sql_str = 'INSERT INTO `images` ({keys}) VALUES ({values})'.format(keys=keys, values=values)
                cursor.execute(sql_str, tuple(self.image_msg.values()))
                db.commit()
                print(self.image_msg['image_name'], 'insert mysql succeed')
                self.log.info('图片成功保存到数据库\n')
        except MySQLError as e:
            self.log.error(f'保存到数据时发生错误: {e}\n', )
            db.rollback()

    def log_func(self):
        log = logging.getLogger(__name__)
        log.setLevel(logging.INFO)
        if not log.handlers:  # 防止出现多个重复处理函数
            fmt = '%(name)s %(asctime)s %(levelname)s %(message)s'  # 设置日志记录的格式
            dft = '%Y-%m-%d  %H:%M:%S'  # 设置时间格式
            fh = logging.FileHandler(os.path.abspath('log.log'), encoding='utf-8')  # 日志记录文件
            formattr = logging.Formatter(fmt=fmt, datefmt=dft) 
            fh.setFormatter(formattr)
            log.addHandler(fh)  # 添加处理函数

        return log

    def main(self):
        self.log.info('程序开始执行。。。')
        self.get_image_msg()
        image_urldetail = self.image_msg['image_urlbase']
        image_url = self.base_url + image_urldetail
        self.image_msg['image_data'] = requests.get(image_url).content
        self.save2mysql()
        time.sleep(20)


if __name__ == '__main__':
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='passwd', db='bing_images')
    cursor = db.cursor()
    image = AutoGetBingDailyPg()
    image.main()
