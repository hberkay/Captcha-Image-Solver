# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from webdriver_manager.chrome import ChromeDriverManager
# from openai import OpenAI
import base64

class CaptchaSolver:
    def __init__(self):
        # OpenAI client initialization
        # self.client = OpenAI(api_key='YOUR-API-KEY')
        
        # Chrome options 
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--start-maximized')
        
        # Additional options to prevent bot detection
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize ChromeDriver with Selenium Manager
        self.driver = webdriver.Chrome(
            service=webdriver.ChromeService(ChromeDriverManager().install()),
            options=self.options
        )
        self.wait = WebDriverWait(self.driver, 10)

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
#I don't know if chatgpt is working properly. I didn't pay for the token
#but 4o-Mini detects the given object from the picture and returns the coordinates correctly thanks to the prompt below.
    """
    def send_to_chatgpt(self, image_path):
        try:
            base64_image = self.encode_image(image_path)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": \"""You have an IQ of 300 and your profession is solving captchas.
                                            Don't write any explanations.
                                            In the image, there is a captcha, and it is asking you to find the object mentioned in the text among the images.
                                            I only want you to return the position of the object mentioned in the text.
                                            For the position, I expect a 2D matrix response.
                                            The top-left square's position is [0][0], and the bottom-right square's position is [2][2].
                                            If the object is not present, just say "continue".

                                            Example response:
                                            [1][2],[0][0],[1][1]\"""  
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "data:image/png;base64," + base64_image
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            print("ChatGPT Response:", response.choices[0].message.content)
            return response.choices[0].message.content

        except Exception as e:
            print(f"ChatGPT API Error: {str(e)}")
            return None
    """

    def click_tiles(self, coordinates):
        """
        Clicks captcha tiles based on given coordinates
        Example coordinates: "[0][0],[1][2],[2][1]"
        """
        try:
            # Convert string format coordinates into a list
            coord_list = coordinates.replace(" ", "").split(",")
            
            for coord in coord_list:
                # Convert [x][y] format coordinates to numbers
                row = int(coord.split("][")[0].replace("[", ""))
                col = int(coord.split("][")[1].replace("]", ""))
                
                # Calculate tabindex value (starting from 4)
                tabindex = 4 + (row * 3) + col
                
                # Find the corresponding cell in the table by tabindex and click it
                tile = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    f".rc-imageselect-tile[tabindex='{tabindex}']"
                )
                tile.click()
                time.sleep(0.5)  # Short wait between clicks
            
            return True
            
        except Exception as e:
            print(f"Click error: {str(e)}")
            return False

    def solve_captcha(self, url):
        try:
            # Go to website
            self.driver.get(url)
            print("Website opened")

            # Find and switch to reCAPTCHA iframe
            iframe = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[title*='reCAPTCHA']")
            ))
            self.driver.switch_to.frame(iframe)
            print("Switched to iframe")

            # Find and click checkbox
            checkbox = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".recaptcha-checkbox-border")
            ))
            time.sleep(1)
            checkbox.click()
            print("Captcha checkbox clicked")

            # Switch back to main frame
            self.driver.switch_to.default_content()
            
            # Wait for challenge iframe
            time.sleep(2)
            
            # Find and switch to the challenge iframe using name attribute
            challenge_iframe = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[name^='c-']")  # iframe with name starting with 'c-'
            ))
            self.driver.switch_to.frame(challenge_iframe)
            print("Switched to challenge frame")
            
            # Wait for challenge content to load
            time.sleep(1)
            
            # Take screenshot of the entire iframe content
            screenshot_path = "captcha_challenge.png"
            body_element = self.driver.find_element(By.TAG_NAME, "body")
            body_element.screenshot(screenshot_path)
            print("Challenge screenshot saved")
            
            # Sample coordinates for testing (normally coming from ChatGPT)
            example_coordinates = "[0][0],[1][2],[2][1]"
            self.click_tiles(example_coordinates)
            
            return True

        except TimeoutException:
            print("Timeout: Elements not found")
            return False
        except Exception as e:
            print(e)
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed")

def main():
    solver = CaptchaSolver()
    try:
        # Enter URL here
        url = "URL"  # Replace with your target site URL
        result = solver.solve_captcha(url)
        
        if result:
            print("Operation completed!")
        else:
            print("Operation failed!")
            
        time.sleep(3)
        
    finally:
        solver.close()

if __name__ == "__main__":
    main()
