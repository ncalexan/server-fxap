import time
from browserid.utils import (encode_bytes, bundle_certs_and_assertion,
                             to_int, to_hex)

from browserid import jwt

MOCKMYID_MODULUS          = to_int("15498874758090276039465094105837231567265546373975960480941122651107772824121527483107402353899846252489837024870191707394743196399582959425513904762996756672089693541009892030848825079649783086005554442490232900875792851786203948088457942416978976455297428077460890650409549242124655536986141363719589882160081480785048965686285142002320767066674879737238012064156675899512503143225481933864507793118457805792064445502834162315532113963746801770187685650408560424682654937744713813773896962263709692724630650952159596951348264005004375017610441835956073275708740239518011400991972811669493356682993446554779893834303");

MOCKMYID_PUBLIC_EXPONENT  = to_int("65537");

MOCKMYID_PRIVATE_EXPONENT = to_int("6539906961872354450087244036236367269804254381890095841127085551577495913426869112377010004955160417265879626558436936025363204803913318582680951558904318308893730033158178650549970379367915856087364428530828396795995781364659413467784853435450762392157026962694408807947047846891301466649598749901605789115278274397848888140105306063608217776127549926721544215720872305194645129403056801987422794114703255989202755511523434098625000826968430077091984351410839837395828971692109391386427709263149504336916566097901771762648090880994773325283207496645630792248007805177873532441314470502254528486411726581424522838833");


MOCKMYID_KEY_DATA = {'n':MOCKMYID_MODULUS, 'e':MOCKMYID_PUBLIC_EXPONENT, 'd':MOCKMYID_PRIVATE_EXPONENT, 'algorithm':'RS'}
data = MOCKMYID_KEY_DATA.copy()

MOCKMYID_KEY = jwt.RS256Key(data)
data.pop('d')
MOCKMYID_PUBKEY = jwt.RS256Key(data)

issuer_keypair = (data, MOCKMYID_KEY)

# print key
# print pubkey

# s = jwt.generate({'x':10}, key)
# print s

# t = jwt.parse(s)
# print t.payload

# pubkey["algorithm"] = "RS256"
# print t.check_signature(pubkey)

RS256_KEY_DATA = {
    "e": to_int("65537"),
    "n": to_int("""215157110954304992279368637802866269325596452629865
                395762774177857897276978877993223049183402424105773515
                201290613360308518627825054462116613364134614187172697
                697613069260343087878396452532793731462713531516304214
                014298822788246837398523211444942078088277812631990233
                605547678426218564011563878969467011295043595120351985
                983964933931846863837473460561785876645510646206349911
                224431000742182234603386145326243738136228530828331813
                878460203518442750258401437788566030271868538755030318
                166019192692586115555977516152130159519321313883015410
                981516435771312385629298791747259305672948565747771968
                86049733189121606135786757"""),
    "d": to_int("""207323904265915659359360496298103480082712690236486
                711442619468481988356783086258907621328120702575700798
                914761181078121416297141767464747032219333582869739887
                884736300667713296956049473944465827480687584552025991
                717914841355273754193114413628325025151484385088161118
                794329026966356844773094137980084703759603150591097278
                715178348827663152700571998676478162596562814192444939
                969198839004936798148664921543401849279637016264260100
                884799833350543315289267376119637531072279656873496164
                487439865534937842040868268534375254876875600122000071
                183491091196621992223116828762911412383078024328333659
                43400749509104482286419733"""),
    "algorithm": "RS",
}

data = RS256_KEY_DATA.copy()

email_key = jwt.RS256Key(data)
data.pop('d')
email_pubkey = jwt.RS256Key(data)

for k, v in data.items():
    data[k] = str(v)
email_keypair = (data, email_key)

def make_certificate(email, email_public_key, issuer, issuer_private_key, iat=None, exp=None):
    # Generate the certificate signing the email's public key
    # with the issuer's private key.

    if issuer is None:
        issuer = "mockmyid.com"
    if iat is None:
        iat = int(time.time() * 1000)
    if exp is None:
        exp = int(iat + 60 * 1000)

    certificate = {
        "iss": issuer,
        "iat": iat,
        "exp": exp,
        "principal": {"email": email},
        "public-key": email_public_key,
    }

    certificate = jwt.generate(certificate, issuer_private_key)

    return certificate

def make_assertion(email, audience, issuer=None, exp=None, iat=None,
                    assertion_sig=None, certificate_sig=None,
                    new_style=True, email_keypair=None, issuer_keypair=None):
    """Generate a new dummy assertion for the given email address.

    This method lets you generate BrowserID assertions using dummy private
    keys. Called with just an email and audience it will generate an assertion
    from login.persona.org.

    By specifying the "exp", "assertion_sig" or "certificate_sig" arguments
    it is possible generate invalid assertions for testing purposes.
    """
    if issuer is None:
        issuer = "mockmyid.com"
    if iat is None:
        iat = int(time.time() * 1000)
    if exp is None:
        exp = int(iat + 60 * 1000)

    # Get private key for the email address itself.
    # if email_keypair is None:
    #     email_keypair = get_keypair(email)
    email_pub, email_priv = email_keypair

    # Get private key for the hostname so we can sign it.
    # if issuer_keypair is None:
    #     issuer_keypair = get_keypair(issuer)
    iss_pub, iss_priv = issuer_keypair

    # Generate the assertion, signed with email's public key.
    assertion = {
        "exp": exp,
        "aud": audience,
        "iss": "127.0.0.1",
        "iat": iat,
    }
    assertion = jwt.generate(assertion, email_priv)
    if assertion_sig is not None:
        assertion = ".".join(assertion.split(".")[:-1] +
                                [encode_bytes(assertion_sig)])

    # # Generate the certificate signing the email's public key
    # # with the issuer's public key.
    # certificate = {
    #     "iss": issuer,
    #     "iat": iat,
    #     "exp": exp,
    #     "principal": {"email": email},
    #     "public-key": email_pub,
    # }
    # certificate = jwt.generate(certificate, iss_priv)
    # if certificate_sig is not None:
    #     certificate = ".".join(certificate.split(".")[:-1] +
    #                             [encode_bytes(certificate_sig)])

    certificate = make_certificate(email, email_pub, issuer, iss_priv, iat, exp)
    # def make_certificate(email, email_public_key, issuer, issuer_private_key, iat=None, exp=None):

    # Combine them into a BrowserID bundled assertion.
    return bundle_certs_and_assertion([certificate], assertion, new_style)

aud = "http://localhost:8080"

assertion = make_assertion("test@mockmyid.com", aud, issuer="mockmyid.com", email_keypair=email_keypair, issuer_keypair=issuer_keypair)

xassertion = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEzNTQ2MDA2ODc4NzAsInByaW5jaXBhbCI6eyJlbWFpbCI6InRlc3RAbW9ja215aWQuY29tIn0sInB1YmxpYy1rZXkiOnsiZSI6IjY1NTM3IiwibiI6IjIwMTIyMTc1MjkzMzk1NzI4ODgwNzkwNjg1MzQ0NjEzMDYzNjQ1MzU1NDc5NjQzNzQ5NDE5MjExMTM4MDkyOTEyMDU3MTY0NzYxNTc2NjM3NTQ1NjMxNTAzOTQzMjcwMTQ0MDY0OTk3ODIwMjEzNzk1NTYyNzE4Njg5NTc0Njg2NTIyMjY0MzI2MDU0NDA1MTYzMDgzMDM4Njc3ODU1NTcyNjMzMjA2OTY2MTY0ODU4NjIyMDY2ODQwNjkzMzg3ODk2MzEyMjIyMDg5MjE1NjczMjk0MzU5Mzg1NTExOTY4NTI5Mjk5ODEyOTYzNjU1MjMzNTQyOTc4MTE0MzUwNTQ4NDQ4NDY0OTM5NjkzMDg0MjIyMTA2NTQ2NTIyMjQzMTE2MTMyNzc1Mzk1NjMxMzUwODQzMzk5MjY1OTA5MDE5MzY3NDM5NDI5OTA1NTMyNDk0NjYwMDEyMDc2MTQ0Njc2Nzc0ODYwNDI4OTgxMzU0OTEwMjYwMDg5MDQ3NzAyMzMzNTUzNzE4ODg3Mjg3MDc3OTMyMTM5NDU0Mzg2NzAyMDIwMTAyNjYwNDE2NDg0NTYzODQ2ODI0NTkzNjA2NjMxNjM1Mjc0NjM1NDM4MjM3OTk0MDUzNzg3OTY0NTgwNTAxMzQ2NDUwODQwOTEwNTk1NzgzMjY0MTY2MTAyNzU4MzAzMTAwMDQzNDM2NDE3MzAwODAyMDU2ODA4NTAxODE4NjcyOTEzODgxMzI2Mjk4NjAzMTAyNjk4OTk4OTY0NDEwNzQzMDE0OTE1MjAyMDIyNTg3MDk0ODc4NzExMjQwMzU4MDA4MTExIiwiYWxnb3JpdGhtIjoiUlMifSwiaXNzIjoibW9ja215aWQuY29tIiwiaWF0IjoxMzU0NTk3MDg3ODcwfQ.FINDxuDBM7qCQqBy3cUXL9Gftl-PAi8rS4r-aoOqZUzrX7S5VQPs_2b87jNCSjk0pBv8-dnvDYQXFUr50Eg11E5nWpfR6WA2uIZ8E-uPoSZITswcLYO1popZYuxBh8gAOytp6ECnoSdymnNiv5TcJRxputFkD7HbSuPZVd_XxqF_-1J_FicOj8F-G38Icvf5R-7z-4gTiMrq8izLDGa2bB_l1hGCbxSFS8SVE6Nagyb8mSlb12o3SzJL1wZ6WzpWbNCDtTAlDTMIQB-BmBUlzLx3jz9mC61kcdgNXDaKosOHZgfYtzOiuDOz7BtP_FODQSvE7NM4K4Q_oUMliOhuWA~eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEzNTQ2MDA2ODgyMTIsImF1ZCI6Imh0dHA6XC9cL2xvY2FsaG9zdDo4MDgwIiwiaXNzIjoiMTI3LjAuMC4xIiwiaWF0IjoxMzU0NTk3MDg4MjEyfQ.DoTEEqTz2V_QajY4SMTDswAPBei4gszOUk4mgFBpGE_Af6MD2sYcBl_9pHwqFbVT8rULnZlzmRuJxuJqIjn8J3SbA7lR9CgR9BxLW5BXZDoVtIL1pTwUz_ViVCMowh253eMIAVKfATQ84ql-06492as0f2qH299j7E-hgXDxxIShTTwJft1YK_ALTIb9q4XFlE7RmK3mZRsuE5PnaZNdzvVJczABspyqGREFCpbMpKBuiu8AaYDP0JkPdUlI0rhFhCeVN2Trn-EKNDnyzt2tAnkMULk3P4EUvKKZpB6RvThJ6p9Rea_eBQ9imQpptT0gC4lpmT5x0mftlmYAk5nbeg"

for ass in [assertion, xassertion]:
    a, b = ass.split("~")

    # print jwt.parse(a)
    print jwt.parse(a).payload
    assert jwt.parse(a).check_signature(MOCKMYID_KEY_DATA)

    # print jwt.parse(b)
    print jwt.parse(b).payload
    # assert jwt.parse(b).check_signature(RS256_KEY_DATA)

    print

# print b

from browserid import RemoteVerifier as Verifier
verifier = Verifier(["*"])

# aud = "http://myfavoritebeer.org"
print verifier.verify(assertion, audience=aud)

print make_certificate("test@mockmyid.com", email_keypair[0], "mockmyid.com", issuer_keypair[1])
