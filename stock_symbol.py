import csv

class StockSearcher:

    def __init__(self):
        self.sorted_name_list = [[], []]
        self.sorted_symbol_list = [[], []]
        # Converting the csv files into lists so we can do binary search
        with open("nasdaq_screener_sorted_name.csv", "r") as sorted_name:
            csv_reader = csv.reader(sorted_name, delimiter=",")
            for row in csv_reader:
                self.sorted_name_list[0].append(row[0])
                self.sorted_name_list[1].append(row[1])

        with open("nasdaq_screener_sorted_symbol.csv") as sorted_symbol:
            csv_reader = csv.reader(sorted_symbol, delimiter=",")
            for row in csv_reader:
                self.sorted_symbol_list[0].append(row[0])
                self.sorted_symbol_list[1].append(row[1])

    def lower_bound_name(self, char, char_index, low, high):
        if low > high:
            return low

        mid = low + (high-low) // 2

        if char_index >= len(self.sorted_name_list[1][mid]):
            return low

        if ord(self.sorted_name_list[1][mid][char_index].lower()) >= ord(char.lower()):
            return self.lower_bound_name(char, char_index, low, mid-1)
        else:
            return self.lower_bound_name(char, char_index, mid+1, high)

    def upper_bound_name(self, char, char_index, low, high):
        if low > high:
            return low

        mid = low + (high-low) // 2

        if char_index >= len(self.sorted_name_list[1][mid]):
            return low

        if ord(self.sorted_name_list[1][mid][char_index].lower()) > ord(char.lower()):
            return self.upper_bound_name(char, char_index, low, mid-1)
        else:
            return self.upper_bound_name(char, char_index, mid+1, high)

    def search_by_name(self, search_query):
        # Binary search
        min_index = 0
        max_index = len(self.sorted_name_list[1]) - 1

        for index, char in enumerate(search_query):
            min_index = self.lower_bound_name(char, index, min_index, max_index)
            max_index = self.upper_bound_name(char, index, min_index, max_index)

        return min_index, max_index

    def lower_bound_symbol(self, char, char_index, low, high):
        if low > high:
            return low

        mid = low + (high-low) // 2

        if char_index >=len(self.sorted_symbol_list[0][mid]):
            return low

        if ord(self.sorted_symbol_list[0][mid][char_index].lower()) >= ord(char.lower()):
            return self.lower_bound_symbol(char, char_index, low, mid-1)
        else:
            return self.lower_bound_symbol(char, char_index, mid+1, high)

    def upper_bound_symbol(self, char, char_index, low, high):
        if low > high:
            return low

        mid = low + (high-low) // 2

        if char_index >=len(self.sorted_symbol_list[0][mid]):
            return low

        if ord(self.sorted_symbol_list[0][mid][char_index].lower()) > ord(char.lower()):
            return self.upper_bound_symbol(char, char_index, low, mid-1)
        else:
            return self.upper_bound_symbol(char, char_index, mid+1, high)

    def search_by_symbol(self, search_query):
        # Binary search
        min_index = 0
        max_index = len(self.sorted_symbol_list[1]) - 1

        for index, char in enumerate(search_query):
            min_index = self.lower_bound_symbol(char, index, min_index, max_index)
            max_index = self.upper_bound_symbol(char, index, min_index, max_index)

        return min_index, max_index

# s = StockSearcher()
# low, high = s.search_by_name("apple")
# for i in range(low, high):
#     print(s.sorted_name_list[0][i], s.sorted_name_list[1][i])

# with open("nasdaq_screener_sorted_name.csv", "r") as sorted_name:
#     with open("nasdaq_screener_sorted_name_2.csv", "w") as sorted_name_2:
#         lines = sorted_name.readlines()
#         lines.sort(key=lambda a: a.split(",")[1].lower().rstrip("\n"))
#         sorted_name_2.writelines(lines)