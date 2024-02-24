from minio import Minio

endpoint = '172.16.101.198:9000'
access = "bEDyskir1YNZC17PVfnl"
secret = "jPLs08KCsHqxkKqQsFs3AxJZ5nutzIKorMl9W8ld"


def client():

    return Minio(endpoint, access_key=access, secret_key=secret, secure=False)
