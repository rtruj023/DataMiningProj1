import sys

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
        support_counts[item] = 1
    else:
        support_counts[item] = support_counts[item] + 1
    last_id = trans_id

#Setting the length 1 itemsets, as lists of one element
candidate_items[1] = [[item] for item in items]

#Generate F1(frequent 1-itemsets)
for item in items:
    if support_counts[item] >= min_supp:
        frequent_items[1] += [item]

print(frequent_items.get(1))

#Functions for generating output files

#A user defined function that generates a file of the frequent itemsets
# and their respective support counts
def make_items_file(dictionary, file_name):
    with open(file_name, 'w') as f:
        f.write("ITEMSETS|SUPPORT_COUNT")
        for itemset in dictionary:
            itemset_str = " ".join(str(item) for item in itemset)
            sCount = support_counts[itemset]
            f.write(itemset_str + "|" + sCount + "\n")

#A user defined function that generates a file of the high-confidence frequent rules
def make_rules_file(dictionary, file_name):
    with open(file_name, "w") as f:
        f.write("LHS|RHS|SUPPORT_COUNT|CONFIDENCE")
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
        f.write("minsuppc: " + minsuppc + "\n")
        f.write("minconf: " + minconf + "\n")
        f.write("input file: " + input_file + "\n")
        f.write("output name: " + output_name + "\n")

#Generating example files

make_items_file(frequent_items,"example_items.txt")
make_rules_file(rules,"example_rules.txt")
make_info_file(min_supp, min_conf, file_name,out_file_name, "example_info.txt")




