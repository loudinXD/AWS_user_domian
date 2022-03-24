def domain_status(domain, ses):
    # check verfication
    VerificationAttributes = ses.get_identity_verification_attributes(
        Identities=[
            domain,
        ]
    )
    DkimAttributes = ses.get_identity_dkim_attributes(
        Identities=[
            domain,
        ]
    )
    #when you black here the ['Verification status] goes to next line so careful and reverse it back after black.
    v_status = VerificationAttributes["VerificationAttributes"][domain]["VerificationStatus"]
    d_status = DkimAttributes["DkimAttributes"][domain]["DkimVerificationStatus"]

    return {"DOMAIN CREATION STATUS": v_status, "DOMAIN VERIFICATION": d_status}
