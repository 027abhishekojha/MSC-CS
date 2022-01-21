import sys
import nfa_utils
import time

# print the intro text block
with open("intro.dat") as intro_file:
    print(intro_file.read())

# regular expression string to compare against provided input
regex = None
regex_nfa = None
# last line of user input read from the command line
line_read = ""

# continuously parse and process user input
while True:
    # read in line of user input
    line_read = input("> ")
    # make a lowercase copy of the input for case insensitive comparisons
    line_read_lower = line_read.lower()

    if line_read_lower == "exit":
        # exit the program
        print("\nExiting...")
        sys.exit()

    if line_read_lower.startswith("regex="):
        # user wants to set the regex to a string they've provided
        regex = line_read[6:]
        print("New regex pattern:", regex, "\n")
        start_time = time.time()
        # turn regular expression string into an NFA object
        regex_nfa = nfa_utils.get_regex_nfa(regex)
        regex_nfa.reset()
        finish_time = time.time()
        ms_taken = (finish_time - start_time) * 1000

        print("\nBuilt NFA in {:.3f} ms.\n".format(ms_taken))
        print(regex_nfa)
    else:
        # assume the user intends to test this entered string against the regex
        if regex_nfa is None:
            # regex has not yet been set
            print("Please supply a regular expression string first, with regex=(regex here)")
        else:
            start_time = time.time()
            # feed input string into NFA
            regex_nfa.feed_symbols(line_read, return_if_dies=True)
            accepts = regex_nfa.is_accepting()
            finish_time = time.time()
            ms_taken = (finish_time - start_time) * 1000

            print("String was {} by NFA"
                  .format("ACCEPTED" if accepts else "REJECTED"))

            print("Calculated in {:.3f} ms.".format(ms_taken))

            # print(regex_nfa)
            regex_nfa.reset()

    # print a new line for aesthetics
    print()
