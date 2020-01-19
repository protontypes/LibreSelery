import dns.resolver


class EmailChecker:
    def __init__(self):
        pass

    @staticmethod
    def checkMail(mail):
        #regex = r'\b[\w.-]+?@\w+?\.\w+?\b'
        # if re.fullmatch(regex, mail) is not None:
        try:
            dns.resolver.query(mail.split('@')[1], "MX")[0].exchange
            return True
        except:
            return False
        return False


if __name__ == "__main__":
    pass
