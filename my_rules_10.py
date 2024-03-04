import sys
import itertools
import matplotlib
from functools import reduce

#A Dictionary with the transaction Ids, not ordered since it doesn't matter
transactions = {}
#The counts of the different items
support_counts = {}
#The list of available items that have been shown
items = []
#Minimum support count
min_supp = float(sys.argv[1])
#Minimum confidence rule
min_conf = float(sys.argv[2])
#The input file name
file_name = sys.argv[3]
#Output file name
out_file_name = sys.argv[4]
#Frequent itemsets, a dictionary where the key is the length of the frequent itemsets, so of length 2 is found
#in frequent_items[2] = [['x','y'], ['a', 'b']] 
frequent_items = {}
#Candidates, a dictionary where the key is the length of the candidate itemsets
candidate_items = {}
#Rules, they can be stored in the following format of [{"RH": [1,2,3], "LH": [5], "Confidence": 0.45}, {"RH": [67], "LH": [4, 5], "Confidence": 0.57}], where there are two rules, 1,2,3 -> 5
#and 67 -> 4,5 with confidence .45 and .57 respectively
rules = []
#The association rules, in the format of 
input_file = open(file_name)

#Section 1 reading inputs and setting up variables

#Section 1 reading inputs and setting up variables
last_id = -1
for line in input_file.readlines():
    trans_id = int(line.split(" ")[0])
    item = int(line.split(" ")[1])
    #Add to transactions
    if trans_id != last_id:
        new_item_list = [item]
        transactions[trans_id] = new_item_list
    else:
        transactions[trans_id].append(item)
    if item not in items:
        items.append(item)
        support_counts[str(item)] = 1
    else:
        support_counts[str(item)] = support_counts[str(item)] + 1
    last_id = trans_id

#Setting the length 1 itemsets, as lists of one element
candidate_items[1] = [[item] for item in items]
frequent_items[1] = []
#Generate F1(frequent 1-itemsets)
for item in items:
    if support_counts[str(item)] >= min_supp:
        frequent_items[1].append([item])

print(frequent_items.get(1))

item_length = 2
while len(frequent_items[item_length - 1]) > 0:
    frequent_items[item_length] = []
    candidate_items = []
    #Pruning
    for first_index, first_itemset in enumerate(frequent_items[item_length - 1]):
        for second_index, second_itemset in enumerate(frequent_items[item_length - 1][first_index + 1:]):
            if first_itemset[0:item_length - 2] == second_itemset[0:item_length - 2]:
                candidate = list(list(itertools.combinations(first_itemset + [second_itemset[-1]], item_length))[0])
                is_pruned = False
                for combo in itertools.combinations(first_itemset + [second_itemset[-1]], item_length - 1):
                    if list(combo) not in frequent_items[item_length - 1]:
                        is_pruned = True
                        break
                if not is_pruned:
                    candidate_items.append(candidate)
    #Eliminating
    for candidate in candidate_items:
        count = 0
        for key in transactions:
            not_found = False
            for item in candidate:
                if item not in transactions[key]:
                    not_found = True
                    break
            if not_found == False:
                count += 1
        if count > min_supp:
            frequent_items[item_length].append(candidate)
    item_length += 1


#Functions for generating output files

#A user defined function that generates a file of the frequent itemsets
# and their respective support counts
def make_items_file(dictionary, file_name):
    with open(file_name, 'w') as f:
        f.write("ITEMSETS|SUPPORT_COUNT\n")
        for key in dictionary:
            for itemset in dictionary[key]:
                itemset_str = " ".join(str(item) for item in itemset)
                itemset.sort()
                sCount = support_counts["|".join([str(x) for x in itemset])]
                f.write(itemset_str + "|" + str(sCount) + "\n")

#A user defined function that generates a file of the high-confidence frequent rules
def make_rules_file(dictionary, file_name):
    with open(file_name, "w") as f:
        f.write("LHS|RHS|SUPPORT_COUNT|CONFIDENCE\n")
        for rule in dictionary:
            lhs = " ".join(str(item) for item in rule['LH'])
            rhs = " ".join(str(item) for item in rule['RH'])
            sCount = rule['Support Count']
            confidence = rule['Confidence']
            f.write(lhs + "|" + rhs + "|" + sCount + "|" + confidence + "\n")

#A user defined function that generates a file which includes all information pertinent to this
#association rule mining program
def make_info_file(minsuppc,minconf, output_name,input_file,output_file_name):
    with open(output_file_name, "w") as f:
        f.write("minsuppc: " + str(minsuppc) + "\n")
        f.write("minconf: " + str(minconf) + "\n")
        f.write("input file: " + str(input_file) + "\n")
        f.write("output name: " + str(output_name) + "\n")

#Generating example files

make_items_file(frequent_items, out_file_name +"_items_10.txt")
make_rules_file(rules, out_file_name + "_rules_10.txt")
make_info_file(min_supp, min_conf, file_name,out_file_name, out_file_name + "_info_10.txt")

