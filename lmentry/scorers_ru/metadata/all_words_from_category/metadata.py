def get_category_words(category_words):
    category_words18 = ', '.join([word for word in category_words])
    category_words17 = ', '.join(category_words[:-1]) + f' и {category_words[-1]}'
    category_words16 = ', '.join(category_words[:-1]) + f', и {category_words[-1]}'
    category_words15 = '(' + ', '.join([word for word in category_words]) + ')'
    category_words13 = '(' + ', '.join(category_words[:-1]) + f' и {category_words[-1]}' + ')'
    category_words11 = '(' + ', '.join(category_words[:-1]) + f', и {category_words[-1]}' + ')'
    category_words14 = '[' + ', '.join([word for word in category_words]) + ']'
    category_words12 = '[' + ', '.join(category_words[:-1]) + f' и {category_words[-1]}' + ']'
    category_words10 = '[' + ', '.join(category_words[:-1]) + f', и {category_words[-1]}' + ']'
    category_words9 = ', '.join([f'"{word}"' for word in category_words])
    category_words8 = ', '.join([f'"{word}"' for word in category_words[:-1]]) + f' и "{category_words[-1]}"'
    category_words7 = ', '.join([f'"{word}"' for word in category_words[:-1]]) + f', и "{category_words[-1]}"'
    category_words6 = '(' + ', '.join(
        [f'"{word}"' for word in category_words[:-1]]) + f' и "{category_words[-1]}"' + ')'
    category_words5 = '[' + ', '.join(
        [f'"{word}"' for word in category_words[:-1]]) + f' и "{category_words[-1]}"' + ']'
    category_words4 = '(' + ', '.join([f'"{word}"' for word in category_words]) + ')'
    category_words3 = '[' + ', '.join([f'"{word}"' for word in category_words]) + ']'
    category_words2 = '(' + ', '.join(
        [f'"{word}"' for word in category_words[:-1]]) + f', и "{category_words[-1]}"' + ')'
    category_words1 = '[' + ', '.join(
        [f'"{word}"' for word in category_words[:-1]]) + f', и "{category_words[-1]}"' + ']'

    return (rf'{category_words1}|{category_words2}|{category_words3}|{category_words4}|{category_words5}|'
                        rf'{category_words6}|{category_words7}|{category_words8}|{category_words9}|{category_words10}|'
                        rf'{category_words11}|{category_words12}|{category_words13}|{category_words14}|'
                        rf'{category_words15}|{category_words16}|{category_words17}|{category_words18}')
