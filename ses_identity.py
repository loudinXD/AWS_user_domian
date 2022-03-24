def create_verify_domain(domain, sesv2, route53):
    # Adds a domain to the list of identities for your Amazon SES account in the current AWS Region and attempts to verify it.
    try:
        domain_details = sesv2.create_email_identity(
            EmailIdentity=domain,
        )
        tokens = domain_details["DkimAttributes"]["Tokens"]
        response = create_resoruce_records(route53, domain, tokens)
        return response
    except:
        response = {"status": "failed", "message": "Whoofps!! Domain already created."}
        return response


def create_resoruce_records(route53, domain, tokens):
    for toke in tokens:
        response = route53.change_resource_record_sets(
            HostedZoneId="hostedzone",
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": f"{toke}._domainkey.{domain}",
                            "ResourceRecords": [
                                {"Value": f"{toke}.dkim.amazonses.com"},
                            ],
                            "TTL": 60,
                            "Type": "CNAME",
                        },
                    },
                ]
            },
        )

    response = {"status": "success", "data": tokens}

    return response


def delete_resource(route53, domain, tokens):
    # del resourse record

    for toke in tokens:
        response = route53.change_resource_record_sets(
            HostedZoneId="hostedzone",
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": f"{toke}._domainkey.{domain}",
                            "ResourceRecords": [
                                {"Value": f"{toke}.dkim.amazonses.com"},
                            ],
                            "TTL": 60,
                            "Type": "CNAME",
                        },
                    },
                ]
            },
        )


def delete_identity(ses, domain):
    ses.delete_identity(Identity=domain)
