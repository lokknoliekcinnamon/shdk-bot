def someones_distance(a, b):
    """"
    Calculates the Levenshtein distance between a and b.
    Taken from internet.
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current_column = range(n + 1)  # Keep current and previous column, not entire matrix
    for i in range(1, m + 1):
        previous_column, current_column = current_column, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_column[j] + 1, current_column[j - 1] + 1, previous_column[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_column[j] = min(add, delete, change)

    return current_column[n]


def calc_distance(fw, sw):
    """
    Calculates Damerau-Levenstein distance for two given strings.
    :param fw: first word, a word to be changed
    :param sw: second word, a desired result
    :return: Damerau-Levenstein distance
    """

    fw, sw = list(fw), list(sw)

    if len(fw) > len(sw):
        fw, sw = sw, fw

    def recursive_calc(fw, sw, distance=0, cnt=0):

        if len(sw) > len(fw):
            fw.extend([1] * (len(sw) - len(fw)))  # extending shorter word to a length of
                                                # a longer one to avoid index error
        if cnt == len(sw):
            return distance

        elif cnt == len(sw) - 1: # last letter
            if fw[cnt] == sw[cnt]: #  MATCH
                print(f'{fw[cnt]} == {sw[cnt]}')
                return recursive_calc(fw, sw, distance, cnt + 1)
            else: # REPLACE
                print(f'Replaced {fw[cnt]} with {sw[cnt]}')
                fw[cnt] = sw[cnt]
                print(''.join(str(i) for i in fw))
                return recursive_calc(fw, sw, distance+1, cnt+1)

        else:
            if fw[cnt] == sw[cnt]: #  MATCH
                print(f'{fw[cnt]} == {sw[cnt]}')
                return recursive_calc(fw,sw,distance,cnt+1)
            elif fw[cnt] == sw[cnt+1]:
                if fw[cnt+1] == sw[cnt]:  # TRANSPOSITION
                    print(f'Swapped {fw[cnt]} and {fw[cnt+1]}')
                    fw[cnt], fw[cnt+1] = fw[cnt+1], fw[cnt]
                    print(''.join(str(i) for i in fw))
                    return recursive_calc(fw,sw,distance+1,cnt+1)
                else: # INSERT
                    print(f'Inserted {sw[cnt]} before {fw[cnt]}')
                    fw.insert(cnt, sw[cnt])
                    print(''.join(str(i) for i in fw))
                    return recursive_calc(fw, sw, distance+1, cnt+1)
            elif fw[cnt+1] == sw[cnt]:
                print(f'Deleted {fw[cnt]}')
                del fw[cnt]
                print(''.join(str(i) for i in fw))
                return recursive_calc(fw, sw, distance+1, cnt+1)
            else: # REPLACE
                print(f'Replaced {fw[cnt]} with {sw[cnt]}')
                fw[cnt] = sw[cnt]
                print(''.join(str(i) for i in fw))
                return recursive_calc(fw, sw, distance+1, cnt+1)

    a = recursive_calc(fw, sw)
    print(a)
    return a







