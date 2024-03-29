from rest_framework.exceptions import APIException


class NotExistsGithubUser(APIException):
    status_code = 404
    default_detail = '존재하지 않는 Github User 입니다.'
    default_code = 'NOT_EXISTS'


class RateLimitGithubAPI(APIException):
    """
    github_user가 없거나 rate_limit로 인해 업데이트를 할 수 없는경우
    """
    status_code = 403
    default_detail = 'Github api호출이 가능한 시점이 되면 유저정보를 생성하거나 업데이트합니다.'
    default_code = 'RATE_LIMIT'
