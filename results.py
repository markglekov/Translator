def main():
    X = 0
    Y = 0
    Z = 0
    X = 3
    Y = 4
    Z = 5
    hypoCheck(X, Y, Z)
    X = 10
    Y = 19
    calcHypo(X, Y)


def hypoCheck(X, Y, Z):
    pythagoreanTriple = ((X ** 2) + (Y ** 2))
    if (pythagoreanTriple == (Z ** 2)):
        print(True)
        print("This is a Pythagorean triple: ", X, Y, Z)
    else:
        print(False)
        print("This is not a Pythagorean triple: ", X, Y, Z)


def calcHypo(X, Y):
    hypo = (((X ** 2) + (Y ** 2)) ** 0.5)
    print('Hypotenuse of a right triangle with sides', X, 'and', Y, 'is', hypo)


print("Hello World!!!")
main()
