import random, time, pickle, math
import numpy as np
import matplotlib.pyplot as plt
from FAQ import FAQ
from roulette import roulette
from rocket import rocket
from enemy_names import enemy_names, enemy_types
from list_of_equipment_perks import weapon_perks, armor_perks, weapon_names, armor_names_head, armor_names_body, armor_names_boots, armor_names_legs
''' Alpha 0.0.12 '''

class Player:##########################################################################
    def __init__(self, farm, zoo, statistics, pet, name, birja) -> None:############################# 
        self.name = name
        self.money = 10_000_000_000_000#################################
        self.farm = farm
        self.zoo = zoo
        self.statistics = statistics
        self.pet = pet
        self.birja = birja
        self.loans = []
        self.bankrupt_turns = 11
          
    def save_to_file(self, filename):# Сохранение Player
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
              
    def print_available_animals(self): # доступные к покупке животные
        print("Доступные для покупки животные:")
        for i, animal in enumerate(self.farm.animals):
            print(f"{i}: {animal['name']} (Цена: {animal['price']}$)")
            
    def print_available_food(self): # доступная к покупке еда
        print('Доступная для покупки еда:')
        for i, food in enumerate(self.farm.food):
            print(f"{i}: {food['type']} (Цени: {food['price']}$)")
    
    def print_available_animals_zoo(self): 
        print("Доступные для покупки животные:")
        for i, animal in enumerate(self.zoo.animals):
            price = format_money(animal['price'])# преобразование денег в более удобный вид
            print(f"{i}: {animal['name']} (Цена: {price}$) (Популярность: {animal['popularity']})")
          
    def print_available_attraction(self): 
        print("Доступные для покупки аттракционы:")
        for i, attraction in enumerate(self.zoo.attraction):
            price = format_money(attraction['price'])
            print(f"{i}: {attraction['name']} (Цена: {price}$) (Популярность: {attraction['popularity']})")
    
    def print_trees_to_buy(self): # пишет доступные для покупки деревья
        print()
        for i, tree in enumerate(self.farm.trees_to_buy):
            print(f'{i+1}: {tree['Type']} ({tree['Cost']}$)')
    
    def choose_stock_to_buy(self):# выбор акций к покупке
        while True:
            self.show_companies()
            company_choice = input("Введите номер компании, которое хотите купить (или -1 для выхода): ")
            if company_choice == '-1':
                break
            valid_choice = digit_check(company_choice)
            if 0 <= valid_choice < len(self.birja.companies):
                amount = input("Введите количество: ")
                valid_amount = digit_check(amount)
                self.buy_stock(valid_choice, valid_amount)
            else:
                print("\nНекорректный номер компании. Попробуйте снова.")  
    
    def choose_trees_to_buy(self): # основной цикл выбора и покупки дерева
        while True:
            total_money = format_money(self.money)
            print(f'\n{total_money}$')
            self.print_trees_to_buy()
            choice = digit_check(input('Введите индекс дерева, которое хотите купить (0 - для выхода): '))
            
            if choice == 0:
                break
            
            if 0 < choice <= len(self.farm.trees_to_buy):
                amount = digit_check(input('Введите количество: '))
                self.buy_trees(choice, amount)
            else:
                print('Некорректный ввод')
    
    def Birja(self):# меню биржи
        print('\nЧто бы вы хотели?'
              '\n(1) - Торговать на бирже'
              '\n(2) - Посмотреть свой портфель'
              '\n(3) - Продать Акции'
              '\n(4) - График цен на акции')
        birja_choice = input()
        
        match birja_choice:
            case '1':
                self.choose_stock_to_buy()
            case '2':
                self.show_portfolio()
                pause()
            case '3':
                self.choose_stock_to_sell()
            case '4':
                self.birja.plot_price_history()
            
    def show_companies(self):# показать акции компаний которые можно купить 
        for i, company in enumerate(self.birja.companies):
            print(f'{i}: {company["Name"]}. Кол-во доступных акций: {company["Amount"]}. Цена каждой: {format_money(company["Price"])}$')
            print(f'Общая стоимость всех акций компании: {format_money(round(company["Amount"] * company["Price"], 2))} $')

    def buy_stock(self, company_index, amount):# функция покупки акций
        stock = self.birja.companies[company_index]
        total_cost = stock['Price'] * amount
        if self.money >= total_cost and stock['Amount'] >= amount:
            self.money -= total_cost
            self.statistics.add_statistics(total_cost, 'расход')
            stock['Amount'] -= amount
            self.birja.portfolio[company_index]['Amount'] += amount
            self.birja.portfolio[company_index]['InitialPrice'] = stock['Price']
            print(f'\nПотрачено {format_money(total_cost)}$')
            print(f'Куплено {amount} {stock["Name"]}')
        else:
            print('\nНедостаточно средств для покупки или количество введенных акций больше предложения на рынке')

    def show_portfolio(self):# показать акции в портфеле
        counter = 0
        for i, stock in enumerate(self.birja.portfolio):
            if stock['Amount'] > 0:
                print(f'{i}: {stock["Name"]}: количество - {stock["Amount"]}, цена за единицу - {stock["Price"]}, '
                    f'цена при покупке: {stock["InitialPrice"]}, '
                    f'изменение цены с момента покупки: {stock["PriceChange"]:.2f}% ')
                print("Введите номер компании, которое хотите продать (или -1 для выхода): ")
            else:
                counter += 1
            if counter == len(self.birja.portfolio):
                print('У вас в данный момент нет акций в портфеле')
    
    def choose_stock_to_sell(self):# выбор акций на продажу
        while True:
            self.show_portfolio()
            company_choice = input()
            if company_choice == '-1':
                break
            valid_choice = digit_check(company_choice)
            if 0 <= valid_choice < len(self.birja.portfolio):
                amount = input("Введите количество: ")
                valid_amount = digit_check(amount)
                self.sell_stock(valid_choice, valid_amount)
            else:
                print("\nНекорректный номер компании. Попробуйте снова.")
        
    def sell_stock(self, company_index, amount):# функция продажи акций 
        stock = self.birja.portfolio[company_index]
        total_cost = stock['Price'] * amount
        if stock["Amount"] >= amount:
            self.money += total_cost
            self.statistics.add_statistics(total_cost, 'доход')
            stock["Amount"] -= amount
            self.birja.companies[company_index]['Amount'] += amount
            stock['InitialPrice'] = self.birja.companies[company_index]['Price']
            print(f'\nЗаработано {total_cost}$')
            print(f'Продано {amount} {stock["Name"]}')
        else:
            print('У вас нет столько акций этой компании')
    
    def sell_fruits(self):
        while True:
            self.farm.show_fruits()
            income = 0
            print('\nВы хотите продать какой то тип фруктов или все?'
                '\n(1) - Вид    (2) - Все    (3) - Выход')
            match input():
                case '1':
                    print('\nКакой вид фруктов вы бы хотели продать?')
                    choice = input().capitalize()
                    income = sum(fruit.price for fruit in self.farm.fruits if fruit.type == choice)  # прибыль с проданых фруктов
                    self.money += income
                    self.fruits = [fruit for fruit in self.farm.fruits if fruit.type != choice]  # удаление проданых фруктов
                    if income == 0:
                        print('\nУ вас нет таких фруктов')
                    else:
                        print(f'\nС этой продажи вы заработали {income}$')
                    
                case '2':
                    income = sum(fruit.price for fruit in self.farm.fruits) # прибыль с проданых фруктов
                    self.money += income
                    self.farm.fruits = [] # удаление проданых фруктов
                    if income == 0:
                        print('\nУ вас нет фруктов!!!')
                    else:
                        print(f'\nС этой продажи вы заработали {income}$')

                case _:
                    break
    
    def auto_sell(self):
        global auto_sell_pos
        print('\nХотите включить автопродажу фруктов?'
              '\n(1) - Да    (2) - Нет')
        match input():
            
            case '1':
                self.farm.auto_sell_pos = True
                
            case '2':
                self.farm.auto_sell_pos = False
            
            case _:
                print('Некоректный выбор')
            
    def buy_animals(self, animal_index, amount): # функция покупки животных
        animal = self.farm.animals[animal_index]
        total_cost = animal['price'] * amount
        if self.money >= total_cost:
            self.money -= total_cost
            self.statistics.add_statistics(total_cost, 'расход') # учет статистики расходов
            animal['count'] += amount
            print(f'\nПотрачено {total_cost}$')
            print(f'Куплено {amount} {animal["name"]}')
        else:
            print("\nНедостаточно средств для покупки.")
    
    def buy_food(self, food_index, amount): # функция покупки еды
        food = self.farm.food[food_index]
        total_cost = food['price'] * amount
        if self.money >= total_cost:
            self.money -= total_cost
            self.statistics.add_statistics(total_cost, 'расход') # учет статистики расходов
            food['count'] += amount
            print(f'\nПотрачено {total_cost}$')
            print(f'Куплено {amount} {food["type"]}')
        else:
            print("Недостаточно средств для покупки.")
    
    def buy_animals_zoo(self, animal_index, amount):
        animal = self.zoo.animals[animal_index]
        total_cost = animal['price'] * amount
        if self.money >= total_cost and self.zoo.total_animals < self.zoo.workers * 50:
            self.money -= total_cost
            self.statistics.add_statistics(total_cost, 'расход') # учет статистики расходов
            animal['count'] += amount
            print(f'\nПотрачено {total_cost}$')
            print(f'Куплено {amount} {animal["name"]}')
        else:
            print("Недостаточно средств для покупки или работников чтобы ухаживать за всеми животными.")
    
    def buy_attraction(self, attraction_index, amount):
        attraction = self.zoo.attraction[attraction_index]
        total_cost = attraction['price'] * amount
        if self.money >= total_cost:
            self.money -= total_cost
            self.statistics.add_statistics(total_cost, 'расход') # учет статистики расходов
            attraction['count'] += amount
            print(f'\nПотрачено {total_cost}$')
            print(f'Куплено {amount} {attraction["name"]}')
        else:
            print("Недостаточно средств для покупки.")
    
    def buy_trees(self, index, amount): # покупка дерева
        index -= 1
        if self.money >= self.farm.trees_to_buy[index]['Cost'] * amount:
            self.money -= self.farm.trees_to_buy[index]['Cost'] * amount
            type = self.farm.trees_to_buy[index]['Type']
            fruit = type
            for i in range(amount):
                age = random.randint(1, 100)
                tree = Tree(fruit, type, age)
                self.farm.trees.append(tree)
        else:
            print('Недостаточно средств для покупки')
      
    def upgrades(self): # Магазин
        while True:
            total_money = format_money(self.money)
            print(f'\nУ вас {total_money} денег.'
                   '\nЧто вы хотите купить?'
                   '\n(1) - Поля'
                   '\n(2) - Растения'
                   '\n(3) - Скот'
                   '\n(4) - Еду для скота'
                   '\n(5) - Рабочих (Ухаживают за животными)'
                   '\n(6) - Фермеров (ухаживают за растениями)'
                   '\n(7) - Автоматическая поставка корма'
                   '\n(8) - Информация о ферме'
                   '\n(0) - Выход')
            shop_choice = input()
            
            match shop_choice:
                case '1': # поля
                    print('\n(1) - купить (10 000$) (1 000 растений)'
                          '\n(2) - продать')
                    field_choice = input()
                    match field_choice:
                        case '1':
                            print('\nВведите количество полей для покупки')
                            count = input()
                            valid_count = digit_check(count)
                            if self.money >= valid_count * 10_000:
                                self.money -= valid_count * 10_000
                                self.statistics.add_statistics(valid_count * 10_000, 'расход') # Учет трат в статистику
                                self.farm.increase_area(valid_count)
                                print(f'\nПоздравляем, вы приобрели {valid_count} новых полей')
                            else:
                                print(f'\nУ вас не хватает {valid_count * 10_000 - self.money}$ на эту покупку')
                        
                        case '2':
                            print('\nСколько полей хочешь продать?')
                            num_field = input()
                            valid_num = digit_check(num_field)
                            if (self.farm.area - valid_num) < 0:
                                print('\nВы не можете продать полей больше чем у вас есть')
                            else:
                                print(f"\nВы успешно продали {valid_num} полей за {valid_num * 5000}")
                                self.farm.area -= valid_num
                                self.money += valid_num * 5000
                                               
                case '2': # растения
                    print('\nЧто будем делать дальше?'
'''
(1) - Купить деревья          (4) - Продать фрукты     
(2) - Показать деревья        (5) - Автопродажа фруктов
(3) - Показать фрукты                     
''')
                    match input():
                        case '1':
                            self.choose_trees_to_buy()
                        case '2':
                            self.farm.show_my_trees()
                            pause()
                        case '3':
                            self.farm.show_fruits()
                            pause()
                        case '4':
                            self.sell_fruits()
                        case '5':
                            self.auto_sell()
       
                case '3': # животные
                    while True:
                        total_money = format_money(self.money)
                        print(f'\n{total_money}$')
                        self.print_available_animals()
                        animal_index = int(input("Введите номер животного, которое хотите купить (или -1 для выхода): "))
                        
                        if animal_index == -1:
                            break
                        
                        if 0 <= animal_index < len(self.farm.animals):
                            amount = int(input("Введите количество: "))
                            self.buy_animals(animal_index, amount)
                        else:
                            print("\nНекорректный номер животного. Попробуйте снова.")  

                case '4': # еда для животных
                    while True:
                        total_money = format_money(self.money)
                        print(f'\n{total_money}$')
                        self.print_available_food()
                        food_index = int(input("Введите номер еды, которую хотите купить (или -1 для выхода): "))
                        
                        if food_index == -1:
                            break
                        
                        if 0 <= food_index < len(self.farm.food):
                            amount = int(input("Введите количество: "))
                            self.buy_food(food_index, amount)
                        else:
                            print("\nНекорректный номер еды. Попробуйте снова.")
                
                case '5': # рабочие
                    print('\nВы хотите:'
                          '\n(1) - Нанять (200$)'
                          '\n(2) - Уволить')
                    work_choice = input()
                    
                    match work_choice:
                        case '1':
                            print('\nВведите количество рабочих')
                            count = input()
                            valid_count = digit_check(count)
                            if self.money >= valid_count * 200:
                                self.money -= valid_count * 200
                                self.statistics.add_statistics(valid_count * 200, 'расход') # Учет трат в статистику
                                self.farm.increase_workers(valid_count)
                                print(f'\nПоздравляем, вы наняли {valid_count} рабочих')
                            else:
                                print(f'\nУ вас не хватает {valid_count * 200 - self.money}$ на это')
                        
                        case '2':
                            print('\nВведите количество рабочих подлежащих увольнению')
                            num_workers = input()
                            valid_num_workers = digit_check(num_workers)
                            self.farm.workers -= valid_num_workers
                            print(f'\nВы успешно уволили {valid_num_workers} рабочих')
                        
                case '6': # фермеры
                    print('\nВы хотите:'
                          '\n(1) - Нанять (200$)'
                          '\n(2) - Уволить')
                    work_choice = input()
                    
                    match work_choice:
                        case '1':
                            print('\nВведите количество фермеров')
                            count = input()
                            valid_count = digit_check(count)
                            if self.money >= valid_count * 200:
                                self.money -= valid_count * 200
                                self.statistics.add_statistics(valid_count * 200, 'расход') # Учет трат в статистику
                                self.farm.increase_farmers(valid_count)
                                print(f'\nПоздравляем, вы наняли {valid_count} фермеров')
                            else:
                                print(f'\nУ вас не хватает {valid_count * 200 - self.money}$ на это')
                            
                        case '2':
                            print('\nВведите количество фермеров подлежащих увольнению')
                            num_workers = input()
                            valid_num_workers = digit_check(num_workers)
                            self.farm.farmers -= valid_num_workers
                            print(f'\nВы успешно уволили {valid_num_workers} фермеров')
                            
                case '7': # подписка на еду
                    if self.farm.food_sub == False:
                        print('\nВы действительно хотите оформить подписку на корм?'
                            '\nДоставка корма будет стоить вам 5000$ за ход'
                            '\n(1) - Да    (2) - Нет')
                        shop_confirm = input()
                        if shop_confirm == '1' and self.money >= 5000:
                            self.farm.food_sub = True
                            print('\nВы успешно подписались!')
                    elif self.farm.food_sub == True:
                        print('\nВы действительно хотите отказаться от подписки?'
                            '\n(1) - Да    (2) - Нет')
                        shop_confirm = input()
                        if shop_confirm == '1':
                            self.farm.food_sub = False
                            print('\nВы успешно отменили подписку!')
                
                case '8': # инфо о ферме
                    self.farm.farm_info()
                
                case '0':# Выход из цикла
                    break
                
                case _:
                    print('\nТакого варианта нет.')

    def zoo_upgrades(self): # магазин зоопарка
        while True:
            total_money = format_money(self.money)
            print(f'\nУ вас {total_money} денег.'
                '\nЧто вы хотите купить?'
                '\n(1) - Животные'
                '\n(2) - Работники'
                '\n(3) - Аттракционы'
                '\n(4) - Магазины'
                '\n(5) - Инфо'
                '\n(6) - Выйти')
            shop_choice = input()
            
            match shop_choice:
                case '1':
                    while True:
                        total_money = format_money(self.money)
                        print(f'\n{total_money}$')
                        self.print_available_animals_zoo()
                        animal_index = input("Введите номер животного, которое хотите купить (или -1 для выхода): ")
                        
                        if animal_index == '-1':
                            break
                        
                        valid_index = digit_check(animal_index)
                        
                        
                        if 0 <= valid_index < len(self.zoo.animals):
                            amount = input("Введите количество: ")
                            valid_amount = digit_check(amount)
                            self.buy_animals_zoo(valid_index, valid_amount)
                        else:
                            print("\nНекорректный номер животного. Попробуйте снова.")

                case '2':
                    print('\nВы хотите:'
                          '\n(1) - Нанять (200$)'
                          '\n(2) - Уволить')
                    work_choice = input()
                    
                    match work_choice:
                        case '1':
                            print('\nВведите количество работников')
                            count = input()
                            valid_count = digit_check(count)
                            if self.money >= valid_count * 200:
                                self.money -= valid_count * 200
                                self.statistics.add_statistics(valid_count * 200, 'расход')
                                self.zoo.increase_workers(valid_count)
                                print(f'\nПоздравляем, вы наняли {valid_count} работников')
                            else:
                                print(f'\nУ вас не хватает {valid_count * 200 - self.money}$ на это')

                        case '2':
                            print('\nВведите количество работников подлежащих увольнению')
                            num_workers = input()
                            valid_num_workers = digit_check(num_workers)
                            if self.zoo.total_animals * 50 < valid_num_workers - self.zoo.workers:
                                print('\nНельзя уволить столько рабочих, иначе животные останутся без присмотра')
                            else:
                                self.zoo.workers -= valid_num_workers
                                print(f'\nВы успешно уволили {valid_num_workers} работников')
                                
                        case _:
                            print('\nНекорректный ввод. Попробуйте снова.')

                case '3':
                    while True:
                        total_money = format_money(self.money)
                        print(f'\n{total_money}$')
                        self.print_available_attraction()
                        attraction_index = input("Введите номер аттракциона, который хотите купить (или -1 для выхода): ")
                        if attraction_index == '-1':
                            break
                        
                        valid_index = digit_check(attraction_index)
                        
                        if 0 <= valid_index < len(self.zoo.attraction):
                            amount = input("Введите количество: ")
                            valid_amount = digit_check(amount)
                            self.buy_attraction(valid_index, valid_amount)
                        else:
                            print("\nНекорректный номер аттракциона. Попробуйте снова.")        
                    
                case '4':
                    while True:
                        total_money = format_money(self.money)
                        print(f'\n{total_money}$')
                        self.zoo.print_available_shops()
                        shop_index = input("Введите номер магазина, который хотите построить (или -1 для выхода): ")
                        
                        if shop_index == '-1':
                            break
                        
                        valid_index = digit_check(shop_index)
                                
                        if 0 <= valid_index < len(self.zoo.shops):
                            amount = input("Введите количество: ")
                            valid_amount = digit_check(amount)
                            self.zoo.buy_shop(valid_index, valid_amount)
                        else:
                            print("\nНекорректный номер магазина. Попробуйте снова.")
                
                case '5':
                    self.zoo.zoo_info()
                                
                case '6':
                    break 
                   
    def player_update(self): # Обновление состояния игрока и его бизнесов
        global game_over # Переменная для проигрыша
        money_made = 0 # дневной заработок
        
        self.birja.birja_update()
        
        self.statistics.count_turns()
        
        animal_count = 0
        for animal in self.farm.animals: # подсчет количества животных на ферме
            animal_count += animal['count']
          
        if self.farm.food_sub == True and self.money >= animal_count:# автопокупка еды, если есть подписка 
            self.money -= animal_count + 5000 # -стоимость еды и подписки
            spent = animal_count # переменная трат для записи в статистику
            self.statistics.add_statistics(spent, 'расход') # Учет трат в статистику
            
            for i in range(len(self.farm.animals)): # покупка еды для животных на ферме
                self.farm.food[i]['count'] += self.farm.animals[i]['count']  
            
            money_made -= (animal_count + 5000) # учетка для вывода дневного заработка
                
        self.farm.farm_update() # Апдейт еды и заработка фермы
        if self.zoo is not None: # Проверка на наличие зоопарка
            self.zoo.zoo_update() # Апдейт зоопарка
        
        if self.pet is not None and self.farm.income >= 0:# Доход если есть баф питомца
            self.money += round(self.farm.income + (self.farm.income * (self.pet.level * 0.005)))
            money_made += round(self.farm.income + (self.farm.income * (self.pet.level * 0.005)))
            if self.zoo is not None and self.zoo.income >= 0: # Проверка на наличие зоопарка
                self.money += round(self.zoo.income + (self.zoo.income * (self.pet.level * 0.005)))
                money_made += round(self.zoo.income + (self.zoo.income * (self.pet.level * 0.005)))   
        else: # Доход без бафа
            if self.zoo is not None: # Проверка на наличие зоопарка
                self.money += self.zoo.income
                money_made += self.zoo.income
            self.money += self.farm.income
            money_made += self.farm.income  
        
        self.money += round(self.birja.income) # заработок с дивидентов
        money_made += round(self.birja.income)
        
        self.pay_loan() # выплата кредита
        income = format_money(money_made - pay_per_turn)
        self.statistics.add_statistics(money_made - pay_per_turn, 'доход')
        self.money = round(self.money) # округление денег
        total_money = format_money(self.money)
        print(f'\nСчет: {total_money}$'
              f'\nВы заработали: {income}$')
        
        if self.money < 0: # Банкротство
            self.bankrupt_turns -= 1
            print(f'\nНа вашем счету слишком мало денег,'
                  f'\nесли вы не выйдете из минуса за {self.bankrupt_turns} ходов вы проиграете')
            if self.bankrupt_turns == 0:
                print('\nВы обанкротились!')
                game_over = True # Переменная для проигрыша
        
        else:
            self.bankrupt_turns = 11
            game_over = False
                       
    def get_loan(self): # функция взятия кредита
        while True:
            print('\nКакую сумму вы хотите взять в кредит?')
            loan_amount = input()
            valid_loan_amount = digit_check(loan_amount)
            if valid_loan_amount <= 0:
                print('\nНеправильные данные по размеру кредита!')
                break
            
            print('\nЗа сколько ходов вы планируете выплатить кредит?')
            loan_duration = input()
            valid_loan_duration = digit_check(loan_duration)
            if valid_loan_duration <= 0:
                print('\nНеправильные данные по длительности кредита!')
                break
            
            total_loan = valid_loan_amount * (1 + 0.15 * (valid_loan_duration // 10)) # 15% каждые 10 ходов
            print(f'\nЗа {valid_loan_duration} ходов вам надо будет выплатить {round(total_loan)}$ вы уверены что хотите взять этот кредит?'
                '\n(1) - да    (2) - нет')
            loan_confirm = input()
            if loan_confirm == '1':
                self.money += valid_loan_amount
                self.loans.append({
                    'amount': valid_loan_amount,
                    'duration': valid_loan_duration,
                    'total_amount': total_loan,
                })

                print(f'Вы взяли кредит на сумму {valid_loan_amount}$ сроком на {loan_duration} ходов.')
                break
            else:
                break
    
    def pay_loan(self): # выплата кредита
        global pay_per_turn
        pay_per_turn = 0
        if not self.loans:
            return
        
        for loan in self.loans:
            pay_per_turn = loan['total_amount'] / loan['duration'] # расчет выплаты за ход
            self.money -= round(pay_per_turn) # -деньги в уплату кредита
            self.statistics.add_statistics(round(pay_per_turn), 'расход')
            loan['total_amount'] -= pay_per_turn # обновляем остаток по кредиту
            loan['duration'] -= 1
            
            if loan['duration'] == 0:
                print(f"\nВы успешно погасили кредит на сумму {loan['amount']}$")
                self.loans.remove(loan)
            else:
                payed = format_money(pay_per_turn)
                print(f"\nВы выплатили {payed}$ по кредиту. Осталось {loan['duration']} ходов до погашения.")
    
    def slot_machine(self, bid): # слот машина
        # Символы на барабане
        symbols = ["7", "BAR", "Вишня", "Лимон", "Апельсин"]

        # Таблица выплат
        payout_table = {
            ("7", "7", "7"): bid * 50,
            ("BAR", "BAR", "BAR"): bid * 25,
            ("Вишня", "Вишня", "Вишня"): bid * 10,
            ("Лимон", "Лимон", "Лимон"): bid * 5,
            ("Апельсин", "Апельсин", "Апельсин"): bid * 3,
            ("7", "BAR", "Вишня"): bid,
            ("BAR", "BAR", "Апельсин"): round(bid / 2),
            ("7", "7", "Лимон"): round(bid / 3),
        }

        # Функция для запуска барабана
        def pull_lever():
            return [random.choice(symbols) for _ in range(3)]

        # Функция для проверки выигрыша
        def check_win(combination):
            return combination in payout_table

        # Основная игровая логика
        def play_slot_machine():
            print("Добро пожаловать в игровой автомат!")

            while self.money > 0:
                print(f"\nУ вас на счету:{format_money(self.money)}$")
                x = input("Нажмите Enter, чтобы запустить барабан (или -1 чтобы выйти)...")
                if x == '-1':
                    break
                else:
                    symbols_on_reels = pull_lever()
                    print("Результат:", " | ".join(symbols_on_reels))

                    combination = tuple(symbols_on_reels)
                    if check_win(combination):
                        win_amount = payout_table[combination]
                        print(f"Поздравляем! Вы выиграли {win_amount}!")
                        self.money += win_amount
                        self.statistics.add_statistics(win_amount, 'доход', 'казино доход')
                    else:
                        print("Увы, вы не выиграли.")
                        self.money -= bid  # стоимость одной игры
                        self.statistics.add_statistics(bid, 'расход', 'казино расход')

            print("Игра окончена.")
            
        play_slot_machine()
    
    def black_jack(self): # блэкджек
        # Создаем колоду карт
        suits = ['Черви', 'Бубны', 'Пики', 'Крести']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Валет', 'Дама', 'Король', 'Туз']

        # Определение значения карт
        card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Валет': 10, 'Дама': 10, 'Король': 10, 'Туз': 11}

        # Функция для создания колоды
        def create_deck():
            deck = []
            for suit in suits:
                for rank in ranks:
                    deck.append(rank + ' ' + suit)
            return deck

        # Функция для подсчета суммы карт в руке
        def calculate_hand_value(hand):
            value = 0
            num_aces = 0
            for card in hand:
                rank = card.split()[0]
                value += card_values[rank]
                if rank == 'Туз':
                    num_aces += 1
            while value > 21 and num_aces > 0:
                value -= 10
                num_aces -= 1
            return value

        # Функция для начала игры
        def start_game():
            while True:
                deck = create_deck()
                random.shuffle(deck)

                player_hand = []
                dealer_hand = []

                # Раздача начальных карт
                player_hand.append(deck.pop())
                dealer_hand.append(deck.pop())
                player_hand.append(deck.pop())
                dealer_hand.append(deck.pop())

                # Игрок делает ставку
                print(f'\nУ вас {format_money(self.money)}$')
                bet = input("Сделайте вашу ставку (-1 для выхода): ")
                if bet == '-1':
                    break
                else:
                    valid_bet = digit_check(bet)

                    # Игра продолжается, пока у игрока или дилера сумма очков не превышает 21
                    while True:
                        print("\nВаши карты:", player_hand)
                        print("Сумма ваших очков:", calculate_hand_value(player_hand))
                        print("\nКарта дилера:", dealer_hand[0])

                        action = input("\nВыберите действие ( 1 - Взять / 2 - Уйти): ")

                        if action == '1':
                            player_hand.append(deck.pop())
                            if calculate_hand_value(player_hand) > 21:
                                print("Вы проиграли! Сумма ваших очков превысила 21.")
                                self.money -= valid_bet
                                self.statistics.add_statistics(valid_bet, 'расход', 'казино расход')
                                break
                        elif action == '2':
                            while calculate_hand_value(dealer_hand) < 17:
                                dealer_hand.append(deck.pop())
                            print("\nКарты дилера:", dealer_hand)
                            print("Сумма очков дилера:", calculate_hand_value(dealer_hand))
                            if calculate_hand_value(dealer_hand) > 21 or calculate_hand_value(dealer_hand) < calculate_hand_value(player_hand):
                                print("Поздравляем, вы выиграли!")
                                self.money += valid_bet
                                self.statistics.add_statistics(valid_bet, 'доход', 'казино доход')
                            elif calculate_hand_value(dealer_hand) == calculate_hand_value(player_hand):
                                print("Ничья!")
                            else:
                                print("Вы проиграли. Дилер победил.")
                                self.money -= valid_bet
                                self.statistics.add_statistics(valid_bet, 'расход', 'казино расход')
                            break
                        else:
                            print("Некорректный ввод. Попробуйте снова.")

        start_game()

    def casino(self): # казино
        print('\nДобро пожаловать в казино, во что хотите сыграть?'
              '\n(1) - рулетка    (2) - ракета    (3) - слоты    (4) - блэкджек')
        casino_choice = input()
        
        match casino_choice:
            case '1': # Играть в рулетку
                while True:
                    print(f'\nУ вас {self.money}$')
                    print('(1) - Играть'
                        '\n(2) - Правила'
                        '\n(3) - Выйти')
                    game_choice = input()
                    
                    match game_choice:    
                        case '1':
                            print('\nСделайте ставку:')
                            bid = input()
                            valid_bid = digit_check(bid)
                            if self.money >= valid_bid:
                                self.statistics.add_statistics(valid_bid, 'казино расход', 'расход') # запись расходов на казино
                                self.money -= valid_bid
                                dice = random.randint(0, 36)
                                print('\nНа что ставите?'
                                    '\n(1) - Точное число    (2) - Четное/нечетное')
                                dice_choice = input() # Выбор на что ставить
                                
                                if dice_choice == '1':
                                    print('\nВведите ваше число')
                                    num_choice = input()
                                    valid_num = digit_check(num_choice)   # Проверка на отсутствие букв
                                    if dice == valid_num:
                                        self.money += round(valid_bid * 36) # Зачисление выйгрыша
                                        self.statistics.add_statistics(round(valid_bid * 36), 'казино доход', 'доход') # запись доходов с казино
                                        print(f'\nВыпало число {dice}. Вы выйграли {valid_bid * 36}$')
                                    else:
                                        print(f'\nК сожалению вы проиграли, выпало {dice}')
                                        
                                elif dice_choice == '2':
                                    print('\n(1) - Четное    (2) - Нечетное')
                                    dice_oddnes = input()
                                    
                                    if dice_oddnes == '1':
                                        if is_prime(dice):
                                            print(f'\nВыпало {dice}. Вы проиграли')
                                        else:
                                            print(f'\nВыпало {dice}. Вы выйграли {round(valid_bid * 2)}!')
                                            self.money += round(valid_bid * 2)
                                            self.statistics.add_statistics(round(valid_bid * 2), 'казино доход', 'доход')
                                            
                                    elif dice_oddnes == '2':
                                        if is_prime(dice):
                                            print(f'\nВыпало {dice}. Вы выйграли {round(valid_bid * 2)}!')
                                            self.money += round(valid_bid * 2)
                                            self.statistics.add_statistics(round(valid_bid * 2), 'казино доход', 'доход')  
                                        else:
                                            print(f'\nВыпало {dice}. Вы проиграли')

                            else:
                                print('У вас недостаточно денег на счету!')

                        case '2':
                            roulette()
                        
                        case '3':
                            break
            
            case '2': # Играть в ракету
                while True:
                    print(f'\nУ вас {self.money}$'
                        '\n(1) - Играть'
                        '\n(2) - Правила'
                        '\n(3) - Выйти')
                    game_choice = input()
                    
                    match game_choice:
                        case '1':
                            print('\nСделайте ставку:')
                            bid = input()
                            valid_bid = digit_check(bid)
                            if self.money >= valid_bid:
                                self.statistics.add_statistics(valid_bid, 'казино расход', 'расход') # запись расходов на казино
                                self.money -= valid_bid
                                multi = 1.0 # число на которое умножается выйгрыш
                                bonus = 0.125 # число которое добавляется к множителю при удачном стечении обстоятельств
                                
                                while True:
                                    print(f'\nСейчас выйгрыш {round(valid_bid * multi)}$'
                                        '\n      Вывести?       '
                                        '\n(1) - Да    (2) - Нет')
                                    rocket_choice = input()
                                    
                                    match rocket_choice:
                                        case '1':
                                            self.money += round(valid_bid * multi)
                                            self.statistics.add_statistics(round(valid_bid * multi), 'казино доход', 'доход')
                                            print(f'\nВы забрали выйгрыш в размере{round(valid_bid * multi)}$')
                                            break
                                        
                                        case '2':
                                            x = random.randint(1, 100)
                                            if x > 33:
                                                multi += bonus
                                            else:
                                                print('Ракета разбилась!')
                                                break
                                
                            else:
                                print('У вас недостаточно денег на счету!')      
                        
                        case '2':
                            rocket()
                                                    
                        case '3':
                            break    
            
            case '3': # Слоты
                my_bid = input('Введите вашу ставку:')
                my_bid_validate = digit_check(my_bid)
                self.slot_machine(my_bid_validate)
            
            case '4': # Блэкджек
                self.black_jack()
                
                  
class Farm:
    def __init__(self, name) -> None:
        self.name = name
        self.area = 0
        self.farmers = 0
        self.workers = 0
        
        self.trees = []
        self.trees_to_buy = [
            {'Type': 'Вишня', 'Cost': 200},
            {'Type': 'Слива', 'Cost': 400},
            {'Type': 'Яблоко', 'Cost': 500},
            {'Type': 'Груша', 'Cost': 500},
            {'Type': 'Персик', 'Cost': 1000}
        ]
        self.fruits = []
        self.auto_sell_pos = False

        self.animals = [
        {'name': 'Курица', 'count': 0, 'price': 1_500, 'income' : 50},
        {'name': 'Гусь', 'count': 0, 'price': 2_000, 'income' : 100},
        {'name': 'Овца', 'count': 0, 'price': 2_500, 'income' : 150},
        {'name': 'Корова', 'count': 0, 'price': 3_500, 'income' : 250},
        {'name': 'Свинья', 'count': 0, 'price': 4_000, 'income' : 300}                    
        ]
        
        self.food = [
        {'type': 'Куриная', 'count': 10, 'price': 1},
        {'type': 'Гусиная', 'count': 10, 'price': 1},
        {'type': 'Овечья', 'count': 10, 'price': 1},
        {'type': 'Коровья', 'count': 10, 'price': 1},
        {'type': 'Свиная', 'count': 10, 'price': 1}
        ]
        
        self.income = 0 
        self.food_sub = False
        self.cost = 0
        
    def farm_update(self): # Апдейт показателей фермы
        
        animal_income = 0
        for animal in self.animals: 
            animal_income += animal['income'] * animal['count'] # расчет дохода со всех животных на ферме
        
        animal_cost = 0
        for animal in self.animals:
            animal_cost += animal['price'] * animal['count'] # расчет стоимости всех животных на ферме
        
        food_cost = 0
        for food in self.food:
            food_cost += food['price'] * food['count']
        
        self.fruit_creation() # урожай плодов с деревьев
        
        self.income = animal_income - (self.workers * 5_000) - (self.farmers * 4_000) - (self.area * 1_000) # заработок фермы за ход
        self.cost = self.area * 10_000 + self.workers * 5_000 + self.farmers * 4000 + animal_cost + food_cost
        
        if self.auto_sell_pos == True:
            income = sum(fruit.price for fruit in self.fruits) # прибыль с проданых фруктов
            self.income += income
            self.fruits = [] # удаление проданых фруктов
            if income == 0:
                print('\nУ вас нет фруктов для автоматической продажи')
            else:
                print(f'\nАвтоматически продано фруктов на {income}$')
        
        spent = (self.workers * 5_000) + (self.farmers * 4_000) + (self.area * 1_000) # переменная трат для записи в статистику
        player.statistics.add_statistics(spent, 'расход') # Учет трат в статистику
        
        if len(self.trees) > self.farmers * 140: # Один работник фермы может следить только за 140 деревьями
            vegies_lost = 0
            for i in range(len(self.trees) - self.farmers * 140):
                self.trees.pop()
                vegies_lost += 1
            print(f'{vegies_lost} деревьев умерло из-за недостатка ухода')
            
        if len(self.trees) > self.area * 1000: # На одном поле не может расти больше 1000 растений
            vegies_lost = 0
            for i in range(len(self.trees) - self.area * 1000):
                self.trees.pop()
                vegies_lost += 1
            print(f'\n{vegies_lost} овощей потеряно из-за нехватки полей')

        # проверка на то чтобы животным хватало рабочих
        animal_lost = 0 # счетчик умерших животных от ухода          
        total_animals = 0 # всего животных
        breeds = 0 # видов животных
        for i in range(len(self.animals)):
            if self.animals[i]['count'] > 0:
                total_animals += self.animals[i]['count']
                breeds += 1
        if total_animals > self.workers * 30: # проверка если перебор животных
            animal_lost = total_animals - self.workers * 30 # подсчет умерших животных
            for i in range(len(self.animals)):
                if total_animals <= self.workers * 30: # проверка достаточно ли теперь животных или еще нет
                    break
                if self.animals[i]['count'] > 0:
                    self.animals[i]['count'] = max(self.animals[i]['count'] - math.ceil(animal_lost / breeds), 0) # новое количество животного
                    total_animals -= math.ceil(animal_lost / breeds)          
        if animal_lost > 0:
            print(f'\n{animal_lost} животных умерло из-за недостатка ухода')
                
        animal_lost = 0 # счетчик умерших животных от голода
        for i in range(len(self.animals)):             
            if self.animals[i]['count'] > self.food[i]['count']: # Одной едой можно накормить 1 животное
                animal_lost += self.animals[i]['count'] - self.food[i]['count']
                self.animals[i]['count'] = max(self.food[i]['count'], 0)
        if animal_lost > 0:
            print(f'\n{animal_lost} животных умерло из-за недостатка еды')
        
        for i in range(len(self.animals)):    
            self.food[i]['count'] -= self.animals[i]['count'] # животные кушают
        
    def farm_info(self):
        print(f'\nНазвание фермы - {self.name}'
              f'\nОбщая стоимость фермы - {self.cost}'
              f'\nКоличество полей - {self.area}'
              f'\nКоличество рабочих - {self.workers}'
              f'\nКоличество фермеров - {self.farmers}'
              f'\nКоличество растущих деревьев - {len(self.trees)}')
        for animal in self.animals:
            print(f'{animal["name"]}: {animal['count']}')
        for food in self.food:
            print(f'{food['type']}: {food['count']}')
        print(f'Доход за 1 ход - {format_money(self.income)}$')
        pause()       
    
    def increase_area(self, n): #увеличение кол-ва полей
        self.area += n
        
    def increase_workers(self, n): #увеличение кол-ва рабочих
        self.workers += n 

    def increase_farmers(self, n): # +фермер
        self.farmers += n
    
    def fruit_creation(self): # урожай деревьев
        prices ={'Вишня': 12.5,
                 'Яблоко': 12.5,
                 'Груша': 12.5,
                 'Персик': 12.5,
                 'Слива': 12.5}
        
        for tree in self.trees:
            price = prices[tree.type]
            fruits = [Fruit(tree.type, price) for _ in range(3)]
            self.fruits.extend(fruits)
    
    def show_my_trees(self): # показывает сколько каких деревье у меня есть
        tree_num = len(self.trees)# Кол-во деревьев
        print(f'\nУ вас {tree_num} деревьев')
        
        num_of_trees = {} # словарь для отображения количества деревьев
        
        for tree in self.trees: # подсчет деревьев
            if tree.type in num_of_trees.keys():
                num_of_trees[tree.type] += 1
            else:
                num_of_trees[tree.type] = 1
        
        for tree, num in num_of_trees.items(): # вывод информации о деревьях
            if num > 0:
                print(f'{tree}: {num} штук ({(num / tree_num) * 100: .2f}% )')
    
    def show_fruits(self):
        fruit_num = len(self.fruits)# Кол-во деревьев
        print(f'\nУ вас {fruit_num} фруктов в инвентаре')
        
        num_of_fruits = {}
        
        for fruit in self.fruits:
            if fruit.type in num_of_fruits:
                num_of_fruits[fruit.type] += 1
            else:
                num_of_fruits[fruit.type] = 1
                
        for fruit, num in num_of_fruits.items(): # вывод информации о деревьях
            if num > 0:
                print(f'{fruit}: {num} штук ({(num / fruit_num) * 100:.2f}% )')
    
    
class Zoo:
    def __init__(self, name) -> None:
        self.name = name
        self.workers = 0
        self.animals = [
            {'name': 'Свин', 'count': 0, 'price': 3_000, 'popularity': 30, 'type' : 'herbivore'},
            {'name': 'Капибара', 'count': 0, 'price': 10_000, 'popularity': 60, 'type' : 'herbivore'},
            {'name': 'Рысь', 'count': 0, 'price': 30_000, 'popularity': 110, 'type' : 'carnivore'},
            {'name': 'Трубкозуб', 'count': 0, 'price': 50_000, 'popularity': 125, 'type' : 'herbivore'},
            {'name': 'Тапир', 'count': 0, 'price': 70_000, 'popularity': 140, 'type' : 'herbivore'},
            {'name': 'Бегемот', 'count': 0, 'price': 100_000, 'popularity': 160, 'type' : 'carnivore'},
            {'name': 'Жираф', 'count': 0, 'price': 150_000, 'popularity': 190, 'type' : 'herbivore'},
            {'name': 'Слон', 'count': 0, 'price': 250_000, 'popularity': 260, 'type' : 'herbivore'},
            {'name': 'Панда', 'count': 0, 'price': 1_000_000, 'popularity': 1_100, 'type' : 'herbivore'}
        ]
        
        self.attraction = [
            {'name': 'Тир', 'count': 0, 'price': 10_000, 'popularity': 100, 'ticket': 5},
            {'name': 'Тарзанка', 'count': 0, 'price': 30_000, 'popularity': 150, 'ticket': 5},
            {'name': 'Батуты', 'count': 0, 'price': 50_000, 'popularity': 175, 'ticket': 5},
            {'name': 'Игровая площадка', 'count': 0, 'price': 100_000, 'popularity': 200, 'ticket': 5},
            {'name': 'Колесо обозрения', 'count': 0, 'price': 200_000, 'popularity': 300, 'ticket': 5},
            {'name': 'Летающая тарелка', 'count': 0, 'price': 300_000, 'popularity': 400, 'ticket': 5},
            {'name': 'Тоннель любви', 'count': 0, 'price': 500_000, 'popularity': 500, 'ticket': 5},
            {'name': 'Кинозал', 'count': 0, 'price': 800_000, 'popularity': 700, 'ticket': 5},
            {'name': 'Американские горки', 'count': 0, 'price': 1_000_000, 'popularity': 900, 'ticket': 5},
            {'name': 'Дельфинарий', 'count': 0, 'price': 10_000_000, 'popularity': 5000, 'ticket': 5}
            
        ]
        
        self.shops = [ # Доделать!!!
            {'name': 'Сахарная вата', 'count': 0, 'price': 100_000, 'popularity': 1000},
            {'name': 'Сувениры', 'count': 0, 'price': 500_000, 'popularity': 500},
            {'name': 'Фигурки животных', 'count': 0, 'price': 700_000, 'popularity': 700},
            {'name': 'Игрушки', 'count': 0, 'price': 1_000_000, 'popularity': 1000},
            {'name': 'Кафе', 'count': 0, 'price': 10_000_000, 'popularity': 10000},
            {'name': 'Ресторан', 'count': 0, 'price': 15_000_000, 'popularity': 15000},
            {'name': 'Торговый центр', 'count': 0, 'price': 100_000_000, 'popularity': 100000},
            {'name': 'ТРЦ', 'count': 0, 'price': 150_000_000, 'popularity': 150000}
        ]
        
        self.visitors = 0
        self.income = 0
        self.cost = 300_000
        self.total_animals = 0
        self.rating = 0

    def zoo_update(self):
        total_popularity = 0
        self.total_animals = 0
        self.cost = 300_000
        animal_types = 0 # кол-во видов животных
        attraction_types = 0 # кол-во видов аттракционов
        shop_types = 0
        self.rating = 0
        
        for animal in self.animals: # расчет рейтинга парка от животных
            if animal['count'] > 0:
                animal_types += 1
        self.rating_count(animal_types)
                        
        for attraction in self.attraction: # расчет рейтинга парка от аттракционов
            if attraction['count'] > 0:
                attraction_types += 1
        self.rating_count(attraction_types)
                    
        for shop in self.shops:
            if shop['count'] > 0:
                shop_types += 1
        self.rating_count(attraction_types)
        
        for animal in self.animals:# расчет цены зоопарка
            self.cost += animal['price'] * animal['count']
        for attraction in self.attraction:
            self.cost += attraction['price'] * attraction['count']
        
        for animal in self.animals:# расчет популярности зоопарка
            total_popularity += animal['popularity'] * animal['count']
        for attraction in self.attraction:
            total_popularity += attraction['popularity'] * attraction['count']
        for shop in self.shops:
            total_popularity += shop['popularity'] * shop['count']
        
        for animal in self.animals: # расчет количества животных в зоопарке
            self.total_animals += animal['count']
        
        self.visitors = total_popularity
        
        self.income = (self.visitors * 5) - (self.workers * 5_000) # вход стоит 5$
        self.income = round(self.income * ((self.rating + 100) / 100))
        player.statistics.add_statistics(self.workers * 5_000, 'расход')
   
    def zoo_info(self):
        print('')
        for animal in self.animals:
            if animal['count'] >= 1:
                print(f'{animal["name"]} (Количество: {animal["count"]}) (Популярность: {animal["popularity"]})')
        print('')
        for attraction in self.attraction:
            if attraction['count'] >= 1:
                print(f'{attraction["name"]} (Количество: {attraction["count"]}) (Популярность: {attraction["popularity"]})')
        print(f'\nРаботников: {self.workers}')
        print(f'\nПосетителей: {self.visitors} ')
        print(f'Рейтинг: {self.rating}')
        print(f'\nДоход: {format_money(self.income)}$')
    
    def rating_count(self, diversity):
        if 4 <= diversity <= 6:
            self.rating += 1
        elif 7 <= diversity <= 9:
            self.rating += 2
        elif diversity >= 10:
            self.rating += 3
       
    def increase_workers(self, n):
        self.workers += n    
    
    def print_available_shops(self):
        for i, shop in enumerate(self.shops):
            price = format_money(shop['price'])
            print(f'{i}: {shop['name']} (Цена: {price}$) (Популярность: {shop['popularity']})')
    
    def buy_shop(self, shop_index, amount):
        shop = self.shops[shop_index]
        total_cost = shop['price'] * amount
        if player.money >= total_cost:
            player.money -= total_cost
            player.statistics.add_statistics(total_cost, 'расход') # учет статистики расходов
            shop['count'] += amount
            print(f'\nПотрачено {total_cost}$')
            print(f'Куплено {amount} {shop["name"]}')
        else:
            print("Недостаточно средств для покупки.")
    
       
class Statistics:
    def __init__(self) -> None:
        self.money_made = 0
        self.money_spent = 0
        self.vegies_bought = 0
        self.cows_bought = 0
        self.cost_of_all = 0
        self.achieves = []
        self.casino_win = 0
        self.casino_lost = 0
        self.turns = 0
        
    def competition_check(self):
        achiv_state = player.pet.competitions
        
        match achiv_state:
            case 2:
                self.achieves.append('COMPETITION WINNER I')
            case 3:
                self.achieves.append('COMPETITION WINNER II')
            case 4:
                self.achieves.append('COMPETITION WINNER III')
            case 5:
                self.achieves.append('COMPETITION WINNER IV')
            case 6:
                self.achieves.append('COMPETITION WINNER V')
            case 7:
                self.achieves.append('COMPETITION WINNER VI')
            case 8:
                self.achieves.append('COMPETITION WINNER VII')
            case 9:
                self.achieves.append('COMPETITION WINNER VIII')
            case 10:
                self.achieves.append('COMPETITION WINNER IX')
            case 11:
                self.achieves.append('COMPETITION WINNER X')
            
    def show_achiev_competition(self):
        print('\nВаши достижения:')
        for achievement in self.achieves:
            print(achievement)
        pause()
    
    def add_statistics(self, money, *args):
        
        if 'расход' in args:
            self.money_spent += money
            
        if 'доход' in args and money >= 0:
            self.money_made += money
        
        if 'казино доход' in args:
            self.casino_win += money
            
        if 'казино расход' in args:
            self.casino_lost += money
        
    def plus_vegies(self, amount):
        self.vegies_bought += amount
        
    def everything_cost(self, cost):
        self.cost_of_all = cost
        
    def count_turns(self):
        self.turns += 1
    
    def show_stats(self):
        print(f'\nДенег потрачено: {self.money_spent}$'
              f'\nДенег заработано: {self.money_made}$'
              f'\nДенег потрачено в казино: {self.casino_lost}$'
              f'\nДенег зараотано в казино: {self.casino_win}$'
              f'\nХодов сделано: {self.turns}')
        pause()
    
    def show_companies(self):
        pass
    
    
class Pet:
    def __init__(self, type, name) -> None:
        self.name = name
        self.type = type
        self.exp = 0
        self.level = 1
        self.exp_per_level = 1
        self.competitions = 1
    
    def update_exp_per_level(self):
        self.exp_per_level = self.level * (self.level - 1) * 500
                     
    def competition(self):
        competitor_level = self.competitions ** 2
        print(f'\nВаш первый питомец-соперник имеет Уровень: {competitor_level}' 
              f'\nВаш питомец: Уровень: {self.level}, Имя: {self.name}, Тип: {self.type}')
        if self.level > competitor_level:
            print('\nВаш питомец одержал победу!'
                    '\nЗа победу вам дадут награду в список ваших достижений')
            self.competitions += 1
            player.statistics.competition_check()
            pause()
        elif self.level == competitor_level:
            chance = random.randint(0,1)
            match chance:
                case 1:
                    print('\nВаш питомец одержал победу!'
                    '\nЗа победу вам дадут награду в список ваших достижений')
                    self.competitions += 1
                    player.statistics.competition_check()
                    pause()       
                case _:
                    print('\nК сожалению вам не удалось выйграть, приходите еще!')
                    pause()    
        else:
            print('\nК сожалению вам не удалось выйграть, приходите еще!')
            pause()
            
    
class Pet_fighter(Pet):
    def __init__(self, type, name, health = 100, armor = 5, damage = 15, miss = 1, accuracy = 10, crit_chance = 1, bleed_chance = 1, bleed_damage = 5) -> None:
        super().__init__(type, name)
        self.health = health # хп
        self.armor = armor # броня
        self.damage = damage # урон
        self.miss = miss # рейтинг уворота
        self.accuracy = accuracy # рейтинг точности
        self.crit_chance = crit_chance # крит шанс в процентах максимум 80%
        self.bleed_chance = bleed_chance # шанс блида в процентах
        self.bleed_damage = bleed_damage # урон от блида за ход
        self.bleeding = 0 # количество ходов которые будет истекать кровью
        self.skill_points = 5 # очки таланта
        self.wins = 0 # количество убийств
        self.loses = 0 # количество поражений
        self.inventory = [] # инвентарь
        self.head = None # только тип головной убор
        self.body = None # только тип броня
        self.pants = None # только тип штаны
        self.boots = None # только тип ботинки
        self.weapon = None # только тип оружие
    
    def inventory_choice(self):
        while True:
            print('\nВыберите предмет:')
            self.show_inventory()
            item_choice = input()
            if item_choice == '-1':
                break
            valid_choice = digit_check(item_choice)
            if 0 <= valid_choice < len(self.inventory): 
                chosen_item = self.inventory[valid_choice]

                match chosen_item.type:
                    case 'Weapon':
                        if self.weapon is not None: # если у персонажа уже есть оружие оно падает в инвентарь
                            self.inventory.append(self.weapon) 
                        self.weapon = chosen_item
                        self.damage = chosen_item.damage
                        self.inventory.remove(chosen_item) # надетый предмет удаляется из инвентаря

                    case _:
                        self.armor = 0 # обнуление брони для последующего перерасчета
                        
                        # надевание брони в нужный слот
                        if chosen_item.type == 'Шлем':
                            if self.head is not None: # если у персонажа уже есть шлем он падает в инвентарь
                                self.inventory.append(self.head)
                            self.head = chosen_item
                            
                        elif chosen_item.type == 'Нагрудник':
                            if self.body is not None: 
                                self.inventory.append(self.body)
                            self.body = chosen_item
                                                    
                        elif chosen_item.type == 'Штаны':
                            if self.pants is not None: 
                                self.inventory.append(self.pants)
                            self.pants = chosen_item

                        elif chosen_item.type == 'Сапоги':
                            if self.boots is not None: 
                                self.inventory.append(self.boots)
                            self.boots = chosen_item

                        self.inventory.remove(chosen_item) # предмет инвентаря удаляется  
                        
                        # перерасчет брони  
                        if self.head is not None:
                            self.armor += self.head.defence
                        if self.body is not None:
                            self.armor += self.body.defence
                        if self.pants is not None:
                            self.armor += self.pants.defence
                        if self.boots is not None:
                            self.armor += self.boots.defence
            else:
                print('\nНеправильный индекс')
     
    def gain_level(self):# увеличение уровня питомца
        if self.exp >= self.exp_per_level:
            while self.exp >= self.exp_per_level:
                self.exp -= self.exp_per_level
                self.level += 1
                self.skill_points += 1
                self.update_exp_per_level()
                
    def pet_upgrade(self):
        print('\n(1) - Увеличить уровень'
              '\n(2) - Улучшить показатели')
        pet_choice = input()
        
        match pet_choice:
            case '1':
                print(f'{format_money(player.money)}$')
                print('\nСколько денег вы бы хотели вложить в питомца?')
                amount = input()
                valid_amount = digit_check(amount)
                player.money -= valid_amount
                player.statistics.add_statistics(valid_amount, 'расход') # Учет трат в статистику
                self.exp += valid_amount
                self.gain_level()
                print(f'\nВы успешно вложили {valid_amount}$ в своего питомца'
                    f'\nТеперь он имеет {self.level} уровень, до следующего уровня ему осталось {self.exp_per_level - self.exp}')
                pause()
            
            case '2':
                print(f'\nОчков навыков: {self.skill_points} ')
                print('\n(1) - Макс. здоровье'
                      '\n(2) - Уклонение'
                      '\n(3) - Точность'
                      '\n(4) - Крит. шанс'
                      '\n(5) - Блид. шанс'
                      '\n(6) - Блид. урон')
                skill_choice = input()
                print('\nСколько очков вы бы хотели вложить?')
                points = input()
                valid_points = digit_check(points)
                if valid_points <= self.skill_points:
                    match skill_choice:
                        case '1':
                            self.health += valid_points
                            self.skill_points -= valid_points
                        
                        case '2':
                            self.miss += valid_points
                            self.skill_points -= valid_points 
                            
                        case '3':
                            self.accuracy += valid_points
                            self.skill_points -= valid_points
                        
                        case '4':
                            self.crit_chance += valid_points
                            self.skill_points -= valid_points
                        
                        case '5':
                            self.bleed_chance += valid_points
                            self.skill_points -= valid_points
                        
                        case '6':
                            self.bleed_damage += valid_points * 2
                            self.skill_points -= valid_points 
                                  
                else:
                    print('\nУ вас нет столько очков навыков')
    
    def create_random_enemy(self):
        name = random.choice(enemy_names)
        type = random.choice(enemy_types)
        damage = round(random.uniform(self.damage * 0.75, self.damage * 1.25))
        armor = round(random.uniform(self.armor * 0.75, self.armor * 1.25))
        health = round(random.uniform(self.health * 0.75, self.health * 1.25))
        miss = round(random.uniform(self.miss * 0.75, self.miss * 1.25))
        accuracy = round(random.uniform(self.accuracy * 0.75, self.accuracy * 1.25))
        crit_chance = round(random.uniform(self.crit_chance * 0.75, self.crit_chance * 1.25))
        bleed_chance = round(random.uniform(self.bleed_chance * 0.75, self.bleed_chance * 1.25))
        bleed_damage = round(random.uniform(self.bleed_damage * 0.75, self.bleed_damage * 1.25))
        
        enemy = Pet_fighter(type, name, health,armor, damage, miss, accuracy, crit_chance, bleed_chance, bleed_damage)
        return enemy
                        
    def attack(self, enemy): # механика нанесения урона
        armor_perks = [] # создание списка и добавление в него перков брони противника
        if enemy.head is not None:
            armor_perks.append(enemy.head.specialty)
        if enemy.body is not None:
            armor_perks.append(enemy.body.specialty)
        if enemy.pants is not None:   
            armor_perks.append(enemy.pants.specialty)
        if enemy.boots is not None:
            armor_perks.append(enemy.boots.specialty)
        
        damage = self.damage
        hit = random.randint(0, 100)
        miss_chance = ((enemy.miss / 2) / self.accuracy) * 100 # расчет шанса попасть исходя из рейтинга точности и уклонения
        
        if "Изворотливый" in armor_perks: # проверка на трейт брони изворотливость
            if hit < miss_chance * 2:
                return print("ПРОМАХ")
        
        if hit < miss_chance: # Не попал по противнику
            return print('ПРОМАХ')
        
        crit = random.randint(0, 100)
        bleed = random.randint(0, 100)
        fire = random.randint(0, 100)
        
        if crit < min(self.crit_chance, 80): #Проверка на крит
            damage *= 2
            print('КРИТИЧЕСКИЙ УДАР!')
        
        if self.weapon is not None and self.weapon.specialty == 'Невосприимчивый':# проверка на трейт моего оружия невосприимчивый
            pass
        elif "Драконий" in armor_perks: # проверка на трейт брони противника драконий
            damage = max(damage - enemy.armor *2, 1)
        else:   
            damage = max(damage - enemy.armor, 1) # урон с учетом брони
        
        if 'Заживляющий' in armor_perks:
            pass
        else:
            # Расчет блида
            if enemy.bleeding > 0: #проверка на наличие блида у противника
                damage += self.bleed_damage
                already_bleeding = True # переменная что блид уже наложен и нет смысла накладывать его еще раз
                enemy.bleeding -= 1 # -1 ход блида
            elif enemy.bleeding <= 0:
                already_bleeding = False
            
            if bleed < min(self.bleed_chance, 80) and already_bleeding == False: # Проверка прокнул ли блид или есть ли он уже
                enemy.bleeding = 3
                damage += self.bleed_damage
                print('НАЛОЖЕН ЭФФЕКТ КРОВОТЕЧЕНИЯ!')
        
        if self.weapon is not None and self.weapon.specialty == 'Пламенный' and fire <= 33: # проверка на трейт моего оружия пламенный
            damage += 30
            print('ДОП УРОН ОГНЕМ')
        
        # Нанесение финального урона
        if self.weapon is not None and self.weapon.specialty == 'Смертельный': # проверка на трейт моего оружия смертельный
            death = random.randint(0,100)
            if death <= 5:
                enemy.health -= enemy.health
            else:
               enemy.health -= damage 
        else:   
            enemy.health -= damage
            if 'Шипованный' in armor_perks: # проверка на трейт брони противника шипованный
                self.health -= round(damage * 0.2)
                print(f'Отдача от шипованной брони {round(damage * 0.2)}')
       
        if self.weapon is not None and self.weapon.specialty == 'Вампирский': # проверка на трейт моего оружия вампирский
            self.health += round(damage * 0.2)
            print(f'Восстановлено {round(damage * 0.2)} хп вамиризмом')
        print(f'Урона нанесено {damage}')
    
    def is_dead(self, enemy): # проверка на конец боя
        if enemy.health <= 0:
            print('\nПобеда')
            self.wins += 1
            drop = create_item()
            self.inventory.append(drop)
            print('Вам выпало снаряжение с противника!')
            return True
        
        elif self.health <= 0:
            print('\nНе победа')
            self.loses += 1
            return True
        
    def fight(self): # механика сражения +ВНУТРИ ЕЩЕ ФУНКЦИЯ ВОССТАНОВЛЕНИЯ ХП НЕ ТЕРЯТЬ!
        start_health = self.health
        def recover(creature): # функция восстановления хп до первичного значения
            creature.health = start_health
        
        enemy = self.create_random_enemy()
        
        def fight_info(pet, enemy): # функция вывода информации о петах во время боя
            print(f"\nПротивник:                       Вы:"
                  f"\nХп: {enemy.health}                           Хп: {pet.health}"
                  f"\nБроня: {enemy.armor}                         Броня: {pet.armor}"
                  f"\nУрон: {enemy.damage}                         Урон: {pet.damage}")
        
        my_miss_chance =  min(((enemy.miss / 2) / self.accuracy) * 100, 100)
        enemy_miss_chance = min(((self.miss/ 2) / enemy.accuracy) * 100, 100)
        print(f"\nВаш противник: {enemy.type}, по прозвищу {enemy.name}. Ваши характеристики:"
              f"\nПротивник:                       Вы:"
              f"\nХп: {enemy.health}                           Хп: {self.health}"
              f"\nБроня: {enemy.armor}                         Броня: {self.armor}"
              f"\nУрон: {enemy.damage}                         Урон: {self.damage}"
              f"\nШанс крита {enemy.crit_chance}%                  Шанс крита {self.crit_chance}%"
              f"\nШанс блида {enemy.bleed_chance}%                  Шанс блида {self.bleed_chance}%"
              f"\nШанс промаха {round(enemy_miss_chance)}%                 Шанс промаха {round(my_miss_chance)}%")
        print('\nХотите начать сражение?'
              '\n(1) - Да    (2) - Нет')
        fight_confirm = input()
        
        match fight_confirm:
            case '1':
                while True:
                    if self.is_dead(enemy): # проверка смерти
                        recover(player.pet)
                        break
                    print('Ваш ход:')
                    self.attack(enemy) # моя атака
                    if self.is_dead(enemy): # проверка смерти
                        recover(player.pet)
                        break
                    fight_info(player.pet, enemy)
                    pause()
                    print('Ход противника:')
                    enemy.attack(player.pet) # атака противника
                    if self.is_dead(enemy): # проверка смерти
                        recover(player.pet)
                        break
                    fight_info(player.pet, enemy)
                    pause()
                              
            case _:
                print('Слабачок)')
                
    def pet_gameplay(self):# выбор действий пета
        print('\nЧто бы вы хотели делать со своим питомцем дальше?'
                '\n(1) - Улучшить'
                '\n(2) - Учавствовать в выставке'
                '\n(3) - Учавствовать в драке'
                '\n(4) - Надеть вещь из инвентаря'
                '\n(5) - Продать вещь из инвентаря'
                '\n(6) - Посмотреть экипировку'
                '\n(7) - Турнир'
                '\n(8) - Слияние предметов')
        pet_choice = input()
        
        match pet_choice:
            case '1':
                self.pet_upgrade()
            case '2':
                self.competition()
            case '3':
                self.fight()
            case '4':
                self.inventory_choice()
            case '5':
                self.sell_item()
            case '6':
                self.show_equipment()
            case '7':
                self.pet_cup()
            case '8':
                self.merge()
    
    def show_inventory(self): # функция перечисления преметов в инвентаре
        if len(self.inventory) > 0:
            for i, item in enumerate(self.inventory):
                match item.type:
                    case 'Weapon':
                        print(f'{i}: Название: {item.name}, Урон: {item.damage}, Цена: {item.cost}, Редкость: {item.rarity}')
                        if item.specialty != '':
                            print(f'Особенность: {item.specialty}')
                    case _:
                        print(f'{i}: Название: {item.name}, Броня: {item.defence}, Цена: {item.cost}, Редкость: {item.rarity}, Тип брони: {item.type}')
                        if item.specialty != '':
                            print(f'Особенность: {item.specialty}')
            print("\n(Введите -1 чтобы выйти)")
            
        else:
            print("\nВаш инвентарь пуст"
                  "\n(Введите -1)")
                
    def sell_item(self):# продажа вещи из инвентаря
        while True:
            print('\nВыберите предмет:')
            self.show_inventory()
            item_choice = input()
            if item_choice == '-1':
                break
            valid_choice = digit_check(item_choice)
            if 0 <= valid_choice < len(self.inventory): 
                chosen_item = self.inventory[valid_choice]    
                player.money += chosen_item.cost 
                player.statistics.add_statistics(chosen_item.cost, 'доход')  
                self.inventory.remove(chosen_item)
                print(f"\n{chosen_item.name} Успешно продан за {chosen_item.cost}!")

    def show_equipment(self):# показ надетых вещей
        print()
        if self.head != None:
            print(f'Название: {self.head.name}, Урон: {self.head.defence}, Цена: {self.head.cost}, Редкость: {self.head.rarity}')
            if self.head.specialty != '':
                print(f'Особенность: {self.head.specialty}')
        if self.body != None:
            print(f'Название: {self.body.name}, Урон: {self.body.defence}, Цена: {self.body.cost}, Редкость: {self.body.rarity}')
            if self.body.specialty != '':
                print(f'Особенность: {self.body.specialty}')
        if self.pants != None:
            print(f'Название: {self.pants.name}, Урон: {self.pants.defence}, Цена: {self.pants.cost}, Редкость: {self.pants.rarity}')
            if self.pants.specialty != '':
                print(f'Особенность: {self.pants.specialty}')
        if self.boots != None:
            print(f'Название: {self.boots.name}, Урон: {self.boots.defence}, Цена: {self.boots.cost}, Редкость: {self.boots.rarity}')
            if self.boots.specialty != '':
                print(f'Особенность: {self.boots.specialty}')
        if self.weapon != None:
            print(f'Название: {self.weapon.name}, Урон: {self.weapon.damage}, Цена: {self.weapon.cost}, Редкость: {self.weapon.rarity}')
            if self.weapon.specialty != '':
                print(f'Особенность: {self.weapon.specialty}')
        pause()

    def merge(self):
        while True:
            print('\nВыберите 2 предмета из инвентаря для их слияния:')
            self.show_inventory()
            chosen_item_1 = input()
            if chosen_item_1 == '-1':
                break
            chosen_item_2 = input()
            if chosen_item_2 == '-1':
                break
            valid_item_1 = digit_check(chosen_item_1)
            valid_item_2 = digit_check(chosen_item_2)
            if 0 <= valid_item_1 < len(self.inventory) and 0 <= valid_item_2 < len(self.inventory):
                chosen_item_1 = self.inventory[valid_item_1]
                chosen_item_2 = self.inventory[valid_item_2]
                merge_items(chosen_item_1, chosen_item_2)
                    
    def pet_cup(self):
        print("\nДобро пожаловать на турнир!")
        fight_round = 1
        while True:
            win_check_start = self.wins
            print(f"\nСейчас {fight_round} раунд, готовы сражаться?"
                  '\n(1) - Да    (2) - Нет')
            cup_choice = input()
            if cup_choice == '1':
                self.fight()
                win_check_end = self.wins
                if win_check_end > win_check_start:
                    if fight_round == 4:
                        print("\nВы победили, вам достается награда!")
                        for i in range(5):
                            item = create_item()
                            self.inventory.append(item)
                        break
                    else:
                        fight_round += 1
                        continue
                else:
                    break
            if cup_choice == '2':
                break


class Armor:
    def __init__(self, name, defence, cost = 0, rarity = 'Обычный', type = 'Armor', specialty = '') -> None:
        self.name = name
        self.defence = defence
        self.cost = cost
        self.rarity = rarity 
        self.specialty = specialty
        self.type = type
        
    def stat_check(self): # Улучшение статов от редкости предмета
        match self.rarity:
            case 'Обычный':
                self.defence *= 1
            
            case 'Редкий':
                self.defence = round(self.defence * 1.5)
                
            case 'Мифический':
                self.defence *= 2
                
            case 'Легендарный':
                perk = random.choice(armor_perks)
                self.defence *= 3
                self.specialty = perk
        self.cost = self.defence * 1_000

       
class Weapon:
    def __init__(self, name, damage, cost, rarity, specialty = '') -> None:
        self.name = name
        self.damage = damage
        self.cost = cost
        self.rarity = rarity # common, rare, mythic, legendary
        self.specialty = specialty
        self.type = 'Weapon'

    def stat_check(self): # Улучшение статов от редкости предмета
        match self.rarity:
            case 'Обычный':
                self.damage *= 1
            
            case 'Редкий':
                self.damage = 2
                
            case 'Мифический':
                self.damage *= 3
                
            case 'Легендарный':
                perk = random.choice(weapon_perks)
                self.damage *= 5
                self.specialty = perk # брать из списка из соответствующего файла
        self.cost = self.damage * 1_000
   

class Birja:
    def __init__(self) -> None:
        self.companies = [
            {'Name': 'Apple', 'Amount': 752400, 'Price': 1347},
            {'Name': 'Google', 'Amount': 687000, 'Price': 1340},
            {'Name': 'Microsoft', 'Amount': 100010, 'Price': 3670},
            {'Name': 'Alibaba', 'Amount': 934800, 'Price': 1789},
            {'Name': 'Tesla', 'Amount': 478000, 'Price': 7890},
            {'Name': 'SpaceX', 'Amount': 968000, 'Price': 1089},
            {'Name': 'Gazprom', 'Amount': 574000, 'Price': 1890},
            {'Name': 'Ford', 'Amount': 568000, 'Price': 17890},
            {'Name': 'IBM', 'Amount': 998000, 'Price': 13890}
        ]
        self.portfolio = [
            {'Name': 'Apple', 'Amount': 0, 'Price': 1347, 'InitialPrice': 1347, 'PriceChange': 0.0},
            {'Name': 'Google', 'Amount': 0, 'Price': 134, 'InitialPrice': 134, 'PriceChange': 0.0},
            {'Name': 'Microsoft', 'Amount': 0, 'Price': 367, 'InitialPrice': 367, 'PriceChange': 0.0},
            {'Name': 'Alibaba', 'Amount': 0, 'Price': 1789, 'InitialPrice': 1789, 'PriceChange': 0.0},
            {'Name': 'Tesla', 'Amount': 0, 'Price': 789, 'InitialPrice': 789, 'PriceChange': 0.0},
            {'Name': 'SpaceX', 'Amount': 0, 'Price': 1089, 'InitialPrice': 1089, 'PriceChange': 0.0},
            {'Name': 'Gazprom', 'Amount': 0, 'Price': 189, 'InitialPrice': 189, 'PriceChange': 0.0},
            {'Name': 'Ford', 'Amount': 0, 'Price': 17890, 'InitialPrice': 17890, 'PriceChange': 0.0},
            {'Name': 'IBM', 'Amount': 0, 'Price': 178900, 'InitialPrice': 13890, 'PriceChange': 0.0}
        ]
        self.income = 0
        self.days = 0
        self.price_history = {company['Name']: [] for company in self.companies}
        self.long_term_trends = {company['Name']: 0.02 for company in self.companies}  # Например, 2% годового роста

    def birja_update(self, dt=1):
        self.days += 1
        self.income = 0  
        for company in self.companies:
            drift = 0.08  # Дрифт (среднегодовая доходность акций)
            volatility = 0.2  # Волатильность (стандартное отклонение доходности акций)
            
            # Генерируем случайное изменение в соответствии с броуновским движением
            epsilon = np.random.normal(0, 1) * np.sqrt(dt)
            
            # Определяем максимальное изменение цены, например, в пределах 5% от текущей цены
            max_price_change_percentage = 5.0
            max_price_change = company['Price'] * (max_price_change_percentage / 100.0)
            
            # Вычисляем новую цену акций с учетом ограничения
            new_price = company['Price'] * np.exp((drift - 0.5 * volatility**2) * dt + volatility * epsilon)
            
            # Применяем долгосрочный тренд
            new_price *= (1 + self.long_term_trends[company['Name']])
            
            # Устанавливаем верхний и нижний пороги для цены акций
            upper_limit = 1_000_000  # Верхний порог
            lower_limit = 0.01    # Нижний порог (минимальная цена)
            new_price = max(lower_limit, min(upper_limit, new_price))
            
            new_price = round(new_price, 2)
            
            # Вычисляем процент изменения цены
            price_change_percentage = ((new_price - company['Price']) / company['Price']) * 100
            
            company['Price'] = new_price
            
            # добавление истории цен
            if len(self.price_history[company['Name']]) >= 50:
                self.price_history[company['Name']].pop(0)  # Удаляем старые данные
            self.price_history[company['Name']].append(new_price)
            
            matching_portfolio_company = next((stock for stock in self.portfolio if stock['Name'] == company['Name']), None)
            if matching_portfolio_company:
                matching_portfolio_company['Price'] = new_price
                matching_portfolio_company['PriceChange'] = price_change_percentage
    
        for stock in self.portfolio:
            if stock["Amount"] > 0:
                self.income += round((stock["Amount"] + stock['Price']) * 0.05)
                
    def plot_price_history(self):
        for company_name, prices in self.price_history.items():
            plt.plot(range(max(1, self.days - 49), self.days + 1), prices[-50:], label=company_name)

        plt.xlabel('Days')
        plt.ylabel('Price')
        plt.title('Stock Price History')
        plt.legend()
        plt.grid(True)
        plt.show()


class Tree:
    def __init__(self, fruit, type, age) -> None:
        self.fruit = fruit
        self.type = type
        self.age = age


class Fruit:
    def __init__(self, type, price) -> None:
        self.type = type
        self.sugar = 0
        self.water = 0
        self.kcl = 0
        self.price = price
  
                  
def pause():# ENTER to continue
    print('(ENTER)')
    x = input()
    
def name_check(name): # Проверка на наличие цифр в имени
    while True:
        if not name:
            print("\nЭта строчка не может быть пустой.")
        elif not all(char.isalpha() for char in name):
            print("\nЭта строчка может содержать только буквы.")
        else:
            print('\nВсе в порядке!')
            return name
        name = input('Введите корректное имя: ').capitalize()

def digit_check(digit):# Проверка на наличие букв в числе
    while True:
        if not digit:
            print("\nЭта строчка не может быть пустой.")
            
        elif not all(char.isdigit() for char in digit):
            print("\nЭта строка может содержать только целые числа.")

        elif int(digit) < 0:
            print('Это число не может быть отрицательным')

        else:
            return int(digit)
        digit = input('Введите корректное число: ')        

def is_prime(num): # Проверка на четность
    return num % 2 != 0

def format_money(amount): # переделка денег в читаемые
    if abs(amount) >= 1_000_000_000_000_000:
        return f'{amount / 1_000_000_000_000_000: .3f} квадрилионов'
    elif abs(amount) >= 1_000_000_000_000:
        return f'{amount / 1_000_000_000_000:.3f} трлн.'
    elif abs(amount) >= 1_000_000_000:
        return f'{amount / 1_000_000_000:.3f} млрд.'
    elif abs(amount) >= 1_000_000:
        return f'{amount / 1_000_000:.3f} млн.'
    elif abs(amount) >= 10_000:
        return f'{amount / 1_000:.3f} тыс.'
    else:
        return str(amount)
           
def farm_creation():# содание фермы 
    global valid_farm_name
    print(f'\nВам досталась ферма в наследство,'
        f'\nОна давно заросла и вам придется привести ее в порядок'
        f'\nНо для начала придумайте ей название:')
    farm_name = input()
    valid_farm_name = name_check(farm_name).capitalize()
    print(f'\nОтличное название, теперь ферма называется {valid_farm_name}')

def birja_creation():
    birja = Birja()
    return birja

def pet_creation():# создание пета
    print('\nЗавести питомца будет совершенно бесплатно!'
          '\nДля начала выберите тип питомца например: кошка, собака, свинья')
    pet_type = input().capitalize()
    valid_type = name_check(pet_type)
    print('\nТеперь вы можете назвать своего питомца!')
    pet_name = input().capitalize()
    valid_name = name_check(pet_name)
    pet = Pet_fighter(valid_type, valid_name)
    player.pet = pet
    print(f'\nПоздравляем, вы завели питомца типа {player.pet.type} и назвали его {player.pet.name}')

def zoo_creation():# Создание и покупка зоопарка
    print(f'\nКупить зоопарк будет стоить 3 000 000$'
          '\nУверены что хотите купить?'
          '\n(1) - Да    (2) - Нет')
    zoo_choice = input()
    
    match zoo_choice:
        case '1' if player.money >= 3_000_000:
            player.money -= 3_000_000
            player.statistics.add_statistics(3_000_000, 'расход')
            print('Придумайте название своему новому зоопарку!')
            zoo_name = input()
            valid_zoo_name = name_check(zoo_name)
            zoo = Zoo(valid_zoo_name)
            player.zoo = zoo
            print(f'\nПоздравляем вас с покупкой зоопарка {player.zoo.name}')
        
        case '2':
            print('\nПриходите если надумаете!')
            
        case _:
            print('\nПри покупке что-то пошло не так.')       

def create_item(): # создание предмета дропа
    rarity = random.randint(0, 100)
    if rarity <= 60:
        rareness = 'Обычный'
    elif 60 < rarity <= 80:
        rareness = 'Редкий'
    elif 80 < rarity <= 95:
        rareness = 'Мифический'
    else:
        rareness = 'Легендарный'
    drop_type = random.randint(0, 1)
    match drop_type:
        case 1:
            damage = random.randint(10, 40)
            name = random.choice(weapon_names)
            item = Weapon(name, damage, 0, rareness)
            item.stat_check() # проверка на редкость и баф от этого
            return item
        case 0:
            armor_drop = random.randint(0, 100)
            if armor_drop <= 25:
                armor_name = random.choice(armor_names_body)
                armor_type = 'Нагрудник'
            elif 25 < armor_drop <= 50:
                armor_name = random.choice(armor_names_boots)
                armor_type = 'Сапоги'
            elif 50 < armor_drop <= 75:
                armor_name = random.choice(armor_names_head)
                armor_type = 'Шлем'
            elif 75 < armor_drop <= 100:
                armor_name = random.choice(armor_names_legs)
                armor_type = 'Штаны'
            defence = random.randint(10, 40)     
            item = Armor(armor_name, defence, 0, rareness, armor_type) 
            item.stat_check() # проверка на редкость и баф от этого
            return item
  
def merge_items(item_1, item_2): # совмещение предметов
    
        if item_1.type != item_2.type or item_1 == item_2:
            print('\nЭти предметы нельзя совместить')
            
        elif item_1.type == 'Weapon':
            new_damage = item_1.damage + item_2.damage
            if item_1.damage >= item_2.damage:
                new_name = item_1.name
            else:
                new_name = item_2.name
            if item_1.rarity == 'Легендарный' or item_2.rarity == 'Легендарный':
                new_rarity = 'Легендарный'
            else:
                new_rarity = 'Мифический'
            if item_1.specialty != '' or item_2.specialty != '':
                new_specialty = random.choice(weapon_perks)
            else:
                new_specialty = ''
            new_item = Weapon(new_name, new_damage, 0, new_rarity, new_specialty)
            new_item.stat_check()
            player.pet.inventory.append(new_item)
            print('\nВы успешно совместили два предмета!')
            player.pet.inventory.remove(item_1)
            player.pet.inventory.remove(item_2)
            
        else:
            new_defence = item_1.defence + item_2.defence
            if item_1.defence >= item_2.defence:
                new_name = item_1.name
            else:
                new_name = item_2.name
            if item_1.rarity == 'Легендарный' or item_2.rarity == 'Легендарный':
                new_rarity = 'Легендарный'
            else:
                new_rarity = 'Мифический'
            if item_1.specialty != '' or item_2.specialty != '':
                new_specialty = random.choice(armor_perks)
            else:
                new_specialty = ''
            new_item = Armor(new_name, new_defence, 0, new_rarity, item_1.type, new_specialty)
            new_item.stat_check()
            player.pet.inventory.append(new_item)
            print('\nВы успешно совместили два предмета!')
            player.pet.inventory.remove(item_1)
            player.pet.inventory.remove(item_2)

def load_from_file(): # Загрузка Player
    with open('c:\\Users\\Public\\Documents\\save.pkl', 'rb') as file:
        return pickle.load(file) 
     
                     
while True: # выбор новая игра или загрузка
    print('\n(1) - Новая игра'
          '\n(2) - Загрузить игру')
    start_choice = input()

    match start_choice:
        case '1':
            print('\nПридумайте себе имя:')
            my_name = input()
            valid_name = name_check(my_name).capitalize()
            print(f'\nПриятно познакомиться, {valid_name}')
            farm_creation()
            birja = birja_creation()
            my_farm = Farm(valid_farm_name)
            statistics = Statistics()
            player = Player(my_farm, None, statistics, None, valid_name, birja)
            break
            
        case '2':
            player = load_from_file()
            print(f'\nДобро пожаловать обратно, {player.name}!')
            break


def game():
    while True:
        start_time = time.time()
        player.save_to_file('c:\\Users\\Public\\Documents\\save.pkl')
        player.player_update()
        end_time = time.time()
        total_time = (end_time - start_time) / 1000 # Время на обновление персонажа и всей хуйни в миллисекундах
        print(f'{str(total_time)[:4]}мс.') # округляю до двух знаков после запятой через превращение в строку потому что ебучий питон при обычном округлении ебет мне мозги и превращает число в 0.00мс
        if game_over: # Проигрыш из-за банкротства
            break
        
        print('\nЧто будем делать дальше?'
              '\n(1) - Управление фермой           (5) - Достижения'
              '\n(2) - Управление зоопарком        (6) - Казино            (9) - Биржа '
              '\n(3) - Кредит                      (7) - Обучение          (0)  - Выход'
              '\n(4) - Питомец                     (8) - Статистика')
        choice = input()
        
        match choice:
            case '1':
                player.upgrades()
                
            case '2':
                if player.zoo == None:
                    zoo_creation()
                else:
                    player.zoo_upgrades()
            
            case '3':
                player.get_loan()
                
            case '4':
                if player.pet == None:
                    pet_creation()
                else:
                    player.pet.pet_gameplay()
                    
            case '5':
                player.statistics.show_achiev_competition() 
            
            case '6':
                player.casino()
                    
            case '7':
                FAQ()
                
            case '8':
                player.statistics.show_stats()
            
            case '9':
                player.Birja()
                
            case '0':
                break
                 

if __name__ == '__main__':
    game()
    