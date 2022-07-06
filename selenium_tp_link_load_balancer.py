from selenium import webdriver  
import time  
from selenium.webdriver.common.keys import Keys  
from pyvirtualdisplay import Display
vdisplay = Display(visible=0, size=(1024, 768))
vdisplay.start()

print("sample test case started") 
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)  
#driver=webdriver.firefox()  
#driver=webdriver.ie()  
#maximize the window size  
driver.maximize_window()  
#navigate to the url  
driver.get("https://www.google.com/")  
#identify the Google search text box and enter the value  
driver.find_element_by_name("q").send_keys("javatpoint")  
time.sleep(3)  
#click on the Google search button  
driver.find_element_by_name("btnK").send_keys(Keys.ENTER)  
time.sleep(3)  
#close the browser  
driver.close()  
print("sample test case successfully completed")  
