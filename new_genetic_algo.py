import random
import numpy as np

generations = 1500
# try to make pop_size of even numbers
pop_size = 150
num_nurses = 13
num_days = 14
chance = 0.7

# different possible values for each nurse
shifts = ['O', 'M', 'E', 'N']


def initialisation():
    """This initializes the population randomly with possible values"""
    lis1 = []
    for day in range(num_nurses):
        lis2 = []
        for nurse in range(num_days):
            lis2.append(random.choice(shifts))
        lis1.append(lis2)

    return np.array(lis1)


dic = {}


# df is a numpy array of possible solutions
def n_shift(df):
    """n_shifts summarises the count for each shift in a day"""
    for day in range(num_days):
        lis = []
        for shift in shifts:
            try:
                lis.append(list(df[:, day]).count(shift))
            except:
                pass
        dic[day] = lis
    # dic {1:[3(0),4(1),3(2)], ...} forms the dictionary that shows on each day what are the number of different shifts provided to all nurses.
    return dic

dic2 = {}


def holiday_check(df):
    """holiday_check confirms that only one holiday in a week"""
    for nurse in range(num_nurses):
        lis = []
        # holidays in first week
        try:
            # number of holidays('o') in first seven days
            lis.append(list(df[nurse, 0:7]).count('O'))
        except:
            # if there is no holiday given in the first week.
            lis.append(0)
        # holidays in second week
        try:
            # number of holidays('o') in second seven days
            lis.append(list(df[nurse, 7:]).count('O'))
        except:
            lis.append(0)
        dic2[nurse] = lis

    # dic2 {'N1':[2(first week),4(second week), N2:[] ...} will return a dictionary in which each key present nurses and its corresponding value represent the list of
    # holidays in first and second week(count for number of '0' values in each week

    return dic2

# As an example:"NNNN" consecutive 4 night shifts might not be desirable under some law mandates
# like wise we can formulate such checks.
pattern = ['NNNN', 'NM']
dic3 = {}


def max_nightshifts(df):
    num_pattern = 0
    for nurse in range(num_nurses):
        for i in range(num_days - len(pattern)):
            t = str(df[nurse])
            if t[i:i + len(pattern)] == pattern:
                num_pattern += 1
        dic3[nurse] = num_pattern
    return dic3

# constraints on different shifts in a day
min_num_morning = 2
min_num_evening = 3
min_num_night = 3


def fitness(populations):
    """this fitness function will calculate the deviation from the desired outcome based on constrains"""
    # populations is a list of dataframes in the form [dataframe,...]
    lis = []
    for schedule in populations:
        imp = 0
        dic_shifts = n_shift(schedule)
        dic_holidays = holiday_check(schedule)
        dic_pattern = max_nightshifts(schedule)
        for day in range(num_days):
            # avalability of the nurses in morning, evening and night shifts are declared at the top
            if dic_shifts[day][1] < min_num_morning:
                imp += (min_num_morning - dic_shifts[day][1]) * 10
            if dic_shifts[day][2] < min_num_evening:
                imp += (min_num_evening - dic_shifts[day][2]) * 10
            if dic_shifts[day][3] < min_num_night:
                imp += (min_num_night - dic_shifts[day][3]) * 10

        for nurse in range(num_nurses):
            # law mandates and service levels are equally important
            if dic_holidays[nurse][0] != 1:
                imp += 20
            if dic_holidays[nurse][1] != 1:
                imp += 20
            # cost for the occurence of a particular pattern
            if dic_pattern[nurse] > 0:
                imp += dic_pattern[nurse] * 20  # appending a pair
        lis.append([schedule, imp])
    # we should rather return list of lists in the form [(dataframe,impurity),...} instead of simple list of impurities.
    return lis


def selection_2_cross(items):
    # item is list of tuples with [(dataframe,impurity)]
    distances = [i[1] for i in items]
    minn = min(distances)
    temp = sorted(distances)
    median = temp[int(len(distances) / 2)]
    n = random.uniform(minn, median)
    for schedule, weight in items:
        if weight <= n:
            return schedule


def crossover(item1, item2):
    one_point = int(random.uniform(1, 14))
    return (np.concatenate((item1[:, :one_point], item2[:, one_point:]), axis=1),
            np.concatenate((item2[:, :one_point], item1[:, one_point:]), axis=1))


def mutation(item, chance):
    for row in range(num_nurses):
        if random.random() > chance:
            point_2_change = int(num_days * random.random())
            item[row, point_2_change] = random.choice(shifts)
    return item


def finding(scored_populations):
    distances = [i[1] for i in scored_populations]
    print(distances)
    return sum(distances) / len(distances)



def final_action():
    # creating dictionary of population where dictt is the list of lists in the form of [[df_name,dataframe],...]
    populations = []
    for i in range(pop_size):
        populations.append(initialisation())

    # print(populations)
    for generation in range(generations):
        # scored_populations is the list of list in the form [(dataframe,impurity)] contains first element
        # as dataframe and second value represent impurity.
        scored_populations = fitness(populations)
        populations = []
        k = 1
        for i in range(int(pop_size / 2)):
            item1 = selection_2_cross(scored_populations)
            random.shuffle(scored_populations)
            item2 = selection_2_cross(scored_populations)
            if k == 1:
                print(item1)
                print(item2)
            item1, item2 = crossover(item1, item2)
            # print(item1.shape,item2.shape)
            if k == 1:
                print(item1)
                print(item2)
            k += 1
            populations.append(mutation(item1, chance))
            populations.append(mutation(item2, chance))
        print("In generation {0} random sample score average is {1}".format(generation, finding(scored_populations)))


final_action()
