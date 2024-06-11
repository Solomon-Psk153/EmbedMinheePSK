import smtplib  # SMTP 사용을 위한 모듈
import re  # Regular Expression을 활용하기 위한 모듈
from email.mime.multipart import MIMEMultipart  # 메일의 Data 영역의 메시지를 만드는 모듈
from email.mime.text import MIMEText  # 메일의 본문 내용을 만드는 모듈
from email.mime.image import MIMEImage  # 메일의 이미지 파일을 base64 형식으로 변환하기 위한 모듈
import secrets, string # 난수, 문자열 값들을 조회하기 위한 모듈

class MailProvider(object):
    def __init__(self, dest, subject, code):
        self.dest=dest
        self.subject=subject
        self.code=code
    
    def sendMail(self):
        
        # smtp 메일을 보내기 위해 설정해야 하는 값들, 원래는 앱 비밀번호를 파일로 철저하게 관리해야 한다.
        gmailSmtpServer = "smtp.gmail.com"
        gmailPort = 465
        myAccount = "psk153777@gmail.com"
        myPassword = "fznl rudj ndua wihu"
        
        # 안전한 매일을 전송하기 위한 설정과 로그인
        smtp = smtplib.SMTP_SSL(gmailSmtpServer, gmailPort)
        smtp.login(myAccount, myPassword)
        
        # 멀티파트(파일도 첨부 가능)로 메일을 보내기 위해서 목적지와 내용을 적음
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = myAccount
        msg['To'] = self.dest
        
        body = self.ContentTemplate(
                self.subject,
                self.code
            )
		
		# 메일의 내용
        msg.attach(MIMEText(body, 'html'))
        
        try:
			# 메일을 보내고 오류가 없다면, 메일을 성공적으로 보냈다고 리턴과 응답 코드를 튜플 형식으로 보냄
            smtp.sendmail(myAccount, self.dest, msg.as_string())
            return {'message': 'send exist email success'}, 201
        except smtplib.SMTPDataError as e:
            return {'message': 'check does email accepted, server policy, email setting'}, 550
        except Exception as e:
            return {'message': 'email not found:{}'.format(e)}, 404
        
	# 메일에 인증코드를 보내기 위해 문자열 조정 후
    @staticmethod
    def randomCodeCreator():
        return ''.join(
            secrets.choice(
                string.ascii_uppercase + string.digits
                ) for _ in range(8)
            )
    
    # 메일의 형식 문자열
    @staticmethod
    def ContentTemplate(subject, code):
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    width: 80%;
                    margin: auto;
                    background: white;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    text-align: center;
                    padding: 10px 0;
                }}
                .content {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .footer {{
                    background-color: #4CAF50;
                    color: white;
                    text-align: center;
                    padding: 10px 0;
                }}
                .code {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{subject}</h1>
                </div>
                <div class="content">
                    <p>다음은 요청하신 인증 코드입니다:</p>
                    <p class="code">{code}</p>
                </div>
                <div class="footer">
                    <p>이 메일은 자동 생성된 메일입니다. 회신하지 마세요.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
