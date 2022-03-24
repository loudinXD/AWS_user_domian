def create_user_and_attach_policy(username, iam):
    # creates IAM user <username>
    try:

        iam_details = iam.create_user(
            UserName=username,
        )
        iam.attach_user_policy(
            UserName=username,
            PolicyArn="policy to attach",
        )
        response = create_access_key(iam, username, iam_details)
        return response
    except:
        # "Username already taken, try something different."
        response = {
            "status": "failed",
            "message": "failed",
        }
        return response


def create_access_key(iam, username, iam_details):
    iam_access_details = iam.create_access_key(UserName=username)
    iam_user_name = iam_details["User"]["UserName"]
    iam_user_id = iam_details["User"]["UserId"]
    iam_access_key = iam_access_details["AccessKey"]["AccessKeyId"]
    iam_user_secretaccess = iam_access_details["AccessKey"]["SecretAccessKey"]
    data = {
        "IAM USER NAME: ": iam_user_name,
        "USER ID": iam_user_id,
        "USER ACCESS KEY": iam_access_key,
        "USER SECRET ACCESS KEY": iam_user_secretaccess,
    }
    # {'IAM USER NAME: ': 'tester_8', 'USER ID: ': 'AIDAQRDGJNSFITUZ7O44BAXTMKN2H', 'USER SECRET ACCESS KEY': '81/v3WsyYdsafddfv5WU3/hli6FgyjOkdgcDJSkvXHVW2R'}
    response = {"status": "success", "data": data}
    return response


def delete_accesskey(iam, resp, username):
    accesskeyr = resp["IAM ACCESS KEY ID"]
    response = iam.delete_access_key(
        UserName=username,
        AccessKeyId=accesskeyr,
    )


def detach_policy(iam, username):
    response = iam.detach_user_policy(
        UserName=username, PolicyArn="policy to detach"
    )


def delete_user(iam, username):
    iam.delete_user(UserName=username)
