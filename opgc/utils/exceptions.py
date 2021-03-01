

class GitHubUserDoesNotExist(Exception):
    def __str__(self):
        return "not exists github user."


class RateLimit(Exception):
    def __str__(self):
        return "github api rate limited."
