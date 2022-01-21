#Program to Construct DFA using REGEX
# str = "CAABBAAB"
def DFA(str, N):
    # If n <= 1, then prNo
    if (N <= 1):
        print("No")
        return
    # To count the matched characters
    count = 0
    # Check if the first character is C
    if (str[0] == 'C'):
        count += 1
        # Traverse the rest of string
        for i in range(1, N):

            # If character is A or B,
            # increment count by 1
            if (str[i] == 'A' or str[i] == 'B'):
                count += 1
            else:
                break
    else:
        # If the first character
        # is not C, pr-1
        print("No")
        return
    # If all characters matches
    if (count == N):
        print("Yes")
    else:
        print("No")
# Driver Code
if __name__ == '__main__':
    str = "ACCBBCCA"
    N = len(str)
    DFA(str, N)
