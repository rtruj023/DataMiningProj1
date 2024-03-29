import sys
import itertools
import matplotlib.pyplot as plt
import time


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
        support_counts[str(item)] = 1
    else:
        support_counts[str(item)] = support_counts[str(item)] + 1
    last_id = trans_id
itemsCount = len(items)
#Setting the length 1 itemsets, as lists of one element
candidate_items[1] = [[item] for item in items]
frequent_items[1] = []

start_time = time.time()
#Generate F1(frequent 1-itemsets)
for item in items:
    if support_counts[str(item)] >= min_supp:
        frequent_items[1].append([item])



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

        if count >= min_supp:
            frequent_items[item_length].append(candidate)
            itemset_str = "|".join(str(item) for item in candidate)
            support_counts[itemset_str] = count

    item_length += 1

end_time = time.time()
#Variable that stores computational time in seconds of frequent itemset generation
frequent_itemset_time = end_time - start_time

start_time2 = time.time()
#Generating High Confidence Rules
for key in frequent_items:
    if key > 1:
        rule_itemsets = frequent_items[key]
        for items in rule_itemsets:
            for i in range(1,len(items)):
                for combination in itertools.combinations(items, i):
                    lhs = list(combination)
                    rhs = []
                    for x in items:
                        if x not in lhs:
                            rhs.append(x)
                    support_union = support_counts["|".join(str(item) for item in items)]
                    support_lhs = support_counts["|".join(str(item) for item in lhs)]
                    #Confidence = support count of itemset divided by the support count of LHS
                    confidence = support_union / support_lhs
                    if confidence >= min_conf:
                        rules.append({'LH': lhs, 'RH': rhs, 'Support Count': support_counts["|".join(str(item) for item in items)], 'Confidence': confidence})

end_time2 = time.time()
#Variables that stores computational time in seconds of high confidence rule generation
candidate_rules_time = end_time2 - start_time2

#Generating information/statistics for info file

#Variable that holds the length of the longest transaction
trans_len = 0
for item in transactions:
    current_trans = len(transactions[item])
    if current_trans > trans_len:
        trans_len = current_trans

#Variable that holds the length of the largest k-itemset
itemset_len = 0
for k in frequent_items:
    if len(frequent_items[k]) == 0:
        break
    if k > itemset_len:
        itemset_len = k

#Variable that stores the rule with the highest confidence
highest_rule = None
#Variable that stores the confidence of highest_rule
highest_conf = 0.00
for item in rules:
    if item['Confidence'] > highest_conf:
        highest_conf = item['Confidence']
        highest_rule = item

#Variable that holds the
total_num_itemsets = 0
for k in frequent_items:
    if len(frequent_items[k]) == 0:
        break
    total_num_itemsets += len(frequent_items[k])

#Functions for generating output files


#A user defined function that generates a file of the frequent itemsets
# and their respective support counts
def make_items_file(dictionary, file_name):
    with open(file_name, 'w') as f:
        for key in dictionary:
            for itemset in dictionary[key]:
                itemset_str = " ".join(str(item) for item in itemset)
                itemset.sort()
                sCount = support_counts["|".join([str(x) for x in itemset])]
                f.write(itemset_str + "|" + str(sCount) + "\n")

#A user defined function that generates a file of the high-confidence frequent rules
def make_rules_file(dictionary, file_name):
    if min_conf == -1:
        return
    with open(file_name, "w") as f:
        for rule in dictionary:
            lhs = " ".join(str(item) for item in rule['LH'])
            rhs = " ".join(str(item) for item in rule['RH'])
            sCount = rule['Support Count']
            confidence = "{:f}".format(rule['Confidence'])
            f.write(lhs + "|" + rhs + "|" + str(sCount) + "|" + confidence + "\n")

#A user defined function that generates a file which includes all information pertinent to this
#association rule mining program
def make_info_file(minsuppc,minconf, input_file, output_name, output_file_name):
    with open(output_file_name, "w") as f:
        f.write("minsuppc: " + str(minsuppc) + "\n")
        f.write("minconf: " + str(minconf) + "\n")
        f.write("input file: " + str(input_file) + "\n")
        f.write("output name: " + str(output_name) + "\n")
        f.write("Number of items: " + str(itemsCount) + "\n")
        f.write("Number of transactions: " + str(len(transactions)) + "\n")
        f.write("Length of the longest transaction: " + str(trans_len) + "\n")
        f.write("Length of the largest k-itemset: " + str(itemset_len) + "\n")

        #Loop for writing number of k-itemsets for key that is not empty
        for k in frequent_items:
            if len(frequent_items[k]) == 0:
                break
            current_num = len(frequent_items[k])
            f.write("Number of frequent " + str(k) + "-itemsets: " + str(current_num) + "\n")

        f.write("Total number of frequent itemsets: " + str(total_num_itemsets) + "\n")
        f.write("Number of high confidence rules: " + str(len(rules)) + "\n")

        #Checks if rules are generated at all
        if(highest_rule != None):
            lhs = " ".join(str(item) for item in highest_rule['LH'])
            rhs = " ".join(str(item) for item in highest_rule['RH'])
            sCount = highest_rule['Support Count']
            confidence = "{:.2f}".format(highest_rule['Confidence'])
            f.write("The rule with the highest confidence: " + lhs + '|' + rhs + '|' + str(sCount) + '|' + confidence + "\n")
        else:
            f.write("The rule with the highest confidence: " + "\n")
        f.write("Time in seconds to find the frequent itemsets: " + str(frequent_itemset_time) + "\n")
        f.write("Time in seconds to find the confident rules: " + str(candidate_rules_time))

#A user defined function that uses matplotlib to generate a bar graph that illustrates
#the relationship between frequent k-itemsets and their corresponding k value
def make_plot_items(frequent_k_items,output_file_name):
    fig, ax = plt.subplots()
    k_values = []
    for k in range(1,itemset_len + 1):
        k_values.append(k)
    num_itemsets = [len(frequent_items[k]) for k in k_values]

    itemset_graph = ax.bar(k_values, num_itemsets, label='Frequent Itemsets', color= 'tab:red')
    ax.bar_label(itemset_graph, fmt='%d')

    ax.set_xticks(k_values)
    ax.set_xticklabels(k_values, rotation=0, ha='right')
    ax.set_xlabel("Value of k")
    ax.set_ylabel("Number of Frequent k-Itemsets")
    ax.set_title("Frequent itemsets for each value of k")

    fig.savefig(output_file_name)

#A user defined function that uses matplotlib to generate a bar graph that illustrates
#the relationship between the number of high confidence and their corresponding k
#value
def make_plot_rules(rules, minconf, output_file_name):
    if min_conf == -1:
        return

    fig, ax = plt.subplots()

    k_rules = {}
    for rule in rules:
        k = len(rule['LH']) + len(rule['RH'])
        if k not in k_rules:
            k_rules[k] = []
        k_rules[k].append(rule)

    k_values = list(k_rules.keys())
    num_rules = [len(k_rules[k]) for k in k_values]

    rule_graph = ax.bar(k_values, num_rules, label='High Confidence Rules', color='tab:blue')
    ax.bar_label(rule_graph, fmt='%d')

    ax.set_xticks(k_values)
    ax.set_xticklabels(k_values, rotation=0, ha='right')
    ax.set_xlabel("Value of k")
    ax.set_ylabel("Number of High Confidence Rules")
    ax.set_title("High Confidence Rules for each value k")

    fig.savefig(output_file_name)

#Bar Graph for the amount of time required to find the frequent itemsets and candidate rules
def make_time_comaprison(frequent_itemset_time,candidate_rules_time):
    fig, ax = plt.subplots()

    processes = ['Frequent Itemsets Generation', 'Candidate Rules Generation']
    time_required = [frequent_itemset_time, candidate_rules_time]
    bar_colors = ['tab:red', 'tab:blue']

    time_graph = ax.bar(processes, time_required, label=processes, color=bar_colors)
    ax.bar_label(time_graph,fmt='%.4f')
    ax.set_ylabel('Time required (seconds)')
    ax.set_title('Graph displaying time required for each process')

    fig.savefig('time_comparison.png')

#Bar Graph for the number of frequent itemsets and candidate rules for every support
def make_itemset_rule_comaprison(itemset_count,rule_count):
    fig, ax = plt.subplots()

    processes = ['Frequent Itemsets', 'Candidate Rules']
    time_required = [itemset_count, rule_count]
    bar_colors = ['tab:red', 'tab:blue']

    time_graph = ax.bar(processes, time_required, label=processes, color=bar_colors)
    ax.bar_label(time_graph, fmt='%d')
    ax.set_ylabel('# of Items')
    ax.set_title('Graph displaying # for each process')

    fig.savefig('itemset_rule_comparison.png')



#Generating files
#make_items_file(frequent_items, out_file_name +"_items_10.txt")
#make_rules_file(rules, out_file_name + "_rules_10.txt")
#make_info_file(min_supp, min_conf, file_name,out_file_name, out_file_name + "_info_10.txt")
#make_plot_items(frequent_items, out_file_name + "_plot_items_10.png")
#make_plot_rules(rules,min_conf,out_file_name + "_plot_rules_10.png")

make_time_comaprison(frequent_itemset_time,candidate_rules_time)
make_itemset_rule_comaprison(total_num_itemsets,len(rules))
