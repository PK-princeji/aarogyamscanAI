import smtplib
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("princeji3242@gmail.com", "dszp ycyj eubz xypr")
server.quit()
print("SMTP test successful!")
