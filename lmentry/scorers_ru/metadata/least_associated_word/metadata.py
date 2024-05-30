def get_words(words):
    words19 = ', '.join(words[:-1]) + f' или {words[-1]}'
    words18 = ', '.join([word for word in words])
    words17 = ', '.join(words[:-1]) + f' и {words[-1]}'
    words16 = ', '.join(words[:-1]) + f', и {words[-1]}'
    words15 = '(' + ', '.join([word for word in words]) + ')'
    words13 = '(' + ', '.join(words[:-1]) + f' и {words[-1]}' + ')'
    words11 = '(' + ', '.join(words[:-1]) + f', и {words[-1]}' + ')'
    words14 = '[' + ', '.join([word for word in words]) + ']'
    words12 = '[' + ', '.join(words[:-1]) + f' и {words[-1]}' + ']'
    words10 = '[' + ', '.join(words[:-1]) + f', и {words[-1]}' + ']'
    words9 = ', '.join([f'"{word}"' for word in words])
    words8 = ', '.join([f'"{word}"' for word in words[:-1]]) + f' и "{words[-1]}"'
    words7 = ', '.join([f'"{word}"' for word in words[:-1]]) + f', и "{words[-1]}"'
    words6 = '(' + ', '.join(
        [f'"{word}"' for word in words[:-1]]) + f' и "{words[-1]}"' + ')'
    words5 = '[' + ', '.join(
        [f'"{word}"' for word in words[:-1]]) + f' и "{words[-1]}"' + ']'
    words4 = '(' + ', '.join([f'"{word}"' for word in words]) + ')'
    words3 = '[' + ', '.join([f'"{word}"' for word in words]) + ']'
    words2 = '(' + ', '.join(
        [f'"{word}"' for word in words[:-1]]) + f', и "{words[-1]}"' + ')'
    words1 = '[' + ', '.join(
        [f'"{word}"' for word in words[:-1]]) + f', и "{words[-1]}"' + ']'

    words = (rf'({words1}|{words2}|{words3}|{words4}|{words5}|{words6}|{words7}|{words8}|{words9}|{words10}|'
             rf'{words11}|{words12}|{words13}|{words14}|{words15}|{words16}|{words17}|{words18}|{words19})')
    return words