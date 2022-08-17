import re
import pandas

def logcheker(phone=False):
    if not phone:
        with open('input.txt') as input:
            with open('buffer.txt', 'w') as buffer:
                txt = input.read(3)
                while txt != '':
                    if txt == '0A ':
                        txt = '0A\n'
                    buffer.write(txt)
                    txt = input.read(3)
        #форматирование файла в читаемый вид
        with open('buffer.txt') as input:
            with open('output.txt', 'w') as output:
                for (i, line) in enumerate(input, 1):
                    # Проверка на рано перенесенную строку и слитные написания
                    txt = spacer(line)
                    while len(txt) < 119:
                        buf = spacer(input.readline())
                        if buf == '':
                            break
                        txt = txt[:-1] + ' ' + buf
                    if not txt.endswith('0D 0A\n') or len(txt) > 120:
                        print(f'Error at line {i}: {txt}')
                    else:
                        output.write(txt)
    else:
        with open('input.txt') as input:
            with open('output.txt', 'w') as output:
                for (i, line) in enumerate(input, 1):
                    # Проверка на рано перенесенную строку и слитные написания
                    txt = spacer(line)
                    while len(txt) < 119:
                        buf = spacer(input.readline())
                        if buf == '':
                            break
                        txt = txt[:-1] + ' ' + buf
                    if not txt.endswith('0D 0A\n') or len(txt) > 120:
                        print(f'Error at output line {i}')
                    else:
                        output.write(txt)
    #Проверка на потерю пакетов
    data = pandas.read_csv('output.txt', delimiter=" ", skip_blank_lines=True, low_memory=False)
    data.columns = ['axH1', 'axL1', 'ayH1', 'ayL1', 'azH1', 'azL1', 'gxH1', 'gxL1', 'gyH1', 'gyL1', 'gzH1', 'gzL1',
                    'axH2', 'axL2', 'ayH2', 'ayL2', 'azH1', 'azL2', 'gxH2', 'gxL2', 'gyH2', 'gyL2', 'gzH2', 'gzL2',
                    'axH3', 'axL3', 'ayH3', 'ayL3', 'azH3', 'azL3', 'gxH3', 'gxL3', 'gyH3', 'gyL3', 'gzH3', 'gzL3',
                    'millisH', 'millisL', 'r', 'n']
    data['millisL'] = data['millisL'].apply(int, base=16)
    i = 0
    while i < data.index[-1]:
        a = data.iat[i, 37]
        b = data.iat[i + 1, 37]
        difference = b - a
        if 1 < difference < 255 or -255 < difference < 1:
            print(f'Missmatch at string {i} \r\n {a} and {b}')
        i += 1

def spacer(txt):
    result = re.search('\w{4}', txt)
    while result:
        txt = txt[:result.span()[0] + 2] + ' ' + txt[result.span()[0] + 2:]
        result = re.search('\w{4}', txt)
    return txt

if __name__ == '__main__':
    logcheker(phone=True)