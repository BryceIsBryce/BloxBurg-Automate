import time
import autoit
import keyboard

SPEED = 2
# 10; 2

FAST_TIME = 0.015
SLOW_TIME = 0.5

time.sleep(1)

class ToppingTypes:
    LETTUCE = "Lettuce"
    TOMATO = "Tomato"
    MEAT_PATTY = "Meat Patty"
    VEGAN_PATTY = "Vegan Patty"
    CHEESE = "Cheese"
    ONION = "Onion"

class FryTypes:
    REGULAR = "Regular"
    STUFFED = "Stuffed"
    ONION = "Onion"

class DrinkTypes:
    REGULAR = "Regular"
    JUICE = "Juice"
    MILKSHAKE = "Milkshake"

class OrderSizes:
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"

class MousePositions:
    BOTTOM_BUN = (1660, 730)
    TOP_BUN = (1660, 320)
    LETTUCE = (1660, 670)
    TOMATO = (1660, 590)
    MEAT_PATTY = (1610, 520)
    VEGAN_PATTY = (1710, 520)
    CHEESE = (1660, 460)
    ONION = (1660, 390)
    BURGER_TOPPINGS_PAGE = (1850, 350)
    
    FRIES_PAGE = (1850, 460)
    REGULAR_FRIES = (1590, 400)
    STUFFED_FRIES = (1590, 520)
    ONION_FRIES = (1590, 640)
    
    DRINKS_PAGE = (1850, 570)
    REGULAR_DRINK = (1590, 400)
    JUICE_DRINK = (1590, 520)
    MILKSHAKE_DRINK = (1590, 640)
    
    SMALL_SIZE = (1730, 400)
    MEDIUM_SIZE = (1730, 520)
    LARGE_SIZE = (1730, 640)
    
    SUBMIT = (1850, 690)

def MoveAndClick(Position: tuple, Delay: float = SLOW_TIME, SliceDelay: bool = True):
    if CancelRequested():
        print("Mouse action canceled.")
        return
    print(f"Moving to {Position} and clicking")
    autoit.mouse_move(Position[0], Position[1], speed=SPEED)
    time.sleep(Delay)
    autoit.mouse_click()
    time.sleep(Delay / 2 if SliceDelay else Delay)

def AddTopping(Topping: str, Quantity: int):
    print(f"Selecting {Topping}")
    ToppingPositions = {
        ToppingTypes.LETTUCE: MousePositions.LETTUCE,
        ToppingTypes.TOMATO: MousePositions.TOMATO,
        ToppingTypes.MEAT_PATTY: MousePositions.MEAT_PATTY,
        ToppingTypes.VEGAN_PATTY: MousePositions.VEGAN_PATTY,
        ToppingTypes.CHEESE: MousePositions.CHEESE,
        ToppingTypes.ONION: MousePositions.ONION
    }
    for _ in range(Quantity):
        MoveAndClick(ToppingPositions[Topping.replace("_", " ").title()], FAST_TIME)
        if CancelRequested():
            print("Canceling request.")
            return
        time.sleep(SLOW_TIME / 2)

def BurgerOrder(Toppings: dict):
    if CancelRequested():
        print("Canceling request.")
        return
    print("Starting burger stacking...")
    MoveAndClick(MousePositions.BURGER_TOPPINGS_PAGE, SliceDelay=False)
    MoveAndClick(MousePositions.BOTTOM_BUN, FAST_TIME)
    for Topping, Quantity in Toppings.items():
        AddTopping(Topping, Quantity)
        if CancelRequested():
            print("Canceling request.")
            return
    MoveAndClick(MousePositions.TOP_BUN, FAST_TIME)
    print("Burger stacking completed.")

def FriesOrder(FryType: str, FrySize: str):
    if CancelRequested():
        print("Canceling request.")
        return
    print("Starting fries order...")
    MoveAndClick(MousePositions.FRIES_PAGE, SliceDelay=False)
    FryTypePositions = {
        FryTypes.REGULAR: MousePositions.REGULAR_FRIES,
        FryTypes.STUFFED: MousePositions.STUFFED_FRIES,
        FryTypes.ONION: MousePositions.ONION_FRIES
    }
    FrySizePositions = {
        OrderSizes.SMALL: MousePositions.SMALL_SIZE,
        OrderSizes.MEDIUM: MousePositions.MEDIUM_SIZE,
        OrderSizes.LARGE: MousePositions.LARGE_SIZE
    }
    MoveAndClick(FryTypePositions[FryType.title()], FAST_TIME)
    MoveAndClick(FrySizePositions[FrySize.title()], FAST_TIME)
    print("Fries order completed.")

def DrinkOrder(DrinkType: str, DrinkSize: str):
    if CancelRequested():
        print("Canceling request.")
        return
    print("Starting drink order...")
    MoveAndClick(MousePositions.DRINKS_PAGE, SliceDelay=False)
    DrinkTypePositions = {
        DrinkTypes.REGULAR: MousePositions.REGULAR_DRINK,
        DrinkTypes.JUICE: MousePositions.JUICE_DRINK,
        DrinkTypes.MILKSHAKE: MousePositions.MILKSHAKE_DRINK
    }
    DrinkSizePositions = {
        OrderSizes.SMALL: MousePositions.SMALL_SIZE,
        OrderSizes.MEDIUM: MousePositions.MEDIUM_SIZE,
        OrderSizes.LARGE: MousePositions.LARGE_SIZE
    }
    MoveAndClick(DrinkTypePositions[DrinkType.title()], FAST_TIME)
    MoveAndClick(DrinkSizePositions[DrinkSize.title()], FAST_TIME)
    print("Drink order completed.")
    
def CompleteOrder():
    MoveAndClick(MousePositions.SUBMIT, 0.5)

def CancelRequested():
    return keyboard.is_pressed('space')

# Example usage
if __name__ == "__main__":
    try:
        Toppings = {
            ToppingTypes.VEGAN_PATTY: 1,
            ToppingTypes.CHEESE: 1,
            ToppingTypes.ONION: 2
        }
        BurgerOrder(Toppings)
        FriesOrder(FryTypes.REGULAR, OrderSizes.MEDIUM)
        DrinkOrder(DrinkTypes.JUICE, OrderSizes.LARGE)
        CompleteOrder()
    except KeyboardInterrupt:
        print("Program exited.")
