# from kavenegar import *

#
# def send_otp_code(phone_number, code):
#     try:
#         api = KavenegarAPI('786A4F3855702B68736E4D7458524341674179335649675847454C365967774C446A4C45614257507336733D')
#         params = {
#             'sender': "2000660110",
#             'receptor': phone_number,
#             'message': f"کد تایید شما {code}",
#         }
#         response = api.sms_send(params)
#     except APIException as e:
#         print(e)
#     except HTTPException as e:
#         print(e)


def send_otp_code(phone_number, code):
    pass