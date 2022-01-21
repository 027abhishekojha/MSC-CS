import unittest
import nfa_utils


class TestNFA(unittest.TestCase):

    def test_single_symbol_nfa(self):
        print("Testing single symbol regex NFA")

        nfa = nfa_utils.get_single_symbol_regex("x")
        print(nfa)

        # test NFA state
        self.assertEqual(nfa.alphabet,{'x'})
        self.assertEqual(nfa.states, {0, 1})
        self.assertEqual(nfa.transition_function, {(0, 'x'): {1}})
        self.assertEqual(nfa.accept_states, {1})
        self.assertEqual(nfa.in_states, {0})

        # test NFA behaviour
        self.assertFalse(nfa.is_accepting())

        nfa.feed_symbol("x")
        self.assertEqual(nfa.in_states, {1})
        self.assertTrue(nfa.is_accepting())

        nfa.feed_symbol("x")
        self.assertFalse(nfa.is_accepting())
        self.assertEqual(nfa.in_states, set())
        self.assertTrue(nfa.is_dead())

    def test_nfa_concat(self):
        print("Testing concatenated NFA a.b")

        # recognizes "a.b"
        nfa = nfa_utils.get_concat(nfa_utils.get_single_symbol_regex("a"),
                                   nfa_utils.get_single_symbol_regex("b"))
        print(nfa)

        self.assertFalse(nfa.is_accepting())
        nfa.feed_symbol("a")
        self.assertFalse(nfa.is_accepting())
        nfa.feed_symbol("b")
        self.assertTrue(nfa.is_accepting())
        nfa.feed_symbol("a")
        self.assertFalse(nfa.is_accepting())

    def test_big_nfa_concat(self):
        print("Testing concatenated NFA a.b.c.c.b.a.G.G.G")

        concat_strings = ["abc", "cba", "GGG"]

        # construct a large NFA by creating 3 sub NFAs, and
        # concatenating them together
        nfa = None
        for str in concat_strings:
            # construct sub nfa
            sub_nfa = None
            for c in str:
                if sub_nfa is None:
                    sub_nfa = nfa_utils.get_single_symbol_regex(c)
                else:
                    sub_nfa = nfa_utils.get_concat(sub_nfa, nfa_utils.get_single_symbol_regex(c))

            # combine this sub NFA with the overall NFA
            if nfa is None:
                nfa = sub_nfa
            else:
                nfa = nfa_utils.get_concat(nfa, sub_nfa)

        print(nfa)

        # ensure the NFA does not accept until the entire input string has been fed in
        input_str = "".join(concat_strings)

        for symbol in input_str:
            self.assertFalse(nfa.is_accepting())
            nfa.feed_symbol(symbol)

        self.assertTrue(nfa.is_accepting())

    def test_empty_string(self):
        print("Testing empty string transitions")

        # construct an NFA equivalent to a|<empty string>
        nfa = nfa_utils.get_single_symbol_regex("a")
        nfa.add_state(2, True)
        nfa.add_transition(0, "", {2})
        nfa.reset()
        print(nfa)

        # NFA should accept straight away due to the empty string transition
        # from the initial state to an accept state
        self.assertTrue(nfa.is_accepting())
        # after feeding an 'a', the NFA should accept; state 2 is dead
        # but a transition from state 0 to 1 (accepts) should still work
        nfa.feed_symbol("a")
        self.assertTrue(nfa.is_accepting())
        # after feeding a final a, the NFA should be dead (no transitions available
        # for the current "active" states)
        nfa.feed_symbol("a")
        self.assertFalse(nfa.is_accepting())
        self.assertTrue(nfa.is_dead())

    def test_nfa_union(self):
        print("Testing NFA union a.b|c.d")

        # build NFA
        nfa = nfa_utils.get_union(
            nfa_utils.get_regex_nfa("a.b"),
            nfa_utils.get_regex_nfa("c.d")
        )

        nfa.reset()
        print(nfa)

        # test accepts a.b
        self.assertFalse(nfa.is_accepting())
        nfa.feed_symbol("a")
        self.assertFalse(nfa.is_accepting())
        nfa.feed_symbol("b")
        self.assertTrue(nfa.is_accepting())
        nfa.feed_symbol("c")
        self.assertFalse(nfa.is_accepting())

        # test accepts c.d
        nfa.reset()
        self.assertFalse(nfa.is_accepting())
        nfa.feed_symbol("c")
        self.assertFalse(nfa.is_accepting())
        nfa.feed_symbol("d")
        self.assertTrue(nfa.is_accepting())
        nfa.feed_symbol("e")
        self.assertFalse(nfa.is_accepting())

    def test_kleene_star(self):
        print("Testing kleene star NFA a*")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("a*")
        nfa.reset()
        print(nfa)

        # test if accepts empty string
        self.assertTrue(nfa.is_accepting())

        # test if accepts 1 or many a's
        for i in range(20):
            nfa.feed_symbol("a")
            self.assertTrue(nfa.is_accepting())

        # test if rejects other symbols
        nfa.feed_symbol("b")
        self.assertFalse(nfa.is_accepting())
        self.assertTrue(nfa.is_dead())

    def test_big_kleene_star(self):
        print("Testing big kleene star NFA a*b*c*")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("a*b*c*")
        nfa.reset()
        print(nfa)

        # test if accepts empty string (none of a, b, or c)
        self.assertTrue(nfa.is_accepting())

        # test if rejects other symbol
        nfa.feed_symbol("d")
        self.assertFalse(nfa.is_accepting())

        # test if accepts many a's, b's, and c's in order
        symbols = ["a", "b", "c"]

        # test different numbers of a's, b's, and c's
        for i in range(10):
            nfa.reset()
            # feed each symbol a number of times
            for symbol in symbols:
                for j in range(i + 1):
                    nfa.feed_symbol(symbol)
                    self.assertTrue(nfa.is_accepting())

        # test if rejects other symbol
        nfa.feed_symbol("d")
        self.assertFalse(nfa.is_accepting())

    def test_one_or_more_of(self):
        print("Testing \"one or more of\" operator a+")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("a+")
        nfa.reset()
        print(nfa)

        # test if rejects empty string
        self.assertFalse(nfa.is_accepting())

        # test if accepts 1 or many a's
        for i in range(20):
            nfa.feed_symbol("a")
            self.assertTrue(nfa.is_accepting())

        # test if rejects other symbols
        nfa.feed_symbol("b")
        self.assertFalse(nfa.is_accepting())
        self.assertTrue(nfa.is_dead())

    def zero_or_one_of(self):
        print("Testing \"zero or one of\" operator a?bcd")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("a?bcd")
        nfa.reset()
        print(nfa)

        # test rejects empty string
        self.assertFalse(nfa.is_accepting())

        # test accepts "bcd"
        nfa.feed_symbols("bcd")
        self.assertTrue(nfa.is_accepting())
        nfa.reset()

        # test also accepts "abcd"
        nfa.feed_symbol("abcd")
        self.assertTrue(nfa.is_accepting())
        nfa.reset()

        # test rejects "aabcd"
        nfa.feed_symbols("aabcd")
        self.assertFalse(nfa.is_accepting())
        nfa.reset()

        # test rejects "aaaaaaaaabcd"
        nfa.feed_symbols("aaaaaaaaabcd")
        self.assertFalse(nfa.is_accepting())
        nfa.reset()

    def test_nfa_equals(self):
        print("Testing NFA equals function")

        # test equal
        nfa_a = nfa_utils.get_regex_nfa("a.b|c")
        nfa_b = nfa_utils.get_regex_nfa("a.b|c")

        self.assertEqual(nfa_a, nfa_b)

        # test NOT equal
        nfa_a = nfa_utils.get_regex_nfa("a.b|c")
        nfa_b = nfa_utils.get_regex_nfa("a.b.c.d")

        self.assertNotEqual(nfa_a, nfa_b)

    def test_implicit_concatenation(self):
        print("Testing implicit NFA concatenation")

        nfa_a = nfa_utils.get_regex_nfa("a.b.c.d|c")
        nfa_b = nfa_utils.get_regex_nfa("abcd|c")

        self.assertEqual(nfa_a, nfa_b)

    def test_readme_example_1(self):
        print("Testing README example \"p.y.t.h.o.n or python\"")

        # test with and without implicit concatenation
        variations = ["python", "p.y.t.h.o.n"]

        for variation in variations:
            # build NFA
            nfa = nfa_utils.get_regex_nfa(variation)
            nfa.reset()
            print(nfa)

            # test rejects empty string
            self.assertFalse(nfa.is_accepting())

            # test accepts "python"
            nfa.feed_symbols("python")
            self.assertTrue(nfa.is_accepting())
            nfa.reset()

            # test rejects "java"
            nfa.feed_symbol("java")
            self.assertFalse(nfa.is_accepting())
            nfa.reset()

    def test_readme_example_2(self):
        print("Testing README example \"python|java|C#\"")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("python|java|C#")
        nfa.reset()
        print(nfa)

        # test rejects empty string
        self.assertFalse(nfa.is_accepting())

        accept_list = ["python", "java", "C#"]
        reject_list = ["perl", "C++", "Go"]

        # test accepts all in accept list
        for symbol_input in accept_list:
            nfa.feed_symbols(symbol_input)
            self.assertTrue(nfa.is_accepting())
            nfa.reset()

        # test reject all in reject list
        for symbol_input in reject_list:
            nfa.feed_symbols(symbol_input)
            self.assertFalse(nfa.is_accepting())
            nfa.reset()

    def test_readme_example_3(self):
        print("Testing README example \"o+k then or o*ok then\"")

        # test both + symbol and * symbol variations
        variations = ["o+k then", "o*ok then"]

        for variation in variations:
            # build NFA
            nfa = nfa_utils.get_regex_nfa(variation)
            nfa.reset()
            print(nfa)

            # test rejects empty string
            self.assertFalse(nfa.is_accepting())

            accept_list = ["ok then", "ooook then", "ooooooook then"]
            reject_list = ["k then", "okay", "oki-doki"]

            # test accepts all in accept list
            for symbol_input in accept_list:
                nfa.feed_symbols(symbol_input)
                self.assertTrue(nfa.is_accepting())
                nfa.reset()

            # test reject all in reject list
            for symbol_input in reject_list:
                nfa.feed_symbols(symbol_input)
                self.assertFalse(nfa.is_accepting())
                nfa.reset()

    def test_readme_example_4(self):
        print("Testing README example \"c?loud\"")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("c?loud")
        nfa.reset()
        print(nfa)

        # test rejects empty string
        self.assertFalse(nfa.is_accepting())

        accept_list = ["cloud", "loud"]
        reject_list = ["oud", "ccloud"]

        # test accepts all in accept list
        for symbol_input in accept_list:
            nfa.feed_symbols(symbol_input)
            self.assertTrue(nfa.is_accepting())
            nfa.reset()

        # test reject all in reject list
        for symbol_input in reject_list:
            nfa.feed_symbols(symbol_input)
            self.assertFalse(nfa.is_accepting())
            nfa.reset()

    def test_readme_example_5(self):
        print("Testing README example \"H?A?h?a?*!*|H?E?h?e?*!*\"")

        # build NFA
        nfa = nfa_utils.get_regex_nfa("H?A?h?a?*!*|H?E?h?e?*!*")
        nfa.reset()
        print(nfa)

        accept_list = ["Hah", "heh", "Haha", "AAAAAAAAAAHAHAHAHAHA!!", "eeeehehehehehe", "hhhaaaaaaaaaaaa", "HEHEEE!"]
        reject_list = ["Heaha", "Haha!h!", "!haha", "I don't get it"]

        # test accepts all in accept list
        for symbol_input in accept_list:
            nfa.feed_symbols(symbol_input)
            self.assertTrue(nfa.is_accepting())
            nfa.reset()

        # test reject all in reject list
        for symbol_input in reject_list:
            nfa.feed_symbols(symbol_input)
            self.assertFalse(nfa.is_accepting())
            nfa.reset()
