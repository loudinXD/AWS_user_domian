"""Usage:
  sesgen [-d] <user> <domain>
  sesgen -h | --help | --version | -v

Options:
    -d, --delete    Delete
"""

import os
import json
import copy
from woof import woof
from docopt import docopt
from functions.sesgen.clients import iam, s3, ses, sesv2, route53
from functions.sesgen.iam_user import (
    create_user_and_attach_policy,
    delete_accesskey,
    detach_policy,
    delete_user,
)
from functions.sesgen.smtp_creation import smtp_password
from functions.sesgen.ses_identity import (
    create_resoruce_records,
    create_verify_domain,
    delete_resource,
    delete_identity,
)
from functions.sesgen.status import domain_status

shell = os.environ.get("SHELL", "sh")


def hasfailed(status):
    if status["status"] == "failed":
        return True


@woof(html_template="sesgen/template.html")
def sesgen(*args):
    """for creating : sesgen <username> <domain>
    for deleting : sesgen --delete <username> <domain>
    for version : sesgen --version"""
    region = "ap-south-1"

    bucket = "sesgen-woof"

    try:
        arguments = docopt(__doc__, argv=list(args), help=False)
    except:
        return {"Error, couldn't recognize command": __doc__}

    if arguments["--delete"] == True:
        # use logger, rollback views
        option, username, domain = args
        object_name = f"{username}_{domain}"
        response = s3.get_object(Bucket=bucket, Key=object_name)
        resp = json.loads(response["Body"].read())
        tokens = []
        for i in range(1, 4):
            tokens.append(resp[f"CNAME TOKEN-{i}"])
        try:
            delete_resource(route53, domain, tokens)
        except:
            return {"problem": "deleting resource records"}
        try:
            delete_accesskey(iam, resp, username)
        except:
            return {"problem": "deleting accesskey"}
        try:
            del_bucket_object = s3.delete_object(Bucket=bucket, Key=object_name)
        except:
            return {"problem": "deleting bucket obj"}
        try:
            delete_identity(ses, domain)
        except:
            return {"problem": "deteting identity"}
        try:
            detach_policy(iam, username)
        except:
            return {"problem": "detaching policy"}
        try:
            delete_user(iam, username)
        except:
            return {"problem": "deleting user"}
        response = {"Deleted IAM user": username, "Deleted identity": domain}
        return response

    elif arguments["--help"] == True or arguments["-h"] == True:
        return {"Help": __doc__}

    elif arguments["--version"] == True or arguments["-v"] == True:
        return {"Version": "0.0.3"}

    else:
        username, domain = args
        object_name = f"{username}_{domain}"
        user_response = create_user_and_attach_policy(username, iam)
        # if the IAM user already exists then this will execute which prints all the things from bucket
        if hasfailed(user_response):
            print("f")
            statuses = domain_status(domain, ses)
            domian_creation_statuts = statuses["DOMAIN CREATION STATUS"]
            domain_verification_status = statuses["DOMAIN VERIFICATION"]
            if domian_creation_statuts == "Pending":
                action = "rerun the command"
            elif domian_creation_statuts == "Success":
                action = "successfully setup enjoy, use access key as sender id and smtp password as password"
            response = s3.get_object(Bucket=bucket, Key=object_name)
            resp = json.loads(response["Body"].read())
            resp["IAM CREATION STATUS"] = "Success"
            resp["DOMAIN VERIFICAION STATUS"] = domain_verification_status
            resp["NEXT ACTION"] = action
            return resp
        user_id = user_response["data"]["USER ID"]
        iam_access_key = user_response["data"]["USER ACCESS KEY"]
        iam_secret_key = user_response["data"]["USER SECRET ACCESS KEY"]

        user_password = smtp_password(iam_secret_key, region)
        if hasfailed(user_password):
            return user_password["message"]
        smtp_crediantial = user_password["data"]

        user_domain = create_verify_domain(domain, sesv2, route53)
        if hasfailed(user_domain):
            return user_domain["message"]
        cname_tokens = user_domain["data"]

        statuses = domain_status(domain, ses)
        domian_creation_statuts = statuses["DOMAIN CREATION STATUS"]
        domain_verification_status = statuses["DOMAIN VERIFICATION"]
        if domian_creation_statuts == "Pending":
            next_action = "rerun the command for status update"
        elif domian_creation_statuts == "Success":
            next_action = "ran successfully have fun"
    response = {
        "USER NAME": username,
        "USER ID": user_id,
        "IAM ACCESS KEY ID": iam_access_key,
        "IAM SECRET ACCEESS KEY": iam_secret_key,
        "SMTP PASSWORD": smtp_crediantial,
        "CNAME TOKEN-1": cname_tokens[0],
        "CNAME TOKEN-2": cname_tokens[1],
        "CNAME TOKEN-3": cname_tokens[2],
        "DOMAIN VERIFICAION STATUS": domian_creation_statuts,
        "DKIM VERIFICAION STATUS": domain_verification_status,
        "NEXT ACTION": next_action,
    }
    resp_text = copy.deepcopy(response)
    resp_text.pop("DKIM VERIFICAION STATUS")
    resp_text.pop("DOMAIN VERIFICAION STATUS")
    resp_texter = json.dumps(resp_text, indent=4)
    f = open(f"{object_name}", "w")
    f.write(resp_texter)
    f.close()
    s3.upload_file(object_name, bucket, object_name)
    os.remove(object_name)
    return response
