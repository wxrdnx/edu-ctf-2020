from functools import reduce
import json
import string

class LFSR:
    def __init__(self, init, feedback):
        self.state = init
        self.feedback = feedback
    def getbit(self):
        nextbit = reduce(lambda x, y: x ^ y, [i & j for i, j in zip(self.state, self.feedback)])
        self.state = self.state[1:] + [nextbit]
        return nextbit

def corr(bits0, bits1):
    assert len(bits0) == len(bits1)
    return sum([(i == j) for i, j in zip(bits0, bits1)]) / len(bits0)

def brute_force3(output, bitlength):
    guesses = []
    for guess in range(1, (1 << bitlength + 1) - 1):
        init = [int(i) for i in f"{guess:016b}"]
        feedback = [int(i) for i in f'{52453:016b}']
        lfsr = LFSR(init, feedback)
        output_guess = [lfsr.getbit() for _ in range(100)]
        r = corr(output, output_guess)
        if r >= 0.75:
            guesses.append(guess)
    result = []
    for guess in guesses:
        guess_str = guess.to_bytes(2, 'big').decode('latin1')
        if guess_str[0] in string.printable and guess_str[1] in string.printable:
            result.append(guess)
    assert len(result) == 1
    return result[0]
        
def brute_force2(output, bitlength):
    guesses = []
    for guess in range(1, (1 << bitlength) - 1):
        init = [int(i) for i in f"{guess:016b}"]
        feedback = [int(i) for i in f'{40111:016b}']
        lfsr = LFSR(init, feedback)
        output_guess = [lfsr.getbit() for _ in range(100)]
        r = corr(output, output_guess)
        if r >= 0.75:
            guesses.append(guess)
    result = []
    for guess in guesses:
        guess_str = guess.to_bytes(2, 'big').decode('latin1')
        if guess_str[0] in string.printable and guess_str[1] in string.printable:
            result.append(guess)
    assert len(result) == 1
    return result[0]

def brute_force1(output, bitlength, init3):
    guesses = []
    for guess in range(1, (1 << bitlength) - 1):
        inits = [[int(i) for i in f'{guess:016b}'], [int(i) for i in f'{init3:016b}']]
        feedbacks = [[int(i) for i in f'{39989:016b}'], [int(i) for i in f'{52453:016b}']]
        lfsr1 = LFSR(inits[0], feedbacks[0])
        lfsr3 = LFSR(inits[1], feedbacks[1])
        output_guess = [lfsr1.getbit() ^ lfsr3.getbit() for _ in range(100)]
        r = corr(output, output_guess)
        if r >= 0.68:
            guesses.append(guess)
    result = []
    for guess in guesses:
        guess_str = guess.to_bytes(2, 'big').decode('latin1')
        if guess_str[0] in string.printable and guess_str[1] in string.printable:
            result.append(guess)
    assert len(result) == 1
    return result[0]
        

if __name__ == '__main__':
    with open('output.txt', 'r') as f:
        output = json.load(f)
    init3 = brute_force3(output, 16)
    init2 = brute_force2(output, 16)
    init1 = brute_force1(output, 16, init3)
    flag = b'FLAG{' + init1.to_bytes(2, 'big') + init2.to_bytes(2, 'big') + init3.to_bytes(2, 'big') + b'}'
    print(flag)
