from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys


user_id=input('Enter User Id of your Fb Account :')  # Take user id and password as input from the user
password=input('Enter the password :')

print(user_id)
print(password)

cd='C:\\webdrivers\\chromedriver.exe'


browser= webdriver.Chrome(cd)
browser.get('https://www.facebook.com/')


user_box = browser.find_element_by_id("email")       # For detecting the user id box
user_box.send_keys(user_id)                                               # Enter the user id in the box 

password_box = browser.find_element_by_id("pass")    # For detecting the password box
password_box.send_keys(password)                                          # For detecting the password in the box

login_box = browser.find_element_by_id("u_0_b")      # For detecting the Login button
login_box.click()

time.sleep(20)

k='//*[@id="home_birthdays"]/div/div/div/div/a/div/div/span/span[2]'
n=browser.find_element_by_xpath(k).get_attribute('textContent')
 # To get the number of friends to be wished
num=n[0]
num=int(num)
print(num)


message= "Happy Birthday !!"
browser.get('https://www.facebook.com/events/birthdays/') 
#time.sleep(3)

bday_list=browser.find_elements_by_xpath("//*[@class ='enter_submit uiTextareaNoResize uiTextareaAutogrow uiStreamInlineTextarea inlineReplyTextArea mentionsTextarea textInput']") 

c=0
for element in bday_list: 
    element_id = str(element.get_attribute('id')) 
    XPATH = '//*[@id ="' + element_id + '"]'
    post = browser.find_element_by_xpath(XPATH) #To fetch the box where to enter text
    post.send_keys("Happy Birthday, Best wishes.") # To enter the bday wish
    #time.sleep(1)
    post.send_keys(Keys.RETURN) #To send the wish
    c=c+1
    if(c>num):  # This prevents putting wishes for belated birthday
        break

browser.quit()
