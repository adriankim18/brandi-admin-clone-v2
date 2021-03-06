from datetime import timedelta, datetime, time
from decimal import Decimal

from flask import Flask
from flask_cors import CORS
from flask.json import JSONEncoder

from config import S3_CONFIG
from seller.view.seller_view import SellerView
from product.view.product_view import ProductView
from image.view.image_view import ImageView
from event.view.event_view import EventView


class CustomJSONEncoder(JSONEncoder):

    """
    default JSONEncoder 에 필요한 자료형 추가
    """
    def default(self, obj):
        """

        Args:
            obj: json 형태로 반환하고자 하는 객체

        Returns: obj 를 json 형태로 변경하는 기능이 추가된 JSONEncoder

        Authors:
            leesh3@brandi.co.kr (이소헌)

        History:
            2020-03-25 (leesh3@brandi.co.kr): 초기 생성
        """

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, timedelta):
            return str(obj)

        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, bytes):
            return obj.decode("utf-8")

        if isinstance(obj, datetime):
            return datetime.strftime(obj+timedelta(hours=+9), '%Y-%m-%d %H:%M:%S')

        return JSONEncoder.default(self, obj)


def make_config(app):
    """

    Args:
        app: 실행할 Flask 앱 객체

    Returns:
        AWS S3에 자료를 추가하기 위한 configuration 이 app 에 추가됨

    Authors:
        yoonhc@brandi.co.kr (윤희철)

    History:
        2020-03-30 (yoonhc@brandi.co.kr): 초기 생성

    """
    app.config['AWS_ACCESS_KEY_ID'] = S3_CONFIG['AWS_ACCESS_KEY_ID']
    app.config['AWS_SECRET_ACCESS_KEY'] = S3_CONFIG['AWS_SECRET_ACCESS_KEY']
    app.config['S3_BUCKET_NAME'] = S3_CONFIG['S3_BUCKET_NAME']
    app.config['DEBUG'] = True
    return


def create_app():
    """

    Returns:
        생성된 플라스크 앱 객체

    Authors:
        leesh3@brandi.co.kr (이소헌)
        yoonhc@brandi.co.kr (윤희철)

    History:
        2020-03-25 (leesh3@brandi.co.kr): 초기 생성

    """
    # set flask object
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    make_config(app)
    CORS(app, resources={r"/*/*": {"origins": "*"}})
    app.register_blueprint(SellerView.seller_app)
    app.register_blueprint(ProductView.product_app)
    app.register_blueprint(ImageView.image_app)
    app.register_blueprint(EventView.event_app)

    return app


