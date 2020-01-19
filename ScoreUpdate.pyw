import requests
import smtplib
import time
from email.mime.text import MIMEText
"""
Example:
"j_username" : "106502017",
"j_password" : "12345678",
"gmail_user" : "abcdefg@gmail.com",
"gmail_pass" : "12345678"
"""
user_info = {
	"j_username" : "",
	"j_password" : "",
	"gmail_user" : "",
	"gmail_pass" : ""
}
academic = "1081"

now_score = {}

def check_connect():
	try:
		_ = requests.get("https://www.google.com")
		return True
	except requests.ConnectionError:
		pass
	return False

def send_mail(content):
	msg = MIMEText(content)
	msg["Subject"] = "成績更新！"
	msg["From"] = user_info["gmail_user"]
	msg["To"] = user_info["gmail_user"]

	server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
	server.ehlo()
	server.login(user_info["gmail_user"], user_info["gmail_pass"])
	server.send_message(msg)
	server.quit()

def main():
	while True:
		# Check if it has network
		if check_connect():
			# Get login NID
			r = requests.get("https://portal.ncu.edu.tw/login", allow_redirects=False)
			NID = r.cookies["NID"]

			# Get temp JSESSIONID
			r = requests.get("https://portal.ncu.edu.tw/login")
			JSESSIONID = r.cookies["JSESSIONID"]

			login_cookies = {
				"JSESSIONID" : JSESSIONID,
				"NID" : NID,
				"TS01f80378" : "",
				"BIGipServerpool-cis" : "",
				"PHPSESSID" : "",
			}

			r = requests.post("https://portal.ncu.edu.tw/j_spring_security_check", cookies=login_cookies, data=user_info, allow_redirects=False)

			# Update JSESSIONID
			login_cookies["JSESSIONID"] = r.cookies["JSESSIONID"]

			r = requests.get("https://portal.ncu.edu.tw/system/show/162", cookies=login_cookies)
			# Update cookies
			login_cookies["TS01f80378"] = r.cookies["TS01f80378"]
			login_cookies["BIGipServerpool-cis"] = r.cookies["BIGipServerpool-cis"]
			login_cookies["PHPSESSID"] = r.cookies["PHPSESSID"]

			r = requests.get("https://cis.ncu.edu.tw/ScoreInquiries/student/student_record.php", cookies=login_cookies)

			subr = r.text.split("<td>" + academic + "<td>")[1:-2]

			for i in range(len(subr)):
				subr[i] = subr[i].split("<tr class=list1>")[0]
				subr[i] = subr[i].split(" ", 1)[1]
				subr[i] = subr[i].split("<td>")

			# First time update
			if not now_score:
				for sub in subr:
					now_score.update({sub[0] : sub[2]})
			else:
				content = "成績更新！\n"
				update = False
				for sub in subr:
					if now_score[ sub[0] ] != sub[2]:
						update = True
						now_score.update({sub[0] : sub[2]})
						content += "科目: " + sub[0] + " 成績為 " + sub[2] + "\n"
				if update:
					send_mail(content)

		for key in now_score:
			print(key + " -- " + now_score[key])
		time.sleep(60)

if __name__=="__main__":
	main()