import time
from selenium import webdriver

# driver = webdriver.Firefox()
# driver.get("http://www.baidu.com")

# driver.find_element_by_id("kw").clear()
# driver.find_element_by_id("kw").send_keys("Python")
# driver.find_element_by_id("su").click()
# time.sleep(5)
# driver.quit()


driver = webdriver.Chrome()
driver.get("http://www.baidu.com")
print(driver.title)
time.sleep(5)
driver.quit()