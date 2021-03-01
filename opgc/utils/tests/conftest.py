import pytest

# from tests.init_data import InitTestData


@pytest.fixture(scope='function')
def github_context():
    # init_data = InitTestData()

    ret = type(
        'context',
        (),
        {
            # 'init': init_data,
        }
    )

    return ret
