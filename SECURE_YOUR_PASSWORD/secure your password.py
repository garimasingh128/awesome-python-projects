sym = {
          'a' : '!!',
          'b' : '@',
          'c' : '#',
          'd' : '$',
          'e' : '^',
          'f' : '}',
          'g' : ']',
          'h' : ')',
          'i' : '*',
          'j' : '=',
          'k' : '+',
          'l' : '-',
          'm' : '_',
          'n' : '>',
          'o' : '<',
          'p' : '.',
          'q' : '%',
          'r' : '&',
          's' : '(',
          't' : '{',
          'u' : '[',
          'x' : '?',
          'y' : ',',
          'z' : '|',
          }
inp = 'alphabet'
password = ''

for i in inp:
        for key, val in sym.items():
                if i in key:
                        password = password + val
print("Name you entered : ", inp)
print("Password : ", password)