from collections import defaultdict

double_moves = defaultdict(list)
double_moves['A'].extend('P' * 9)
double_moves['A'].extend('T' * 1)

double_moves[10].extend('R' * 10)

double_moves[9].extend('P' * 5)
double_moves[9].extend('R' * 1)
double_moves[9].extend('P' * 2)
double_moves[9].extend('R' * 2)

double_moves[8].extend('P' * 8)
double_moves[8].extend('T' * 2)

double_moves[7].extend('P' * 6)
double_moves[7].extend('T' * 4)

double_moves[6].extend('P' * 5)
double_moves[6].extend('T' * 5)

double_moves[5].extend('D' * 8)
double_moves[5].extend('T' * 2)

double_moves[4].extend('T' * 3)
double_moves[4].extend('P' * 2)
double_moves[4].extend('T' * 5)

double_moves[3].extend('P' * 6)
double_moves[3].extend('T' * 4)

double_moves[2].extend('P' * 6)
double_moves[2].extend('T' * 4)

ace_moves = defaultdict(list)
ace_moves[10].extend('R' * 10)
ace_moves[9].extend('R' * 10)
ace_moves[8].extend('R' * 10)

ace_moves[7].extend('R' * 1)
ace_moves[7].extend('D' * 4)
ace_moves[7].extend('R' * 2)
ace_moves[7].extend('T' * 3)

ace_moves[6].extend('T' * 1)
ace_moves[6].extend('D' * 4)
ace_moves[6].extend('T' * 5)

ace_moves[5].extend('T' * 2)
ace_moves[5].extend('D' * 3)
ace_moves[5].extend('T' * 5)

ace_moves[4].extend('T' * 2)
ace_moves[4].extend('D' * 3)
ace_moves[4].extend('T' * 5)

ace_moves[3].extend('T' * 3)
ace_moves[3].extend('D' * 2)
ace_moves[3].extend('T' * 5)

ace_moves[2].extend('T' * 3)
ace_moves[2].extend('D' * 2)
ace_moves[2].extend('T' * 5)

classic_moves = defaultdict(list)
classic_moves[21].extend('R' * 10)
classic_moves[20].extend('R' * 10)
classic_moves[19].extend('R' * 10)
classic_moves[18].extend('R' * 10)
classic_moves[17].extend('R' * 10)

classic_moves[16].extend('R' * 5)
classic_moves[16].extend('T' * 5)

classic_moves[15].extend('R' * 5)
classic_moves[15].extend('T' * 5)

classic_moves[14].extend('R' * 5)
classic_moves[14].extend('T' * 5)

classic_moves[13].extend('R' * 5)
classic_moves[13].extend('T' * 5)

classic_moves[12].extend('T' * 2)
classic_moves[12].extend('R' * 3)
classic_moves[12].extend('T' * 5)

classic_moves[11].extend('D' * 8)
classic_moves[11].extend('T' * 2)

classic_moves[10].extend('D' * 8)
classic_moves[10].extend('T' * 2)

classic_moves[9].extend('T' * 1)
classic_moves[9].extend('D' * 4)
classic_moves[9].extend('T' * 5)

classic_moves[8].extend('T' * 10)
classic_moves[7].extend('T' * 10)
classic_moves[6].extend('T' * 10)
classic_moves[5].extend('T' * 10)


def dictionaries(moves):
    return {
        player: {
            'A' if ind is 9 else ind + 2: move for ind, move in enumerate(c_cases)
        } for player, c_cases in moves.items()
    }


double_moves, ace_moves, classic_moves = map(dictionaries, [double_moves, ace_moves, classic_moves])
