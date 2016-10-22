# ParSeMiS Python Wrapper

This script is a wrapper for the frequent subgraph mining library ParSeMiS.

The original project can be found: https://www2.informatik.uni-erlangen.de/EN/research/zold/ParSeMiS/index.html

The source code for the java lib can be found: https://github.com/tomkdickinson/parsemis_wrapper

# Instructions

The script includes a class called Parsemis, which you can pass the same
parameters too if you were using ParSeMiS on the command line. The input
for the graph method are graphs built using NetworkX. 

# Requriements

* **NetworkX**

We use NetworkX due to it's large number of input formats that it can
read and write to.

See: http://networkx.readthedocs.io/en/networkx-1.11/reference/readwrite.html

# Example

An example of this wrapper in action can be found in example.py, with 
a sample dataset in example_dataset/.

The dataset was collected from IMDB and contains all classic episodes of
Doctor Who (every file is an episode), with the characters who appeared
 in that episode. 
 
Running the example will generate a list of the frequent subgraphs in the
dataset, including cooccuring characters.

The example is ran with CloseGraph to remove any subgraphs of a subgraph
that has the same frequency.
 
The top 20 results are below. As can be seen, the most frequent nodes 
are different aliases for Dr Who, followed by groups of companions of the Doctor.

| count  | Nodes\Edges |
|:------:|:------------|
|681 | ['episode']|
|297 | [('episode', 'Dr._Who')]|
|254 | [('episode', 'Doctor_Who')]|
|131 | [('episode', 'The_Doctor')]|
|83 | [('episode', 'Sarah_Jane_Smith')]|
|81 | [('Sarah_Jane_Smith', 'episode'), ('episode', 'Doctor_Who')]|
|78 | [('Jo_Grant', 'episode')]|
|77 | [('Ian_Chesterton', 'episode'), ('episode', 'Dr._Who')]|
|77 | [('episode', 'Brigadier_Lethbridge_Stewart')]|
|76 | [('Barbara_Wright', 'episode'), ('Ian_Chesterton', 'episode'), ('episode', 'Dr._Who')]|
|72 | [('Guard', 'episode')]|
|69 | [('episode', 'Romana')]|
|68 | [('episode', 'Jamie_McCrimmon')]|
|67 | [('episode', 'Romana'), ('episode', 'Doctor_Who')]|
|66 | [('episode', 'Dr._Who'), ('episode', 'Jamie_McCrimmon')]|
|65 | [('episode', 'Tegan')]|
|61 | [('episode', 'Tegan'), ('episode', 'The_Doctor')]|
|54 | [('episode', 'Doctor_Who'), ('episode', 'Brigadier_Lethbridge_Stewart')]|
|52 | [('Susan_Foreman', 'episode')]|
|51 | [('Barbara_Wright', 'episode'), ('Susan_Foreman', 'episode'), ('episode', 'Dr._Who'), ('episode', 'Ian_Chesterton')]|


