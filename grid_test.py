import sys, os
from glob import glob
from pprint import pprint

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--complex", type=str, required=True, metavar="<path>",
                    help="Path to optimized complex coordinates")
parser.add_argument("--fragment1", type=str, required=True, metavar="<path>",
                    help="Path to optimized fragment1 coordinates")
parser.add_argument("--fragment2", type=str, required=True, metavar="<path>",
                    help="Path to optimized fragment2 coordinates")
parser.add_argument("--charge_complex", type=int, required=True, metavar="n",
                    help="Charge of complex")
parser.add_argument("--charge_f1", type=int, required=True, metavar="n",
                    help="Charge of fragment1")
parser.add_argument("--charge_f2", type=int, required=True, metavar="n",
                    help="Charge of fragment2")
parser.add_argument("--mult_complex", type=int, required=True, metavar="n",
                    help="Multiplicity of complex")
parser.add_argument("--mult_f1", type=int, required=True, metavar="n",
                    help="Multiplicity of fragment1")
parser.add_argument("--mult_f2", type=int, required=True, metavar="n",
                    help="Multiplicity of fragment2")
parser.add_argument("--grids", nargs="+", required=True,
                    help="Comma-separated list of the grids to use")
parser.add_argument("--keywords", nargs="+", required=True,
                    help="Comma-separated list of the keywords")
args = parser.parse_args()


class GridTest():
    def __init__(self, complex=args.complex, fragment1=args.fragment1, fragment2=args.fragment2,
                 charge_complex=args.charge_complex, charge_fragment1=args.charge_f1, charge_fragment2=args.charge_f2,
                 mult_complex=args.mult_complex, mult_fragment1=args.mult_f1, mult_fragment2=args.mult_f2,
                 keywords=args.keywords, grids=args.grids):
        """

        :param complex: path to XYZ file containing optimized coordinates
        :param fragment1: path to XYZ file containing optimized coordinates
        :param fragment2: path to XYZ file containing optimized coordinates
        :param charge_complex: charge of complex
        :param charge_fragment1: charge of fragment1
        :param charge_fragment2: charge of fragment2
        :param mult_complex: multiplicity of complex
        :param mult_fragment1: multiplicity of fragment1
        :param mult_fragment2: multiplicity of fragment 2
        :param keywords: list of keywords to define calculation
        :param grids: list of grids to use in testing
        """

        self.complex = complex
        self.fragment1 = fragment1
        self.fragment2 = fragment2
        self.charge_complex = charge_complex
        self.charge_fragment1 = charge_fragment1
        self.charge_fragment2 = charge_fragment2
        self.mult_complex = mult_complex
        self.mult_fragment1 = mult_fragment1
        self.mult_fragment2 = mult_fragment2
        self.root = os.getcwd()

        # Get the list arguments. Two possible ways of providing these, so
        # we must take both cases into account
        if "," in "".join(grids):
            self.grids = "".join(grids).split(",")
        else:
            self.grids = grids

        if "," in "".join(keywords):
            self.keywords = "".join(keywords).split(",")
        else:
            self.keywords = keywords


        # Some assertions
        assert self.complex.endswith(".xyz"), "File has to be an XYZ file"
        assert self.fragment1.endswith(".xyz"), "File has to be an XYZ file"
        assert self.fragment2.endswith(".xyz"), "File has to be an XYZ file"

        self.make_dirs()

    def make_dirs(self):
        """
        Make the directory structure for the tests. One dir for each grid to be tested.

             |__complex
             |
             |__fragment1
        gridn|
             |__fragment2
             |
             |__bsse

        :return:
        """
        for grid in self.grids:
            os.mkdir(os.path.join(self.root, grid))
            os.mkdir(os.path.join(self.root, grid, "complex"))
            os.mkdir(os.path.join(self.root, grid, "fragment1"))
            os.mkdir(os.path.join(self.root, grid, "fragment2"))


    def gen_conf(self):
        raise NotImplementedError

    def make_inputs(self):
        raise NotImplementedError

    def make_bsse_inputs(self):
        raise NotImplementedError


if __name__ == "__main__":
    GridTest()