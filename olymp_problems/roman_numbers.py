def checkio(data):
    
    def thousand(data):
        print('DEBUG](thousand)data = ' + str(data))
        length = len(str(data))
        if length == 4:
            num = str(data)[0]
            debug_num = ('[DEBUG](thousand) = {0}').format(num)
            print(debug_num)
            done_row = 'M' * int(num)
            return done_row
    #print(thousand(3888))
            
    def hundred(data):
        print('[DEBUG](hundred)data = ' + str(data))
        length = len(str(data))
        if length == 4:
            num = str(data)[1]
        elif length == 3:
            num = str(data)[0]
            
        debug_num = ('[DEBUG](hundred) = {0}').format(num)
        print(debug_num)
        
        if int(num) == 4:
            done_row = 'C' + 'D'
            print('[DEBUG](hundred)(== 4) = ' + done_row)
        elif int(num) == 9:
            done_row = 'C' + 'M'
            print('[DEBUG](hundred)(== 9) = ' + done_row)
        elif int(num) >= 5 and not int(num) == 9:
            done_row = 'D' + 'C' * (int(num)-5)
            print('[DEBUG](hundred)(>= 5) = ' + done_row)
        else:
            done_row = 'C' * int(num)
            print('[DEBUG](hundred)(< 4) = ' + done_row)
        return done_row
    #print(hundred(499))
    
    def dozen(data):
        print('[DEBUG](dozen)data = ' + str(data))
        length = len(str(data))
        if length == 4:
            num = str(data)[2]
        elif length == 3:
            num = str(data)[1]
        elif length == 2:
            num = str(data)[0]
            
        debug_num = ('[DEBUG](dozen) = {0}').format(num)
        print(debug_num)
        
        if int(num) == 4:
            done_row = 'X' + 'L'
            print('[DEBUG](dozen)(== 4) = ' + done_row)
        elif int(num) == 9:
            done_row = 'X' + 'C'
            print('[DEBUG](dozen)(== 9) = ' + done_row)
        elif int(num) >= 5 and not int(num) == 9:
            done_row = 'L' + 'X' * (int(num)-5)
            print('[DEBUG](dozen)(< 9) = ' + done_row)
        else:
            done_row = 'X' * int(num)
            print('[DEBUG](dozen)(< 4) = ' + done_row)
        return done_row
    #print(dozen(76))
    
    def unit(data):
        print('[DEBUG](unit)data = ' + str(data))
        length = len(str(data))
        if length == 4:
            num = str(data)[3]
        elif length == 3:
            num = str(data)[2]
        elif length == 2:
            num = str(data)[1]
        elif length == 1:
            num = str(data)[0]
            
        debug_num = ('[DEBUG](unit) = {0}').format(num)
        print(debug_num)
        
        if int(num) == 4:
            done_row = 'I' + 'V'
            print('[DEBUG](unit)(== 4) = ' + done_row)
        elif int(num) == 9:
            done_row = 'I' + 'X'
            print('[DEBUG](unit)(== 9) = ' + done_row)
        elif int(num) >= 5 and not int(num) == 9:
            done_row = 'V' + 'I' * (int(num)-5)
            print('[DEBUG](unit)(>= 5) = ' + done_row)
        else:
            done_row = 'I' * int(num)
            print('[DEBUG](unit)(< 5) = ' + done_row)
        return done_row
    #print(unit(6))
    
    if len(str(data)) == 4:
        roman_num = thousand(data) + hundred(data) + dozen(data) + unit(data)
    if len(str(data)) == 3:
        roman_num = hundred(data) + dozen(data) + unit(data)
    if len(str(data)) == 2:
        roman_num = dozen(data) + unit(data)
    if len(str(data)) == 1:
        roman_num = unit(data)
    print('[DEBUG](roman_num) = ' + roman_num + '\n')
    return roman_num
    
if __name__ == '__main__':
    #These "asserts" using only for self-checking and not necessary for auto-testing
    assert checkio(6) == 'VI', '6'
    assert checkio(76) == 'LXXVI', '76'
    assert checkio(499) == 'CDXCIX', '499'
    assert checkio(3888) == 'MMMDCCCLXXXVIII', '3888'