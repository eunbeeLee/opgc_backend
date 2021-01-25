"""
    Github api 테스트 스크립트
    : 어떤 데이터들을 수집하고 가공할지 테스트

"""
import timeit

from utils.githubs import UpdateGithubInformation

USERNAME = 'JAY-Chan9yu'


def run():
    start_time = timeit.default_timer()  # 시작 시간 체크

    print('------ start update github user ------')
    update_github_information = UpdateGithubInformation(username=USERNAME)
    print('------- start update information -------')
    update_github_information.update()
    print('------- end update information -------')
    terminate_time = timeit.default_timer()  # 종료 시간 체크
    print(f'{terminate_time - start_time}초 걸렸습니다.')
