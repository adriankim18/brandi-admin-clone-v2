import bcrypt
from flask import jsonify, g

from connection import DatabaseConnection

from seller.model.seller_dao import SellerDao


class SellerService:

    """
    셀러 서비스
    """
    def create_new_seller(self, request, db_connection):
        """ 신규 셀러 회원가입

        인력된 인자가 신규 셀러로 가입됨

        Args:
            request: 신규 가입 셀러 정보가 담긴 요청
            db_connection: 데이터 베이스 커넥션 객체

        Returns: http 응답 코드
            200: 신규 셀러 계정 저장 완료
            400: key error
            500: server error

        Authors:
            leesh3@brandi.co.kr (이소헌)
            yoonhc@barndi.co.kr (윤희철)

        History:
            2020-03-25 (leesh3@brandi.co.kr): 초기 생성
            2020-03-30 (yoonhc@barndi.co.kr): db_connection 인자 추가
        """
        seller_dao = SellerDao()
        new_seller = request.json
        new_seller_result = seller_dao.insert_seller(new_seller, db_connection)

        return new_seller_result 

    # noinspection PyMethodMayBeStatic
    def change_password(self, account_info, db_connection):

        """ 계정 비밀번호 변경

        account_info에 담긴 권한 정보를 확인하고,
        마스터 권한일 경우
        -> 비밀번호를 바로 변경해주며,
        셀러 권한일 경우
        -> 데코레이터에서 확인된 account_no 와 파라미터로 받은 account_no 가 일치하는지 확인하고,
        비밀번호 변경

        Args:
            account_info: 엔드포인트에서 전달 받은 account 정보.
            db_connection: 연결된 database connection 객체

        Returns: http 응답코드
            200: SUCCESS 비밀번호 변경 완료
            400: INVALID_AUTH_TYPE_ID
            401: INVALID_PASSWORD
            500: DB_CURSOR_ERROR, SERVER_ERROR

        Authors:
            leejm3@brandi.co.kr (이종민)

        History:
            2020-03-31 (leejm3@brandi.co.kr) : 초기 생성
            2020-04-01 (leejm3@brandi.co.kr) :
            셀러의 경우 decorator account_no 와 parameter account_no이 일치하는 조건 추가

        """

        seller_dao = SellerDao()
        try:
            # Key 가 모두 들어오는지 확인하기 위해 새로운 dict 에 정보를 담음
            new_account_info = {
                'auth_type_id': account_info.get('auth_type_id', None),
                'decorator_account_no': account_info.get('account_no', None),
                'parameter_account_no': account_info.get('parameter_account_no', None),
                'original_password': account_info.get('original_password', None),
                'new_password': account_info.get('new_password', None)
            }

            # 계정이 가진 권한 타입을 가져옴
            account_auth_type_id = new_account_info['auth_type_id']

            # 마스터 권한일 때
            if account_auth_type_id == 1:

                # 인자로 전달 받은 새로운 비밀번호를 암호화 시킨 후 디코드 시켜 'new_password' 로 저장
                crypted_password = bcrypt.hashpw(new_account_info['new_password'].encode('utf-8'), bcrypt.gensalt())
                new_account_info['new_password'] = crypted_password.decode('utf-8')

                # 새로운 비밀번호를 담아서 seller_dao 의 비밀번호 변경 dao 를 호출 및 반환
                changing_password_result = seller_dao.change_password(new_account_info, db_connection)
                return changing_password_result

            # 셀러 권한일 때
            elif account_auth_type_id == 2:

                if new_account_info['decorator_account_no'] == new_account_info['parameter_account_no']:
                    # DB 에서 기존에 저장되어있는 암호화된 비밀번호를 가져옴
                    original_password = seller_dao.get_account_password(new_account_info, db_connection)

                    # DB 에서 가져온 기존 비밀번호와 셀러가 입력한 기존 비밀번호가 일치하는지 확인
                    if bcrypt.checkpw(new_account_info['original_password'].encode('utf-8'),
                                      original_password['password'].encode('utf-8')):
                        # 일치하는지 확인되면 새로운 비밀번호를 암호화해서 new_account_info 에 저장해줌
                        crypted_password = bcrypt.hashpw(new_account_info['new_password'].encode('utf-8'),
                                                         bcrypt.gensalt())
                        new_account_info['new_password'] = crypted_password.decode('utf-8')

                        # 새로운 비밀번호를 담아서 seller_dao 의 비밀번호 변경 dao 를 호출 및 반환
                        changing_password_result = seller_dao.change_password(new_account_info, db_connection)
                        return changing_password_result

                    # 기존 비밀번호와 일치하지 않을 경우
                    return jsonify({'message': 'INVALID_PASSWORD'}), 401

                # decorator_account_no 와 parameter_account_no 가 다를 경우 비밀번호 변경 권한이 없음
                else:
                    return jsonify({'message': 'NO_AUTHORIZATION'}), 403

            # 존재하지 않는 auth_type_id
            else:
                return jsonify({'message': 'INVALID_AUTH_TYPE_ID'}), 400

        except Exception as e:
            return jsonify({'message': f'{e}'}), 400

    # noinspection PyMethodMayBeStatic
    def get_seller_info(self, account_info, db_connection):

        """ 계정 셀러정보 표출

        account_info 에 담긴 권한 정보를 확인하고,
        마스터 권한일 경우
        -> 바로 parameter_account_no 의 셀러 정보를 표출해주며,
        셀러 권한일 경우
        -> 데코레이터에서 확인된 account_no 와 파라미터로 받은 account_no 가 일치하는지 확인하고,
        parameter_account_no 의 셀러정보를 표출해줍니다.

        Args:
            account_info: 엔드포인트에서 전달 받은 account 정보
            db_connection: 연결된 database connection 객체

        Returns: http 응답코드
            200: SUCCESS 비밀번호 변경 완료
            400: INVALID_AUTH_TYPE_ID
            401: INVALID_PASSWORD
            500: SERVER ERROR, DB_CURSOR_ERROR

        Authors:
            leejm3@brandi.co.kr (이종민)

        History:
            2020-04-01 (leejm3@brandi.co.kr) : 초기 생성

        """

        seller_dao = SellerDao()
        try:
            # 계정이 가진 권한 타입을 가져옴
            account_auth_type_id = account_info['auth_type_id']

            # 마스터 권한일 때
            if account_auth_type_id == 1:

                # parameter_account_no 의 셀러정보를 가져옴
                getting_seller_info_result = seller_dao.get_seller_info(account_info, db_connection)
                return getting_seller_info_result

            # 셀러 권한일 때
            elif account_auth_type_id == 2:

                # decorator_account_no 와 parameter_account_no 가 동일한지 확인
                if account_info['decorator_account_no'] == account_info['parameter_account_no']:

                    # parameter_account_no 의 셀러정보를 가져옴
                    getting_seller_info_result = seller_dao.get_seller_info(account_info, db_connection)
                    return getting_seller_info_result

                # decorator_account_no 와 parameter_account_no 가 다를 경우 셀러정보 열람 권한이 없음
                else:
                    return jsonify({'message': 'NO_AUTHORIZATION'}), 403

            # 존재하지 않는 auth_type_id
            else:
                return jsonify({'message': 'INVALID_AUTH_TYPE_ID'}), 400

        except Exception as e:
            return jsonify({'message': f'{e}'}), 400

    # noinspection PyMethodMayBeStatic
    def change_seller_info(self, account_info, db_connection):

        """ 계정 셀러정보 수정 로직(새로운 셀러정보 이력 생성)

        account_info 에 담긴 권한 정보를 확인하고,
        마스터 권한일 경우
        -> 바로 parameter_account_no 의 셀러 정보를 수정해주며,
        셀러 권한일 경우
        -> 데코레이터에서 확인된 수정 진행자의 account_no 와 파라미터로 받은 수정될 셀러의 account_no 가 일치하는지 확인하고,
        parameter_account_no 의 셀러정보를 수정해줍니다.

        Args:
            account_info: 엔드포인트에서 전달 받은 account 정보
            db_connection: 연결된 database connection 객체

        Returns: http 응답코드
            200: SUCCESS 셀러정보 수정(새로운 이력 생성) 완료
            400: INVALID_APP_ID (존재하지 않는 브랜디 앱 아이디 입력)
            400: INVALID_AUTH_TYPE_ID
            403: NO_AUTHORIZATION
            500: SERVER_ERROR, DB_CURSOR_ERROR

        Authors:
            leejm3@brandi.co.kr (이종민)

        History:
            2020-04-03 (leejm3@brandi.co.kr) : 초기 생성

        """

        seller_dao = SellerDao()
        try:
            # 계정이 가진 권한 타입을 가져옴
            account_auth_type_id = account_info['auth_type_id']

            # 마스터 권한일 때
            if account_auth_type_id == 1:

                # parameter_account_no 의 셀러정보를 수정함(새로운 이력 생성)
                changing_seller_info_result = seller_dao.change_seller_info(account_info, db_connection)
                return changing_seller_info_result

            # 셀러 권한일 때
            elif account_auth_type_id == 2:

                # decorator_account_no 와 parameter_account_no 가 동일한지 확인
                if account_info['decorator_account_no'] == account_info['parameter_account_no']:

                    # parameter_account_no 의 셀러정보를 수정함(새로운 이력 생성)
                    changing_seller_info_result = seller_dao.change_seller_info(account_info, db_connection)
                    return changing_seller_info_result

                # decorator_account_no 와 parameter_account_no 가 다를 경우 셀러정보 수정 권한이 없음
                else:
                    return jsonify({'message': 'NO_AUTHORIZATION'}), 403

            # 존재하지 않는 auth_type_id
            else:
                return jsonify({'message': 'INVALID_AUTH_TYPE_ID'}), 400

        except Exception as e:
            return jsonify({'message': f'{e}'}), 400

    def get_seller_list(self, request, user, db_connection):

        """ 가입된 모든 셀러 정보 리스트 표출
        Args:
            request: 클라이언트에서 온 요청
            user: 유저 정보
            db_connection: 데이터베이스 커넥션 객체

        Returns:
            200: 가입된 모든 셀러 정보 리스트
            403: 열람 권한 없음

        Authors:
            yoonhc@brandi.co.kr (윤희철)

        History:
            2020-04-03 (yoonhc@brandi.co.kr): 초기 생성

        """

        seller_dao = SellerDao()
        auth_type_id = user.get('auth_type_id', None)

        # 마스터 유저이면 dao에 db_connection 전달
        if auth_type_id == 1:
            seller_list_result = seller_dao.get_seller_list(request, db_connection)
            return seller_list_result

        return jsonify({'message' : 'AUTHORIZATION_REQUIRED'}), 403

    def change_seller_status(self, request, user, db_connection):

        """ 마스터 권한 셀러 상태 변경
            Args:
                request: 클라이언트에서 온 요청
                user: 유저 정보
                db_connection: 데이터베이스 커넥션 객체

            Returns:
                200: 수정 성공
                400: value값이 정확하게 안들어 온 경우
                403: 수정 권한 없음

            Authors:
                yoonhc@brandi.co.kr (윤희철)

            History:
                2020-04-03 (yoonhc@brandi.co.kr): 초기 생성

        """
        seller_dao = SellerDao()
        auth_type_id = user.get('auth_type_id', None)

        # 마스터 유저이면 dao에 db_connection 전달
        if auth_type_id == 1:
            data = request.json
            seller_status_id = data.get('seller_status_id', None)
            seller_account_id = data.get('seller_account_id', None)
            print(data)

            # 셀러 상태 번호와 셀러 계정 번호가 둘다 들어오지 않으면 400 리턴
            if not seller_status_id or not seller_account_id:
                return jsonify({'message' : 'INVALID_VALUE'}), 400

            seller_list_result = seller_dao.change_seller_status(seller_status_id, seller_account_id, db_connection)
            return seller_list_result

        return jsonify({'message' : 'AUTHORIZATION_REQUIRED'}), 403

    def get_seller_name_list(self, keyword, db_connection):

        """ 마스터 권한으로 상품 등록시 셀러를 검색

        마스터 권한으로 접속하여 상품을 등록할 경우,
        셀러를 한글 이름으로 검색하여 선택할 수 있음

        Args:
            keyword(string): 한글 이름 검색어
            db_connection(DatabaseConnection): 데이터베이스 커넥션 객체

        Returns:
            200: 검색된 셀러 10개
            403: 마스터 권한이 없음
            
         Authors:

            leesh3@brandi.co.kr (이소헌)

        History:
            2020-04-04 (leesh3@brandi.co.kr): 초기 생성

        """
        seller_dao = SellerDao()

        if g.account_info['auth_type_id'] == 1:
            seller_name_list_result = seller_dao.get_seller_name_list(keyword, db_connection)
            return seller_name_list_result

        return jsonify({'message': 'AUTHORIZATION_REQUIRED'}), 403
