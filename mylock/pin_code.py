import random
import numpy
from datetime import datetime


def formulegenerator(grootte):
    formule = []
    for i in range(grootte):
        col = []
        for j in range(4):
            col.append(random.randint(1, 999))
        formule.append(col)

    return formule

def element_product(left,right,rij_1,col_2):
    element = 0
    for i in range (len(left[0])):
        element += (left[rij_1][i])*right[i][col_2]
    return element

def product(left, right):
    """ Return the product of the given matrices.
    The product of two matrices is a matrix whose elements
    are equal to the product of the corresponding row of
    the leftmost matrix with the corresponding column of
    the rightmost matrix.
    """

    product=[[0 for i in range(len(right[0]))]for z in range(len(left))]

    for i in range(len(left)):
        for j in range (len(right[0])):
            product[i][j]=element_product(left,right,i,j)

    return product


def get_code():
    # haal persoongebonden formule op en genereer code
    personal_formula = formulegenerator(4)
    tijd = str(datetime.now())
    maand = int(tijd[5:7])
    dag = int(tijd[8:10])
    uur = int(tijd[11:13])
    minuut = int(tijd[14:16])
    tijdsmat = [[maand],[dag],[uur],[minuut]]

    # numpy matrix vermenigvuldiging tot code Ax=B met A = personal_formula, b = tijdsmat en B is de code
    B = product(personal_formula, tijdsmat)

    code = 0
    for i in range(len(B)):
        number = int(B[i][0])
        code += (number % 10) * (10 ** i)
    if code < 1000:
        code *= 10
    return code
