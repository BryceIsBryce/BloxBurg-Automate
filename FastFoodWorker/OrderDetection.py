import cv2
import numpy as np
import pyautogui
import os
import time

from .OrderProcess import BurgerOrder, FriesOrder, DrinkOrder, CompleteOrder

class ImageRecognitionAI:
    def __init__(self):
        self.BurgerTemplatesFolder = "FastFoodWorker/ToppingsTemplates"
        self.FriesTemplatesFolder = "FastFoodWorker/FriesTemplates"
        self.DrinkTemplatesFolder = "FastFoodWorker/DrinkTemplates"
        self.QuantityTemplates = "FastFoodWorker/QuantityTemplates"
        self.SizeTemplates = "FastFoodWorker/SizeTemplates"
        self.OrderArea = (650, 300, 1290, 440)

    def TakeScreenshot(self, area):
        Screenshot = pyautogui.screenshot(region=area)
        ScreenshotNP = np.array(Screenshot)
        ScreenshotNP = cv2.cvtColor(ScreenshotNP, cv2.COLOR_BGR2RGB)
        return ScreenshotNP

    def PreprocessImage(self, Image):
        Image = cv2.GaussianBlur(Image, (5, 5), 0)
        return Image

    def MatchBurgers(self, Screenshot):
        AllMatches = []

        ScreenshotGray = cv2.cvtColor(Screenshot, cv2.COLOR_BGR2GRAY)
        ScreenshotGray = self.PreprocessImage(ScreenshotGray)

        TermplateCoordinates = {}

        for TemplateName in os.listdir(self.BurgerTemplatesFolder):
            TemplatePath = os.path.join(self.BurgerTemplatesFolder, TemplateName)
            Template = cv2.imread(TemplatePath, cv2.IMREAD_COLOR)
            TemplateGray = cv2.cvtColor(Template, cv2.COLOR_BGR2GRAY)
            TemplateGray = self.PreprocessImage(TemplateGray)

            Res = cv2.matchTemplate(ScreenshotGray, TemplateGray, cv2.TM_CCOEFF_NORMED)
            _, MaxVal, _, MaxLoc = cv2.minMaxLoc(Res)
            
            topping, quantity = TemplateName.split('.')[0].split('-')
            print(f"Topping: {topping}, Quantity: {quantity}, Accuracy: {MaxVal*100:.2f}%")

            if MaxVal >= 0.89:
                Height, Width = TemplateGray.shape[:2]
                BottomRight = (MaxLoc[0] + Width, MaxLoc[1] + Height)
                TermplateCoordinates[TemplateName] = (MaxLoc, BottomRight)

                AllMatches.append((topping, int(quantity), MaxVal, MaxLoc[0], TemplateName))

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

        OrderedMatches = {}
        for k, v in sorted(matches.items(), key=lambda item: item[1]['position']):
            CropImg = Screenshot[v['coordinates'][0][1]:v['coordinates'][1][1], v['coordinates'][0][0]:v['coordinates'][1][0]]
            CropImg = cv2.cvtColor(CropImg, cv2.COLOR_BGR2GRAY)

            Template_1_path = os.path.join(self.QuantityTemplates, "1.png")
            Template_2_path = os.path.join(self.QuantityTemplates, "2.png")
            Template_1 = cv2.imread(Template_1_path, cv2.IMREAD_COLOR)
            Template_1Gray = cv2.cvtColor(Template_1, cv2.COLOR_BGR2GRAY)
            Template_2 = cv2.imread(Template_2_path, cv2.IMREAD_COLOR)
            Template_2Gray = cv2.cvtColor(Template_2, cv2.COLOR_BGR2GRAY)
            res_1 = cv2.matchTemplate(CropImg, Template_1Gray, cv2.TM_CCOEFF_NORMED)
            res_2 = cv2.matchTemplate(CropImg, Template_2Gray, cv2.TM_CCOEFF_NORMED)
            _, max_val_1, _, _ = cv2.minMaxLoc(res_1)
            _, max_val_2, _, _ = cv2.minMaxLoc(res_2)

            print(f"{k} Quantity Check - 1 Quantity Accuracy: {max_val_1*100:.2f}%, 2 Quantity Accuracy: {max_val_2*100:.2f}%")
            if max_val_2 > max_val_1:
                OrderedMatches[k] = 2
            else:
                OrderedMatches[k] = 1

        return OrderedMatches

    def MatchFries(self, Screenshot):
        ScreenshotGray = cv2.cvtColor(Screenshot, cv2.COLOR_BGR2GRAY)
        ScreenshotGray = self.PreprocessImage(ScreenshotGray)
        TermplateCoordinates = {}

        for TemplateName in os.listdir(self.FriesTemplatesFolder):
            TemplatePath = os.path.join(self.FriesTemplatesFolder, TemplateName)
            Template = cv2.imread(TemplatePath, cv2.IMREAD_COLOR)
            TemplateGray = cv2.cvtColor(Template, cv2.COLOR_BGR2GRAY)
            TemplateGray = self.PreprocessImage(TemplateGray)

            Res = cv2.matchTemplate(ScreenshotGray, TemplateGray, cv2.TM_CCOEFF_NORMED)
            _, MaxVal, _, MaxLoc = cv2.minMaxLoc(Res)

            if MaxVal >= 0.95:
                Height, Width = TemplateGray.shape[:2]
                BottomRight = (MaxLoc[0] + Width, MaxLoc[1] + Height)
                TermplateCoordinates[TemplateName] = (MaxLoc, BottomRight)

                FryType, FrySize = TemplateName.split('.')[0].split('-')
                print(f"Fry Type: {FryType}, Size: {FrySize}, Accuracy: {MaxVal*100:.2f}%")

                CropImg = Screenshot[MaxLoc[1]:MaxLoc[1] + Height, MaxLoc[0]:MaxLoc[0] + Width]
                CropImg = cv2.cvtColor(CropImg, cv2.COLOR_BGR2GRAY)
                SizeMatches = {}
                for SizeName in ['small', 'medium', 'large']:
                    SizeTemplatePath = os.path.join(self.SizeTemplates, f"{SizeName}.png")
                    SizeTemplate = cv2.imread(SizeTemplatePath, cv2.IMREAD_COLOR)
                    SizeTemplateGray = cv2.cvtColor(SizeTemplate, cv2.COLOR_BGR2GRAY)
                    ResSize = cv2.matchTemplate(CropImg, SizeTemplateGray, cv2.TM_CCOEFF_NORMED)
                    _, MaxValSize, _, _ = cv2.minMaxLoc(ResSize)
                    SizeMatches[SizeName] = MaxValSize
                    print(f"{FryType} Size Check - {SizeName} Size Accuracy: {MaxValSize*100:.2f}%")

                BestSize = max(SizeMatches, key=SizeMatches.get)
                if SizeMatches[BestSize] >= 0.9:
                    CropImgUpperHalf = CropImg[:Height//2, :]
                    FryTypeMatches = {}
                    for FryTemplateName in os.listdir(self.FriesTemplatesFolder):
                        FryTemplatePath = os.path.join(self.FriesTemplatesFolder, FryTemplateName)
                        FryTemplate = cv2.imread(FryTemplatePath, cv2.IMREAD_COLOR)
                        FryTemplateGray = cv2.cvtColor(FryTemplate, cv2.COLOR_BGR2GRAY)
                        FryTemplateGrayUpperHalf = FryTemplateGray[:FryTemplateGray.shape[0]//2, :]
                        
                        if CropImgUpperHalf.shape[0] >= FryTemplateGrayUpperHalf.shape[0] and CropImgUpperHalf.shape[1] >= FryTemplateGrayUpperHalf.shape[1]:
                            ResType = cv2.matchTemplate(CropImgUpperHalf, FryTemplateGrayUpperHalf, cv2.TM_CCOEFF_NORMED)
                            _, MaxValType, _, _ = cv2.minMaxLoc(ResType)
                            FryTypeName = FryTemplateName.split('-')[0]
                            if FryTypeName not in FryTypeMatches or FryTypeMatches[FryTypeName] < MaxValType:
                                FryTypeMatches[FryTypeName] = MaxValType
                    if FryTypeMatches:
                        BestFryType = max(FryTypeMatches, key=FryTypeMatches.get)
                        print(f"{FryType} Type Check - Best Match: {BestFryType}, Accuracy: {FryTypeMatches[BestFryType]*100:.2f}%")
                        if FryTypeMatches[BestFryType] >= 0.9:
                            return {BestFryType: BestSize}
                    else:
                        print("No Fry type matches found due to Size constraints.")
                return {}
        return {}

    def MatchDrink(self, Screenshot):
        ScreenshotGray = cv2.cvtColor(Screenshot, cv2.COLOR_BGR2GRAY)
        ScreenshotGray = self.PreprocessImage(ScreenshotGray)
        BestMatch = {"DrinkType": None, "DrinkSize": None, "accuracy": 0}

        for TemplateName in os.listdir(self.DrinkTemplatesFolder):
            TemplatePath = os.path.join(self.DrinkTemplatesFolder, TemplateName)
            Template = cv2.imread(TemplatePath, cv2.IMREAD_COLOR)
            TemplateGray = cv2.cvtColor(Template, cv2.COLOR_BGR2GRAY)
            TemplateGray = self.PreprocessImage(TemplateGray)

            Res = cv2.matchTemplate(ScreenshotGray, TemplateGray, cv2.TM_CCOEFF_NORMED)
            _, MaxVal, _, _ = cv2.minMaxLoc(Res)

            DrinkType, DrinkSize = TemplateName.split('.')[0].split('-')
            print(f"Drink Type: {DrinkType}, Size: {DrinkSize}, Accuracy: {MaxVal*100:.2f}%")

            if MaxVal > BestMatch["accuracy"]:
                BestMatch = {"DrinkType": DrinkType, "DrinkSize": DrinkSize, "accuracy": MaxVal}

        if BestMatch["accuracy"] >= 0.9:
            return {BestMatch["DrinkType"]: BestMatch["DrinkSize"]}
        else:
            return {}

    def CaptureAndProcessOrderV1(self):
        print("Capturing and processing burger order...")
        BurgerScreenshot = self.TakeScreenshot(self.OrderArea)
        BurgerOrderedMatches = self.MatchBurgers(BurgerScreenshot)
        print(f"Ordered matches found: {BurgerOrderedMatches}")

        print("Waiting for fries order...")
        time.sleep(3)

        print("Capturing and processing fries order...")
        FriesScreenshot = self.TakeScreenshot(self.OrderArea)
        FriesOrderedMatches = self.MatchFries(FriesScreenshot)
        print(f"Fries ordered matches found: {FriesOrderedMatches}")

        print("Waiting for Drink order...")
        time.sleep(3)

        print("Capturing and processing Drink order...")
        DrinkScreenshot = self.TakeScreenshot(self.OrderArea)
        DrinkOrderedMatches = self.MatchDrink(DrinkScreenshot)
        print(f"Drink ordered matches found: {DrinkOrderedMatches}")
        
        if BurgerOrderedMatches:
            BurgerOrder(BurgerOrderedMatches)
        else:
            print("No matching toppings found.")
            
        time.sleep(0.3)
            
        if FriesOrderedMatches:
            for Fry, Size in FriesOrderedMatches.items():
                FriesOrder(Fry, Size.capitalize())
            
        if DrinkOrderedMatches:
            for Drink, Size in DrinkOrderedMatches.items():
                DrinkOrder(Drink, Size.capitalize())
            
        time.sleep(0.3)
        
        CompleteOrder()

    def CaptureAndProcessOrderV2(self):
        StartTime = time.time()
        
        print("Capturing and processing burger order...")
        BurgerScreenshot = self.TakeScreenshot(self.OrderArea)
        BurgerOrderedMatches = self.MatchBurgers(BurgerScreenshot)
        print(f"Ordered matches found: {BurgerOrderedMatches}")
        
        if BurgerOrderedMatches:
            BurgerOrder(BurgerOrderedMatches)
        else:
            print("No matching toppings found.")
        
        Burgertime = time.time() - StartTime
        TimeToWait = max(3.5 - Burgertime, 0)
        print(f"Waiting {TimeToWait:.2f} seconds for fries order...")
        time.sleep(TimeToWait)

        StartTime = time.time()
        print("Capturing and processing fries order...")
        FriesScreenshot = self.TakeScreenshot(self.OrderArea)
        FriesOrderedMatches = self.MatchFries(FriesScreenshot)
        print(f"Fries ordered matches found: {FriesOrderedMatches}")
        
        if FriesOrderedMatches:
            for Fry, Size in FriesOrderedMatches.items():
                FriesOrder(Fry, Size.capitalize())
        
        FriesTime = time.time() - StartTime
        TimeToWait = max(3 - FriesTime, 0)
        print(f"Waiting {TimeToWait:.2f} seconds for Drink order...")
        time.sleep(TimeToWait)

        print("Capturing and processing Drink order...")
        DrinkScreenshot = self.TakeScreenshot(self.OrderArea)
        DrinkOrderedMatches = self.MatchDrink(DrinkScreenshot)
        print(f"Drink ordered matches found: {DrinkOrderedMatches}")
        
        if DrinkOrderedMatches:
            for Drink, Size in DrinkOrderedMatches.items():
                DrinkOrder(Drink, Size.capitalize())
        
        time.sleep(0.3)
        
        CompleteOrder()

if __name__ == "__main__":
    ai = ImageRecognitionAI()
    # ai.CaptureAndProcessOrderV2()
    while True:
        ai.CaptureAndProcessOrderV2()
        time.sleep(4)