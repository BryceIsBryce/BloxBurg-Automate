import cv2
import numpy as np
import pyautogui
import os
import time

from OrderProcess import BurgerOrder, FriesOrder, DrinkOrder, CompleteOrder

class ImageRecognitionAI:
    def __init__(self):
        self.BurgerTemplatesFolder = "ToppingsTemplates"
        self.FriesTemplatesFolder = "FriesTemplates"
        self.DrinkTemplatesFolder = "DrinkTemplates"
        self.OrderArea = (650, 300, 1290, 440)

    def TakeScreenshot(self, area):
        screenshot = pyautogui.screenshot(region=area)
        screenshot_np = np.array(screenshot)
        screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
        return screenshot_np

    def PreprocessImage(self, image):
        image = cv2.GaussianBlur(image, (5, 5), 0)
        return image

    def MatchBurgers(self, screenshot):
        AllMatches = []

        ScreenshotGray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        ScreenshotGray = self.PreprocessImage(ScreenshotGray)

        TermplateCoordinates = {}

        for TemplateName in os.listdir(self.BurgerTemplatesFolder):
            TemplatePath = os.path.join(self.BurgerTemplatesFolder, TemplateName)
            Template = cv2.imread(TemplatePath, cv2.IMREAD_COLOR)
            TemplateGray = cv2.cvtColor(Template, cv2.COLOR_BGR2GRAY)
            TemplateGray = self.PreprocessImage(TemplateGray)

            Res = cv2.matchTemplate(ScreenshotGray, TemplateGray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(Res)
            
            topping, quantity = TemplateName.split('.')[0].split('-')
            print(f"Topping: {topping}, Quantity: {quantity}, Accuracy: {max_val*100:.2f}%")

            if max_val >= 0.89:
                h, w = TemplateGray.shape[:2]
                bottom_right = (max_loc[0] + w, max_loc[1] + h)
                TermplateCoordinates[TemplateName] = (max_loc, bottom_right)

                AllMatches.append((topping, int(quantity), max_val, max_loc[0], TemplateName))

        AllMatches.sort(key=lambda x: (x[0], -x[2]))

        matches = {}
        for topping, quantity, accuracy, position, TemplateName in AllMatches:
            if topping not in matches or (matches[topping]['accuracy'] < accuracy):
                matches[topping] = {
                    'quantity': quantity, 
                    'accuracy': accuracy, 
                    'position': position, 
                    'coordinates': TermplateCoordinates[TemplateName]
                }

        if 'vegan_patty' in matches and 'meat_patty' in matches:
            if matches['vegan_patty']['position'] < matches['meat_patty']['position']:
                del matches['meat_patty']
            else:
                del matches['vegan_patty']

        ordered_matches = {}
        for k, v in sorted(matches.items(), key=lambda item: item[1]['position']):
            crop_img = screenshot[v['coordinates'][0][1]:v['coordinates'][1][1], v['coordinates'][0][0]:v['coordinates'][1][0]]
            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

            Template_1_path = os.path.join("QuantityTemplates", "1.png")
            Template_2_path = os.path.join("QuantityTemplates", "2.png")
            Template_1 = cv2.imread(Template_1_path, cv2.IMREAD_COLOR)
            Template_1_gray = cv2.cvtColor(Template_1, cv2.COLOR_BGR2GRAY)
            Template_2 = cv2.imread(Template_2_path, cv2.IMREAD_COLOR)
            Template_2_gray = cv2.cvtColor(Template_2, cv2.COLOR_BGR2GRAY)
            res_1 = cv2.matchTemplate(crop_img, Template_1_gray, cv2.TM_CCOEFF_NORMED)
            res_2 = cv2.matchTemplate(crop_img, Template_2_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val_1, _, _ = cv2.minMaxLoc(res_1)
            _, max_val_2, _, _ = cv2.minMaxLoc(res_2)

            print(f"{k} Quantity Check - 1 Quantity Accuracy: {max_val_1*100:.2f}%, 2 Quantity Accuracy: {max_val_2*100:.2f}%")
            if max_val_2 > max_val_1:
                ordered_matches[k] = 2
            else:
                ordered_matches[k] = 1

        return ordered_matches

    def MatchFries(self, screenshot):
        ScreenshotGray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        ScreenshotGray = self.PreprocessImage(ScreenshotGray)
        TermplateCoordinates = {}

        for TemplateName in os.listdir(self.FriesTemplatesFolder):
            TemplatePath = os.path.join(self.FriesTemplatesFolder, TemplateName)
            Template = cv2.imread(TemplatePath, cv2.IMREAD_COLOR)
            TemplateGray = cv2.cvtColor(Template, cv2.COLOR_BGR2GRAY)
            TemplateGray = self.PreprocessImage(TemplateGray)

            Res = cv2.matchTemplate(ScreenshotGray, TemplateGray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(Res)

            if max_val >= 0.95:
                h, w = TemplateGray.shape[:2]
                bottom_right = (max_loc[0] + w, max_loc[1] + h)
                TermplateCoordinates[TemplateName] = (max_loc, bottom_right)

                fry_type, fry_size = TemplateName.split('.')[0].split('-')
                print(f"Fry Type: {fry_type}, Size: {fry_size}, Accuracy: {max_val*100:.2f}%")

                crop_img = screenshot[max_loc[1]:max_loc[1] + h, max_loc[0]:max_loc[0] + w]
                crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
                size_matches = {}
                for size_name in ['small', 'medium', 'large']:
                    size_TemplatePath = os.path.join("SizeTemplates", f"{size_name}.png")
                    size_Template = cv2.imread(size_TemplatePath, cv2.IMREAD_COLOR)
                    size_Template_gray = cv2.cvtColor(size_Template, cv2.COLOR_BGR2GRAY)
                    res_size = cv2.matchTemplate(crop_img, size_Template_gray, cv2.TM_CCOEFF_NORMED)
                    _, max_val_size, _, _ = cv2.minMaxLoc(res_size)
                    size_matches[size_name] = max_val_size
                    print(f"{fry_type} Size Check - {size_name} Size Accuracy: {max_val_size*100:.2f}%")

                best_size = max(size_matches, key=size_matches.get)
                if size_matches[best_size] >= 0.9:
                    crop_img_upper_half = crop_img[:h//2, :]
                    fry_type_matches = {}
                    for fry_TemplateName in os.listdir(self.FriesTemplatesFolder):
                        fry_TemplatePath = os.path.join(self.FriesTemplatesFolder, fry_TemplateName)
                        fry_Template = cv2.imread(fry_TemplatePath, cv2.IMREAD_COLOR)
                        fry_Template_gray = cv2.cvtColor(fry_Template, cv2.COLOR_BGR2GRAY)
                        fry_Template_gray_upper_half = fry_Template_gray[:fry_Template_gray.shape[0]//2, :]
                        
                        if crop_img_upper_half.shape[0] >= fry_Template_gray_upper_half.shape[0] and crop_img_upper_half.shape[1] >= fry_Template_gray_upper_half.shape[1]:
                            res_type = cv2.matchTemplate(crop_img_upper_half, fry_Template_gray_upper_half, cv2.TM_CCOEFF_NORMED)
                            _, max_val_type, _, _ = cv2.minMaxLoc(res_type)
                            fry_type_name = fry_TemplateName.split('-')[0]
                            if fry_type_name not in fry_type_matches or fry_type_matches[fry_type_name] < max_val_type:
                                fry_type_matches[fry_type_name] = max_val_type
                    if fry_type_matches:
                        best_fry_type = max(fry_type_matches, key=fry_type_matches.get)
                        print(f"{fry_type} Type Check - Best Match: {best_fry_type}, Accuracy: {fry_type_matches[best_fry_type]*100:.2f}%")
                        if fry_type_matches[best_fry_type] >= 0.9:
                            return {best_fry_type: best_size}
                    else:
                        print("No fry type matches found due to size constraints.")
                return {}
        return {}

    def MatchDrink(self, screenshot):
        ScreenshotGray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        ScreenshotGray = self.PreprocessImage(ScreenshotGray)
        best_match = {"drink_type": None, "drink_size": None, "accuracy": 0}

        for TemplateName in os.listdir(self.DrinkTemplatesFolder):
            TemplatePath = os.path.join(self.DrinkTemplatesFolder, TemplateName)
            Template = cv2.imread(TemplatePath, cv2.IMREAD_COLOR)
            TemplateGray = cv2.cvtColor(Template, cv2.COLOR_BGR2GRAY)
            TemplateGray = self.PreprocessImage(TemplateGray)

            Res = cv2.matchTemplate(ScreenshotGray, TemplateGray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(Res)

            drink_type, drink_size = TemplateName.split('.')[0].split('-')
            print(f"Drink Type: {drink_type}, Size: {drink_size}, Accuracy: {max_val*100:.2f}%")

            if max_val > best_match["accuracy"]:
                best_match = {"drink_type": drink_type, "drink_size": drink_size, "accuracy": max_val}

        if best_match["accuracy"] >= 0.9:
            return {best_match["drink_type"]: best_match["drink_size"]}
        else:
            return {}

    def CaptureAndProcessOrderV1(self):
        print("Capturing and processing burger order...")
        burger_screenshot = self.TakeScreenshot(self.OrderArea)
        burger_ordered_matches = self.MatchBurgers(burger_screenshot)
        print(f"Ordered matches found: {burger_ordered_matches}")

        print("Waiting for fries order...")
        time.sleep(3)

        print("Capturing and processing fries order...")
        fries_screenshot = self.TakeScreenshot(self.OrderArea)
        fries_ordered_matches = self.MatchFries(fries_screenshot)
        print(f"Fries ordered matches found: {fries_ordered_matches}")

        print("Waiting for drink order...")
        time.sleep(3)

        print("Capturing and processing drink order...")
        drink_screenshot = self.TakeScreenshot(self.OrderArea)
        drink_ordered_matches = self.MatchDrink(drink_screenshot)
        print(f"Drink ordered matches found: {drink_ordered_matches}")
        
        if burger_ordered_matches:
            BurgerOrder(burger_ordered_matches)
        else:
            print("No matching toppings found.")
            
        time.sleep(0.3)
            
        if fries_ordered_matches:
            for fry, size in fries_ordered_matches.items():
                FriesOrder(fry, size.capitalize())
            
        if drink_ordered_matches:
            for drink, size in drink_ordered_matches.items():
                DrinkOrder(drink, size.capitalize())
            
        time.sleep(0.3)
        
        CompleteOrder()

    def CaptureAndProcessOrderV2(self):
        start_time = time.time()
        
        print("Capturing and processing burger order...")
        burger_screenshot = self.TakeScreenshot(self.OrderArea)
        burger_ordered_matches = self.MatchBurgers(burger_screenshot)
        print(f"Ordered matches found: {burger_ordered_matches}")
        
        if burger_ordered_matches:
            BurgerOrder(burger_ordered_matches)
        else:
            print("No matching toppings found.")
        
        burger_time = time.time() - start_time
        time_to_wait = max(3.5 - burger_time, 0)
        print(f"Waiting {time_to_wait:.2f} seconds for fries order...")
        time.sleep(time_to_wait)

        start_time = time.time()
        print("Capturing and processing fries order...")
        fries_screenshot = self.TakeScreenshot(self.OrderArea)
        fries_ordered_matches = self.MatchFries(fries_screenshot)
        print(f"Fries ordered matches found: {fries_ordered_matches}")
        
        if fries_ordered_matches:
            for fry, size in fries_ordered_matches.items():
                FriesOrder(fry, size.capitalize())
        
        fries_time = time.time() - start_time
        time_to_wait = max(3 - fries_time, 0)
        print(f"Waiting {time_to_wait:.2f} seconds for drink order...")
        time.sleep(time_to_wait)

        print("Capturing and processing drink order...")
        drink_screenshot = self.TakeScreenshot(self.OrderArea)
        drink_ordered_matches = self.MatchDrink(drink_screenshot)
        print(f"Drink ordered matches found: {drink_ordered_matches}")
        
        if drink_ordered_matches:
            for drink, size in drink_ordered_matches.items():
                DrinkOrder(drink, size.capitalize())
        
        time.sleep(0.3)
        
        CompleteOrder()

if __name__ == "__main__":
    ai = ImageRecognitionAI()
    # ai.CaptureAndProcessOrderV2()
    while True:
        ai.CaptureAndProcessOrderV2()
        time.sleep(4)