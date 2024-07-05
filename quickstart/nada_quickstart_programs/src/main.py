from nada_dsl import *

def return_val_if_any_false(list_of_bool, val):
    final_value = UnsignedInteger(0)
    for bool in list_of_bool:
        final_value = bool.if_else(final_value, val)
    return final_value

def initialize_voters(nr_voters):
    voters = []
    for i in range(nr_voters):
        voters.append(Party(name="Voter" + str(i)))
    return voters

def inputs_initialization(nr_voters, nr_candidates, voters):
    votes_per_candidate = []
    for c in range(nr_candidates):
        votes_per_candidate.append([])
        for v in range(nr_voters):
            votes_per_candidate[c].append(
                SecretUnsignedInteger(
                    Input(name="v" + str(v) + "_c" + str(c), party=voters[v])
                )
            )
    return votes_per_candidate

def count_votes(nr_voters, nr_candidates, votes_per_candidate, outparty):
    votes = []
    for c in range(nr_candidates):
        result = votes_per_candidate[c][0]
        for v in range(1, nr_voters):
            result += votes_per_candidate[c][v]
        votes.append(Output(result, "final_vote_count_c" + str(c), outparty))
    return votes

def fn_check_sum(nr_voters, nr_candidates, votes_per_candidate, outparty):
    check_sum = []
    if_sum_cheat_open = []
    for v in range(nr_voters):
        check = votes_per_candidate[0][v]
        for c in range(1, nr_candidates):
            vote_v_c = votes_per_candidate[c][v]
            check += vote_v_c
        check_sum.append(Output(check, "check_sum_v" + str(v), outparty))
        comp_v_sum = check <= UnsignedInteger(nr_candidates)
        for c in range(nr_candidates):
            vote_v_c = votes_per_candidate[c][v]
            if_sum_cheat_open_v_c = comp_v_sum.if_else(UnsignedInteger(0), vote_v_c)
            if_sum_cheat_open.append(
                Output(
                    if_sum_cheat_open_v_c,
                    "if_sum_cheat_open_v" + str(v) + "_c" + str(c),
                    outparty,
                )
            )
    return check_sum, if_sum_cheat_open

def fn_check_prod(nr_voters, nr_candidates, votes_per_candidate, outparty):
    check_prod = []
    if_prod_cheat_open = []
    all_comp_prod = []
    for v in range(nr_voters):
        all_comp_v_prod = []
        for c in range(nr_candidates):
            vote_v_c = votes_per_candidate[c][v]
            check_v_c_product = (UnsignedInteger(1) - vote_v_c) * (UnsignedInteger(2) - vote_v_c)
            check_prod.append(
                Output(check_v_c_product, "check_prod_v" + str(v) + "_c" + str(c), outparty)
            )
            comp_v_c_prod = check_v_c_product < UnsignedInteger(1)
            all_comp_v_prod.append(comp_v_c_prod)
        all_comp_prod.append(all_comp_v_prod)
    for v in range(nr_voters):
        all_comp_v_prod = all_comp_prod[v]
        for c in range(nr_candidates):
            vote_v_c = votes_per_candidate[c][v]
            if_prod_cheat_open_v_c = return_val_if_any_false(all_comp_v_prod, vote_v_c)
            if_prod_cheat_open.append(
                Output(
                    if_prod_cheat_open_v_c,
                    "if_prod_cheat_open_v" + str(v) + "_c" + str(c),
                    outparty,
                )
            )
    return check_prod, if_prod_cheat_open

def nada_main():
    nr_voters = UnsignedInteger(3)  # Fixed for demonstration purposes
    nr_candidates = UnsignedInteger(2)  # Fixed for demonstration purposes
    voters = initialize_voters(nr_voters.value)
    outparty = Party(name="OutParty")
    votes_per_candidate = inputs_initialization(nr_voters.value, nr_candidates.value, voters)
    votes = count_votes(nr_voters.value, nr_candidates.value, votes_per_candidate, outparty)
    check_sum, if_sum_cheat_open = fn_check_sum(
        nr_voters.value, nr_candidates.value, votes_per_candidate, outparty
    )
    check_prod, if_prod_cheat_open = fn_check_prod(
        nr_voters.value, nr_candidates.value, votes_per_candidate, outparty
    )
    results = votes + check_sum + if_sum_cheat_open + check_prod + if_prod_cheat_open
    return results