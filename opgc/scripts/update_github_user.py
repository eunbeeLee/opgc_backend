"""
    Github api 테스트 스크립트
    : 어떤 데이터들을 수집하고 가공할지 테스트

"""
import timeit

from sentry_sdk import capture_exception

from core.github_service import GithubInformationService

USERNAME_LIST = ['JAY-Chan9yu', 'techinpark', '87kangsw', 'ginameee', 'Robin-Haenara']


def run():
    start_time = timeit.default_timer()  # 시작 시간 체크

    print('------- start update information -------')
    for username in USERNAME_LIST:
        try:
            github_information_service = GithubInformationService(username=username)
            github_information_service.update()

        except Exception as e:
            capture_exception(e)

    print('------- end update information -------')
    terminate_time = timeit.default_timer()  # 종료 시간 체크
    print(f'{terminate_time - start_time:.2f}초 걸렸습니다.')
